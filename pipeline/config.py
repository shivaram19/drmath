"""Pipeline configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OBSCURA_BINARY = os.getenv(
    "OBSCURA_BINARY",
    "/home/shivaramgoud/tinkering/tinkering-with-claws/picocloth/shared/project/tools/linkedin-scraper/obscura-src/target/release/obscura",
)

# LLM Provider selection: "openai", "azure", or "grok"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "azure").lower()

# OpenAI (standard) settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# Azure OpenAI settings
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://test-1-voice.openai.azure.com")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_KEY_2 = os.getenv("AZURE_OPENAI_KEY_2", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")

# Grok / xAI settings
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-2-latest")
GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

IXL_BASE = "https://in.ixl.com/maths/class-vii"
MATHISFUN_BASE = "https://www.mathsisfun.com"
