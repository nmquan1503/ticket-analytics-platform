from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings 
from app.config import settings
import requests
import re
import array

sql_llm = ChatOpenAI(
    model="Qwen3-32B",
    openai_api_key=settings.API_KEY,
    openai_api_base="https://mkp-api.fptcloud.com/v1",
    temperature=0.7,
    top_p=0.8,
    extra_body={"top_k": 40, "chat_template_kwargs": {"enable_thinking": False}}
)

llm = ChatOpenAI(
    model="gemma-3-27b-it",
    openai_api_key=settings.API_KEY,
    openai_api_base="https://mkp-api.fptcloud.com/v1",
    temperature=0.0,
)

embed_model = OpenAIEmbeddings(
    model="Vietnamese_Embedding",
    openai_api_key=settings.API_KEY,
    openai_api_base="https://mkp-api.fptcloud.com/v1",
)

def get_embedding(text):
    try:
        model = "Vietnamese_Embedding"
        endpoint_url = f"https://mkp-api.fptcloud.com/v1/embeddings"

        # Prepare the request headers
        headers = {
            "Authorization": f"Bearer {settings.API_KEY}", # Standard Bearer token authentication
            "Content-Type": "application/json",   # Specify JSON payload
        }

        # Prepare the request payload (body) in JSON format
        payload = {
            "input": [text],
            "model": model
        }
        # Make the POST request
        response = requests.post(endpoint_url, headers=headers, json=payload) # Use json=payload for auto-serialization
        response.raise_for_status()

        response_data = response.json()
        # formated response and print it
        # print(json.dumps(response_data, indent=2))
        
        embedding = response_data["data"][0]["embedding"]
        # print(f"Dimention length: {len(embedding)}")
        
        return array.array("f", embedding)
    except Exception as e:
        print(f"Embedding error: {e}")

def get_res(prompt):
    return llm.invoke(prompt).content.strip()

def get_sql_res(prompt):
    query = sql_llm.invoke(prompt).content.strip()
    if "<think>" in query:
        query = re.sub(r"<think>.*?</think>", "", query, flags=re.DOTALL).strip()
    query = re.sub(r'```sql\s*|\s*```', '', query)
    query = ' '.join(query.split())
    if "*/" in query:
        query = query.split("*/")[1]
    query = query.replace('\n', ' ')
    query = query.replace('**', ' ')
    return query.strip()


