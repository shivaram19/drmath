"""LLM client supporting OpenAI, Azure OpenAI, and Grok (xAI)."""
from openai import OpenAI, AzureOpenAI

from pipeline.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_BASE_URL,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_KEY_2,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    GROK_API_KEY,
    GROK_MODEL,
    GROK_BASE_URL,
)


class LLMClient:
    def __init__(self):
        if LLM_PROVIDER == "azure":
            key = AZURE_OPENAI_KEY or AZURE_OPENAI_KEY_2
            if not key:
                raise RuntimeError("AZURE_OPENAI_KEY not set.")
            self.client = AzureOpenAI(
                api_key=key,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
            )
            self.model = AZURE_OPENAI_DEPLOYMENT
            print(f"[LLM] Using Azure OpenAI ({self.model}) @ {AZURE_OPENAI_ENDPOINT}")
        elif LLM_PROVIDER == "grok":
            if not GROK_API_KEY:
                raise RuntimeError("GROK_API_KEY not set.")
            self.client = OpenAI(api_key=GROK_API_KEY, base_url=GROK_BASE_URL)
            self.model = GROK_MODEL
            print(f"[LLM] Using Grok ({self.model})")
        else:
            if not OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY not set.")
            self.client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            self.model = OPENAI_MODEL
            print(f"[LLM] Using OpenAI ({self.model})")

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
