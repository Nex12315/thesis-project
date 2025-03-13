import os
import requests
from typing import List
from dotenv import load_dotenv
from langchain.schema import Document

load_dotenv()


class LLMService:
    def __init__(self):
        # For simplicity, we'll use a basic API approach
        # In a real implementation, you would use the appropriate client for your LLM
        self.api_base = os.getenv('LLM_API_BASE', 'http://localhost:11434')
        self.api_key = os.getenv('LLM_API_KEY', '')
        self.model_name = os.getenv('LLM_MODEL_NAME', 'phi4')

    def generate_response(self, query: str, context_docs: List[Document]) -> str:
        '''Generate a response using the LLM with provided context.'''

        # Prepare context from documents
        context = '\n\n'.join([doc.page_content for doc in context_docs])

        # Create a prompt that includes the context
        prompt = f'''You are an AI assistant for the Arctic Valley business simulation project.
        You goal is to help students understand business concepts and navigate their task.
        Use only the information provided in the context to answer the question. 
        If the information needed to answer the question is not in the context, say
        "I don't have enough informatino to answer this question."
        
        Context:
        {context}

        Question: {query}

        Answer:'''

        # For this demonstration, I'll demonstrate how to call a local Ollama instance
        # In production, you'd adjust this to work with your chosen LLM API
        try:
            response = requests.post(
                f'{self.api_base}/api/generate',
                headers={'Content-Type': 'application/json'},
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.1, 'max_tokens': 1024},
                },
                timeout=60,
            )

            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                error = f'Error from LLM API: {response.status_code}, {response.text}'
                print(error)
                return f'I encountered an error while processing your question: {error}'

        except Exception as e:
            error = f'Exception when calling LLM API: {str(e)}'
            print(error)
            return f'I encountered an error while processing your question: {error}'

    def generate_phi4_response(self, query: str, context_docs: List[Document]) -> str:
        '''Alternative implementation for Microsoft's phi4 API.'''
        # This is a placeholder - you'd need to adapt this to the actual phi4 API
        # when you have access to it
        context = "\n\n".join([doc.page_content for doc in context_docs])

        prompt = f'''You are an AI assistant for the Arctic Valley business simulation project.
        You goal is to help students understand business concepts and navigate their task.
        Use only the information provided in the context to answer the question. 
        If the information needed to answer the question is not in the context, say
        "I don't have enough informatino to answer this question."

        Context:
        {context}

        Question: {query}

        Answer:'''

        # You would need to implement the actual API call to phi4 here
        # using Microsoft's SDK or REST API
        # For now, this is just a placeholder

        return (
            "This is a placeholder response. Implement the actual phi4 API integration."
        )
