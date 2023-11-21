import re
from src.llm import load_model, agent
from src.database import Knowledge
from data.source import URL
from src.data_processor import parse_html

from typing import List
from langchain.chains import (
    ConversationalRetrievalChain,
)
from langchain.docstore.document import Document

import chainlit as cl


def load_knowledge(urls=URL):
    chunks = []
    for url in urls:
        text = parse_html(url)
        text = re.sub("\{[^)]*\}", "", text)
        chunks.append(text)
    return chunks


def ask(agent, question, return_context=False):
    question = {'query': question}
    result = agent(question)
    answer = result['result']
    # TODO: do post-processing of result if necessary
    if return_context:
        context = result['source_documents']
        return answer, context
    return answer


# use a simple measure of unique words to evaluate if the model is generating gibberish
def eval_result(result):
    sent = result.split()
    return len(set(sent))/len(sent)


@cl.on_chat_start
async def on_chat_start():
    knowledge = Knowledge("VA question answering system")
    knowledge.build_index(data=load_knowledge(URL))

    msg = cl.Message(
        content=f"Processing `{knowledge.knowledge_name}`...", disable_human_feedback=True
    )
    await msg.send()

    vectorstore = knowledge.get_database()
    llm = load_model()
    chat_agent = agent(llm=llm, vectorstore=vectorstore)

    # Let the user know that the system is ready
    msg.content = f"Processing `{knowledge.knowledge_name}` done. You can now ask questions!"
    await msg.update()

    cl.user_session.set("chain", chat_agent)


@cl.on_message
async def main(message: cl.Message, return_source=False):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler()

    res = await cl.make_async(chain)(message.content, callbacks=[cb])
    answer = res['result']
    if eval_result(answer) < 0.5:
        answer = "Sorry, I don't get that. Can you be more specific?"

    if return_source:
        source_documents = res["source_documents"]  # type: List[Document]
        text_elements = []  # type: List[cl.Text]
        source_text = []

        if source_documents:
            for source_idx, source_doc in enumerate(source_documents):
                source_name = f"source_{source_idx}"
                # Create the text element referenced in the message
                text_elements.append(
                    cl.Text(content=source_doc.page_content, name=source_name)
                )
                source_text.append(source_doc.page_content)
            source_names = [text_el.name for text_el in text_elements]

            if source_names:
                answer += f"\nSources: {', '.join(source_names)}\nSource content: {'; '.join(source_text)}"
            else:
                answer += "\nNo sources found"

    await cl.Message(content=answer, elements=None).send()
