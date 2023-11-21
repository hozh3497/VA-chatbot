from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import MarkdownHeaderTextSplitter


class Knowledge:
    def __init__(self,
                 knowledge_name,
                 model_name='sentence-transformers/all-MiniLM-L6-v2',
                 device='cpu'):
        self.knowledge_name = knowledge_name
        self.model = model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name,
                                                model_kwargs={'device': device})
        self.vectorstore = None

    def build_index(self,
                    data,
                    split_headers=None,
                    chunk_size=500,
                    chunk_overlap=100
                    ):
        if not split_headers:
            split_headers = [
                ("<topic>", "topic"), ("<descriptor>", "context")
            ]

        headers_to_split_on = split_headers
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_header_splits = markdown_splitter.split_text("\n\n".join(data))
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        docs = text_splitter.split_documents(md_header_splits)

        self.vectorstore = FAISS.from_documents(docs, self.embeddings)

    def query(self, question, top_k=5):
        return self.vectorstore.similarity_search(question, k=top_k)

    def save_embeddings(self, path):
        self.vectorstore.save_local(path)

    def get_database(self):
        return self.vectorstore
