from langchain.llms import CTransformers
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain import PromptTemplate
from data.prompts import qa_template


def load_model(path='model/llama-2-7b-chat.ggmlv3.q4_0.bin',
               model_type='llama',
               max_new_tokens=256,
               temperature=0.1):
    llm = CTransformers(model=path,  # Location of downloaded GGML model
                        model_type=model_type,  # Model type Llama
                        config={'max_new_tokens': max_new_tokens,
                                'temperature': temperature})
    return llm


def set_qa_prompt(prompt=qa_template):
    prompt = PromptTemplate(template=prompt,
                            input_variables=['context', 'question'])
    return prompt


def agent(llm,
          vectorstore,
          top_k=3,
          qa_template_=qa_template
          ):
    qa_prompt = set_qa_prompt(prompt=qa_template_)
    dbqa = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=vectorstore.as_retriever(search_kwargs={'k': top_k}),
                                       return_source_documents=True,
                                       chain_type_kwargs={'prompt': qa_prompt})
    return dbqa
