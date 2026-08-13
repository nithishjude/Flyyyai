"""
Known AI Signals — the ground-truth reference data for the scanner.

This module contains:
  - AI_LIBRARIES: mapping of library name → (provider, asset_type, purpose_hint)
  - MODEL_NAME_PATTERNS: compiled regex patterns to detect model name strings
  - ENV_KEY_PATTERNS: compiled regex patterns for provider API key env vars
  - PROVIDER_ENDPOINTS: known AI provider API hostnames
  - MANIFEST_AI_PACKAGES: flat set of known AI packages (for requirements.txt / package.json)
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LibrarySignal:
    provider: str
    asset_type: str        # "Model Integration" | "AI Application" | "AI Agent"
    purpose_hint: str      # Short human-readable purpose description
    model_family: Optional[str] = None  # e.g. "GPT", "Claude", "Llama"


# ---------------------------------------------------------------------------
# Python/JS import → provider mapping
# ---------------------------------------------------------------------------
AI_LIBRARIES: dict[str, LibrarySignal] = {
    # OpenAI
    "openai": LibrarySignal(
        provider="OpenAI",
        asset_type="Model Integration",
        purpose_hint="OpenAI API integration (GPT / embeddings / DALL-E)",
        model_family="GPT",
    ),
    # Anthropic
    "anthropic": LibrarySignal(
        provider="Anthropic",
        asset_type="Model Integration",
        purpose_hint="Anthropic API integration (Claude models)",
        model_family="Claude",
    ),
    # LangChain ecosystem
    "langchain": LibrarySignal(
        provider="LangChain",
        asset_type="AI Application",
        purpose_hint="LangChain orchestration framework",
    ),
    "langchain_openai": LibrarySignal(
        provider="OpenAI via LangChain",
        asset_type="AI Application",
        purpose_hint="LangChain + OpenAI integration",
        model_family="GPT",
    ),
    "langchain_anthropic": LibrarySignal(
        provider="Anthropic via LangChain",
        asset_type="AI Application",
        purpose_hint="LangChain + Anthropic integration",
        model_family="Claude",
    ),
    "langchain_community": LibrarySignal(
        provider="LangChain",
        asset_type="AI Application",
        purpose_hint="LangChain community integrations",
    ),
    # LangGraph
    "langgraph": LibrarySignal(
        provider="LangChain",
        asset_type="AI Agent",
        purpose_hint="LangGraph stateful agent/workflow",
    ),
    # Sentence Transformers
    "sentence_transformers": LibrarySignal(
        provider="Hugging Face",
        asset_type="Model Integration",
        purpose_hint="Sentence-transformers embedding model (semantic search / similarity)",
        model_family="sentence-transformers",
    ),
    # Hugging Face Transformers
    "transformers": LibrarySignal(
        provider="Hugging Face",
        asset_type="Model Integration",
        purpose_hint="Hugging Face Transformers (LLM / classifier / embeddings)",
    ),
    # Google Generative AI
    "google.generativeai": LibrarySignal(
        provider="Google",
        asset_type="Model Integration",
        purpose_hint="Google Generative AI API (Gemini)",
        model_family="Gemini",
    ),
    "google_generativeai": LibrarySignal(
        provider="Google",
        asset_type="Model Integration",
        purpose_hint="Google Generative AI API (Gemini)",
        model_family="Gemini",
    ),
    # Cohere
    "cohere": LibrarySignal(
        provider="Cohere",
        asset_type="Model Integration",
        purpose_hint="Cohere API integration (Command / embeddings)",
        model_family="Command",
    ),
    # Mistral
    "mistralai": LibrarySignal(
        provider="Mistral AI",
        asset_type="Model Integration",
        purpose_hint="Mistral AI API integration",
        model_family="Mistral",
    ),
    # Together AI
    "together": LibrarySignal(
        provider="Together AI",
        asset_type="Model Integration",
        purpose_hint="Together AI API integration (open-source model hosting)",
    ),
    # Groq
    "groq": LibrarySignal(
        provider="Groq",
        asset_type="Model Integration",
        purpose_hint="Groq API integration (fast LLM inference)",
    ),
    # Ollama
    "ollama": LibrarySignal(
        provider="Ollama (self-hosted)",
        asset_type="Model Integration",
        purpose_hint="Ollama local model serving",
    ),
    # AWS Bedrock
    "boto3": LibrarySignal(
        provider="AWS",
        asset_type="Model Integration",
        purpose_hint="AWS SDK — may include Bedrock AI model calls",
    ),
    # Tiktoken (strongly implies OpenAI usage)
    "tiktoken": LibrarySignal(
        provider="OpenAI",
        asset_type="Model Integration",
        purpose_hint="OpenAI token counter — implies GPT model usage",
        model_family="GPT",
    ),
    # FAISS — vector store, implies embedding model
    "faiss": LibrarySignal(
        provider="Meta (self-hosted)",
        asset_type="Model Integration",
        purpose_hint="FAISS vector store — used with an embedding model for similarity search",
    ),
    # ChromaDB
    "chromadb": LibrarySignal(
        provider="Chroma",
        asset_type="Model Integration",
        purpose_hint="ChromaDB vector store — used with an embedding model",
    ),
    # Pinecone
    "pinecone": LibrarySignal(
        provider="Pinecone",
        asset_type="Model Integration",
        purpose_hint="Pinecone managed vector database",
    ),
    # Weaviate
    "weaviate": LibrarySignal(
        provider="Weaviate",
        asset_type="Model Integration",
        purpose_hint="Weaviate vector database",
    ),
}

# Normalised names (underscores/hyphens interchangeable in Python)
AI_LIBRARIES["sentence-transformers"] = AI_LIBRARIES["sentence_transformers"]
AI_LIBRARIES["google-generativeai"] = AI_LIBRARIES["google_generativeai"]

# ---------------------------------------------------------------------------
# Model name string patterns
# ---------------------------------------------------------------------------
_RAW_MODEL_PATTERNS = [
    # OpenAI GPT
    r"\bgpt-4[o\-]?[\w\-.]*\b",
    r"\bgpt-3\.5[\w\-.]*\b",
    r"\bgpt-4[\w\-.]*\b",
    r"\bo1[\w\-.]*\b",
    r"\btext-davinci[\w\-.]*\b",
    # OpenAI Embeddings
    r"\btext-embedding-[\w\-.]+\b",
    r"\btext-search-[\w\-.]+\b",
    # OpenAI DALL-E / Whisper / TTS
    r"\bdall-e[\w\-.]*\b",
    r"\bwhisper[\w\-.]*\b",
    r"\btts-[\w\-.]+\b",
    # Anthropic Claude
    r"\bclaude-[\w\-.]+\b",
    r"\bclaude[\d]+[\w\-.]*\b",
    # Google Gemini
    r"\bgemini-[\w\-.]+\b",
    r"\bgemini[\w\-.]*\b",
    r"\bpalm[\w\-.]*\b",
    # Meta Llama
    r"\bllama[\d]*[\w\-.]*\b",
    r"\bllama-[\w\-.]+\b",
    # Mistral
    r"\bmistral[\w\-.]*\b",
    r"\bmistral-[\w\-.]+\b",
    r"\bmixtra[\w\-.]*\b",
    # Cohere
    r"\bcommand[\w\-.]*\b",
    r"\bembed-[\w\-.]+\b",
    # Sentence Transformers
    r"\ball-MiniLM[\w\-.]*\b",
    r"\bparaphrase-[\w\-.]+\b",
    r"\bmulti-qa[\w\-.]+\b",
    r"\bmsmarco[\w\-.]+\b",
    # Hugging Face generic
    r"\bbert-[\w\-.]+\b",
    r"\broberta[\w\-.]*\b",
    r"\bt5[\w\-.]*\b",
    r"\bdistilbert[\w\-.]*\b",
    # AWS Bedrock model IDs
    r"\bamazon\.titan[\w\-.]*\b",
    r"\banthropic\.claude[\w\-.]*\b",
    r"\bmeta\.llama[\w\-.]*\b",
]

MODEL_NAME_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE) for p in _RAW_MODEL_PATTERNS
]

# ---------------------------------------------------------------------------
# Environment variable key patterns
# ---------------------------------------------------------------------------
_RAW_ENV_KEY_PATTERNS = [
    r"\bOPENAI_API_KEY\b",
    r"\bANTHROPIC_API_KEY\b",
    r"\bANTHROPIC_KEY\b",
    r"\bHUGGINGFACE_API_KEY\b",
    r"\bHUGGINGFACE_TOKEN\b",
    r"\bHF_TOKEN\b",
    r"\bHF_API_TOKEN\b",
    r"\bCOHERE_API_KEY\b",
    r"\bGOOGLE_API_KEY\b",
    r"\bGEMINI_API_KEY\b",
    r"\bMISTRAL_API_KEY\b",
    r"\bAZURE_OPENAI_API_KEY\b",
    r"\bAZURE_OPENAI_KEY\b",
    r"\bAZURE_OPENAI_ENDPOINT\b",
    r"\bTOGETHER_API_KEY\b",
    r"\bGROQ_API_KEY\b",
    r"\bPINECONE_API_KEY\b",
    r"\bWEAVIATE_API_KEY\b",
    r"\bBEDROCK_API_KEY\b",
]

ENV_KEY_PATTERNS: list[re.Pattern] = [
    re.compile(p) for p in _RAW_ENV_KEY_PATTERNS
]

# ---------------------------------------------------------------------------
# Known provider API endpoints
# ---------------------------------------------------------------------------
PROVIDER_ENDPOINTS: dict[str, str] = {
    "api.openai.com": "OpenAI",
    "api.anthropic.com": "Anthropic",
    "generativelanguage.googleapis.com": "Google",
    "api.cohere.com": "Cohere",
    "api.cohere.ai": "Cohere",
    "api.mistral.ai": "Mistral AI",
    "api.together.xyz": "Together AI",
    "api.groq.com": "Groq",
    "api-inference.huggingface.co": "Hugging Face",
    "huggingface.co": "Hugging Face",
    "bedrock.us-east-1.amazonaws.com": "AWS Bedrock",
    "openai.azure.com": "Azure OpenAI",
    "cognitive.microsoft.com": "Azure OpenAI",
}

# ---------------------------------------------------------------------------
# Flat package name set for manifest scanning
# ---------------------------------------------------------------------------
MANIFEST_AI_PACKAGES: set[str] = {
    # Python
    "openai", "anthropic", "langchain", "langchain-openai", "langchain-anthropic",
    "langchain-community", "langchain-core", "langgraph", "sentence-transformers",
    "transformers", "google-generativeai", "cohere", "mistralai", "together",
    "groq", "ollama", "tiktoken", "faiss-cpu", "faiss-gpu", "chromadb",
    "pinecone-client", "pinecone", "weaviate-client", "llama-index",
    "llama-index-core", "llama_index", "haystack-ai", "instructor", "guidance",
    "outlines", "dspy-ai", "autogen-agentchat", "crewai", "phidata",
    "boto3",  # included because Bedrock is commonly accessed via boto3
    "azure-ai-openai", "azure-cognitiveservices-language-luis",
    # JS/TS (npm package names)
    "openai",
    "@anthropic-ai/sdk",
    "@google/generative-ai",
    "langchain",
    "@langchain/openai",
    "@langchain/anthropic",
    "@langchain/community",
    "cohere-ai",
    "@mistralai/mistralai",
    "groq-sdk",
    "@pinecone-database/pinecone",
    "chromadb",
    "weaviate-ts-client",
    "ai",           # Vercel AI SDK
    "@ai-sdk/openai",
    "@ai-sdk/anthropic",
    "llamaindex",
}
