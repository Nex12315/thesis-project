import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Body, BackgroundTasks

from app.document_loader import process_documents
from app.llm_service import LLMService
from app.embeddings import EmbeddingService

# Initialize the FastAPI app
app = FastAPI(title='Arctic Valley AI Advisor')

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # In production, specify the actual origins
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Initialize services
embedding_service = EmbeddingService()
llm_service = LLMService()


# Define request and response models
class QueryRequest(BaseModel):
    query: str
    max_context_docs: int = 4


class QueryResponse(BaseModel):
    answer: str
    sources: list = []


class IndexingRequest(BaseModel):
    documents_directory: str = './data/documents'


class IndexingResponse(BaseModel):
    status: str
    message: str


# Dependency to ensure vector store is loaded
def get_embedding_service():
    if not embedding_service.vector_store:
        if not embedding_service.load_vector_store():
            raise HTTPException(
                status_code=500,
                detail='Vector store not initialized. Run indexing first.',
            )
    return embedding_service


def index_documents_task(documents_directory: str):
    '''Task to process and index documents.'''
    try:
        documents = process_documents(documents_directory)
        embedding_service.create_vector_store(documents)
        print(f'Successfully indexed {len(documents)} document chunks')
    except Exception as e:
        print(f'Error in background indexing task: {e}')


# Routes
@app.post('/query', response_model=QueryResponse)
async def query(
    request: QueryRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    '''Process a query and return an answer based on the documents.'''
    try:
        # Get a relevant documents
        context_docs = embedding_service.similarity_search(
            request.query,
            k=request.max_context_docs,
        )

        # Generate response using LLM
        answer = llm_service.generate_response(request.query, context_docs)

        # Prepare source information
        sources = [
            {
                'title': os.path.basename(doc.metadata.get('source', 'Unknown')),
                'source': doc.metadata.get('source', 'Unknown'),
            }
            for doc in context_docs
        ]

        return {'answer': answer, 'sources': sources}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error processing query: {str(e)}')


@app.post('/index', response_model=IndexingResponse)
async def index_documents(
    background_tasks: BackgroundTasks,
    request: IndexingRequest = Body(...),
):
    '''Index documents from the specified directory.'''
    try:
        # Process documents and create vector store
        # Using background tasks to avoid timeout for large document collections
        background_tasks.add_task(
            index_documents_task,
            documents_directory=request.documents_directory,
        )

        return {
            'status': 'processing',
            'message': f'Indexing documents from {request.documents_directory} in the background.',
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f'Error indexing documents: {str(e)}'
        )


@app.get('/health')
async def health_check():
    '''Check if the service is running.'''
    return {'status': 'healthy'}


# Main function to run the app
if __name__ == '__main__':
    import uvicorn

    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)
