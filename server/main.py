import json
import os
from typing import AsyncGenerator
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Body, BackgroundTasks
from starlette.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool

from server.document_loader import process_documents
from server.llm_service import LLMService
from server.embeddings import EmbeddingService

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

        return {'answer': answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error processing query: {str(e)}')


@app.post('/query-stream')
async def query_stream(
    request: QueryRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    '''Process a query and return a streaming response.'''
    try:
        # Get relevant documents
        context_docs = embedding_service.similarity_search(
            request.query,
            k=request.max_context_docs,
        )

        # Create a streaming response generator
        async def stream_generator() -> AsyncGenerator[str, None]:
            # Stream the actual response
            full_response = ""
            try:
                for line in llm_service.generate_streaming_response(
                    request.query, context_docs
                ):
                    if line:
                        try:
                            # Parse the line as JSON if it's from Ollama
                            line_data = json.loads(line)
                            if "response" in line_data:
                                chunk = line_data["response"]
                                full_response += chunk
                                # Send the chunk as a JSON event
                                yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"
                        except json.JSONDecodeError:
                            # If it's not valid JSON, just send the raw line
                            chunk = (
                                line.decode('utf-8')
                                if isinstance(line, bytes)
                                else line
                            )
                            full_response += chunk
                            yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"

                # Send a completion event
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as e:
                error_msg = f"Error during streaming: {str(e)}"
                print(error_msg)
                yield f"data: {json.dumps({'type': 'error', 'data': error_msg})}\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

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


@app.on_event("startup")
async def startup_event():
    """Initialize the vector store on server startup."""
    print("Checking if vector store exists...")

    # Check if vector store already exists
    vector_store_exists = embedding_service.load_vector_store()

    if not vector_store_exists:
        print("Vector store not found. Starting document indexing...")
        documents_directory = os.getenv("DOCUMENTS_DIR", "./data/documents")

        # Ensure documents directory exists
        if not os.path.exists(documents_directory):
            os.makedirs(documents_directory, exist_ok=True)
            print(f"Created documents directory at {documents_directory}")

        # Check if there are documents to index
        if any(os.scandir(documents_directory)):
            try:
                # Use threadpool to avoid blocking startup
                await run_in_threadpool(index_documents_task, documents_directory)
                print("Initial document indexing completed")
            except Exception as e:
                print(f"Error during initial indexing: {e}")
        else:
            print(
                f"No documents found in {documents_directory}. Add documents and use /index endpoint to index them."
            )
    else:
        print("Vector store loaded successfully")


@app.get('/health')
async def health_check():
    '''Check if the service is running.'''
    return {'status': 'healthy'}
