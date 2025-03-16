from typing import List
import os
import glob

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredExcelLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


def load_document(file_path: str) -> List[Document]:
    '''Load a document based on its file extension.'''
    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_extension in ['.docx', '.doc']:
            loader = Docx2txtLoader(file_path)
        elif file_extension in ['.txt', '.md']:
            loader = TextLoader(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            loader = UnstructuredExcelLoader(file_path)
        else:
            print(f'Unsupported file type: {file_extension} for file {file_path}')
            return []

        return loader.load()
    except Exception as e:
        print(f'Error loading {file_path}: {e}')
        return []


def load_documents(directory: str) -> List[Document]:
    '''Load all documents from a directory'''
    documents = []

    # Find all files with suppotred extensions in the directory
    file_pattern = os.path.join(directory, '**/*.*')
    file_paths = glob.glob(file_pattern, recursive=True)

    for file_path in file_paths:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls']:
            documents.extend(load_document(file_path))

    return documents


def split_documents(
    documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[Document]:
    '''Split documents into chunks.'''
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=['\n\n', '\n', ' ', ''],
    )

    return text_splitter.split_documents(documents)


def process_documents(directory: str) -> List[Document]:
    '''Load and process all documents in the directory'''
    documents = load_documents(directory)

    # Add source metadata if not present
    for doc in documents:
        if 'source' not in doc.metadata:
            doc.metadata['source'] = 'unknown'

    # Split documents into smaller chunks
    split_docs = split_documents(documents)

    print(f'Processed {len(documents)} documents into {len(split_docs)} chunks')
    return split_docs
