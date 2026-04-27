'''
llm.py

TODO write summary here
'''

# Importing Libraries
from openai import OpenAI
from config import (USE_OPENAI,
                    OPENAI_API_KEY,
                    OLLAMA_BASE_URL,
                    EMBEDDING_MODEL,
                    CHAT_MODEL,
                    OPENAI_EMBED_MODEL,
                    OPENAI_CHAT_MODEL)

# Build LLM pipelines
def _build_clients() -> tuple[OpenAI, OpenAI, str, str]:
    if USE_OPENAI and OPENAI_API_KEY:
        client = OpenAI(api_key=OPENAI_API_KEY)
        return client, client, OPENAI_EMBED_MODEL, OPENAI_CHAT_MODEL
    else:
        client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        return client, client, EMBEDDING_MODEL, CHAT_MODEL

_embed_client, _chat_client, _embed_model, _chat_model = _build_clients()

# Expose model names
active_embed_model = _embed_model
active_chat_model = _chat_model

# Return embedding vector for string of text
def embed(text:str) -> list[float]:
    resp = _embed_client.embeddings.create(input=text, model=_embed_model)
    return resp.data[0].embedding


# Send a single-turn chat request and return the model's reply.
def llm_chat(system_prompt: str, user_prompt: str) -> str:
    resp = _chat_client.chat.completions.create(model=_chat_model,
                                                messages=[{"role": "system", "content": system_prompt},
                                                          {"role": "user",   "content": user_prompt},],)
    return resp.choices[0].message.content.strip()
