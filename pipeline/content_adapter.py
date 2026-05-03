"""Adapts scraped content into custom pedagogical style."""
from typing import Optional
from bs4 import BeautifulSoup


DEFAULT_SYSTEM_PROMPT = """You are "Anti-Gravity" — a friendly Indian tutor who explains math to 12-year-olds.

RULES:
1. Use simple English. No jargon.
2. Use Indian examples: gully cricket, auto-rickshaw fares, school tiffins, bazaar shopping, IPL scores, chai stalls.
3. Break everything into short sections with clear headings.
4. Use bullet points, not walls of text.
5. For every concept, suggest a visual: diagram, flowchart, or illustration.
6. Keep it fun and relatable.
"""

DEFAULT_ADAPTER_PROMPT = """TOPIC: {topic}
RAW CONTENT FROM MATHISFUN:
{raw_content}

Produce:
- A catchy title
- A 2-sentence intro hook
- 3-5 sections with headings
- Bullet points in each section
- At least 2 Indian-context examples
- Visual suggestions for each section
- A quick-recap box at the end
"""


def strip_html(raw_html: str) -> str:
    """Remove scripts/styles and extract readable text."""
    soup = BeautifulSoup(raw_html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:2000])


def build_adapter_prompt(topic: str, raw_html: str, custom_system: Optional[str] = None, custom_user: Optional[str] = None) -> tuple:
    """Build system prompt + user prompt for content adaptation.
    Returns (system_prompt, user_prompt).
    """
    clean = strip_html(raw_html)
    system = custom_system or DEFAULT_SYSTEM_PROMPT
    user = (custom_user or DEFAULT_ADAPTER_PROMPT).format(topic=topic, raw_content=clean[:4000])
    return system, user
