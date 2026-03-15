import os
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./representment.db")

MERCHANT_NAME = "Acme Electronics"
