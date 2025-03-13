from typing import List
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document


class EmbeddingService:
    def __init__(self, persist_directory: str = './data/chroma_db'):
        self.embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            model_kwargs={'device': 'cpu'},
        )
        self.persist_directory = persist_directory
        self.vector_store = None

    def create_vector_store(self, documents: List[Document]) -> None:
        '''Create a vector store from a list of documents.'''
        if not documents:
            print('No documents provided to create vector store.')
            return

        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
        )

        print(
            f'Created vector store with {len(documents)} documents at {self.persist_directory}'
        )

    def load_vector_store(self) -> bool:
        '''Load an existing vector store.'''
        if not os.path.exists(self.persist_directory):
            print(f'Vector store not found at {self.persist_directory}')
            return False

        self.vector_store = Chroma(
            persist_directory=self.persist_directory, embedding_function=self.embeddings
        )
        print(f'Loaded vector store from {self.persist_directory}')
        return True

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        '''Retrieve the most relevant document chunks for a query.'''
        if not self.vector_store:
            if not self.load_vector_store():
                raise ValueError(
                    'Vector store not initialized. Run create_vector_store first.'
                )

        return self.vector_store.similarity_search(query, k=k)
