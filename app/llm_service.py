import os
import requests

from typing import List
from langchain.schema import Document


class LLMService:
    def __init__(self):
        self.api_base = 'http://localhost:11434'
        self.model_name = 'phi4'

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
