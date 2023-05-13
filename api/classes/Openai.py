
import openai
from openai.embeddings_utils import get_embedding
from openai.embeddings_utils import cosine_similarity

import nltk

class Openai():
    
    ENGINE_MODEL = ''
    ENGINE_MODEL_EMBEDDING = ''
    
    def __init__(self, 
                 api_type = "azure", 
                 api_key = "9cae1236e81e43138b8895ead77acb12", 
                 api_base = "https://openaipasionaus.openai.azure.com/", 
                 api_version = "2022-12-01", 
                 engine_model = "textDavinci03Model", 
                 engine_model_embedding = "text-embedding-ada-002"):
        
        global ENGINE_MODEL
        global ENGINE_MODEL_EMBEDDING
        
        openai.api_type = api_type
        openai.api_key = api_key
        openai.api_base = api_base
        openai.api_version = api_version
        
        ENGINE_MODEL = engine_model
        ENGINE_MODEL_EMBEDDING = engine_model_embedding
        

    def get_embedding(self, txt, engineEmbedding = None):
        if engineEmbedding is None: 
            engineEmbedding = ENGINE_MODEL_EMBEDDING
        
        return get_embedding(txt, engineEmbedding)
    
    def cosine_similarity(self, _a, _b):
        return cosine_similarity(_a, _b)
    
    def completion(self, prompt, engine = None, temperature = 0.1, max_tokens = 1024):
        
        if engine is None:
            engine = ENGINE_MODEL
                
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
        return response['choices'][0]['text'].strip("\n")
    
    def word_tokenize(self, text):
        return nltk.word_tokenize(text)