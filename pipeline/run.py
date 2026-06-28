"""Main pipeline runner — now a thin compatibility wrapper around the use case.

The actual orchestration lives in `pipeline/use_cases.py` and depends only on the
ports in `pipeline/interfaces.py`. Concrete adapters are wired here so existing
callers (CLI, web UI, tests) keep working without changes.
"""
import argparse
import sys
from typing import Optional

from pipeline.config import OUTPUT_DIR, DATA_DIR
from pipeline.db import get_prompt  # legacy wrapper

# Re-export these names so existing tests can monkey-patch them.
from pipeline.scraper import fetch_ixl_topics, search_mathisfun_topic
from pipeline.llm_client import LLMClient
from db.database import SessionLocal

from pipeline.adapters import (
    IXLTopicSource,
    MathIsFunContentSource,
    OpenAILLMClient,
    FileSystemContentStore,
    SQLGenerationTracker,
)
from pipeline.use_cases import GenerateContentUseCase


def run_pipeline(topic: str, output_path: str, prompt_id: Optional[str] = None):
    """Generate adaptive content for *topic* and write the result to *output_path*."""
    topic_source = IXLTopicSource(fetch_topics=fetch_ixl_topics)
    content_source = MathIsFunContentSource(fetch_content=search_mathisfun_topic)
    llm = OpenAILLMClient(client=LLMClient())
    store = FileSystemContentStore(data_dir=DATA_DIR, output_dir=OUTPUT_DIR)
    tracker = SQLGenerationTracker(session_factory=SessionLocal)

    use_case = GenerateContentUseCase(
        topic_source=topic_source,
        content_source=content_source,
        llm=llm,
        content_store=store,
        generation_tracker=tracker,
        prompt_lookup=lambda pid: get_prompt(pid),
    )
    return use_case.execute(topic, output_path=output_path, prompt_id=prompt_id)


def strip_html(raw_html: str) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw_html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:2000])


def main():
    parser = argparse.ArgumentParser(description="Dr. Math Content Automation Pipeline")
    parser.add_argument("--topic", default="Integers", help="Math topic to process")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    parser.add_argument("--prompt-id", default=None, help="Custom prompt ID to use")
    args = parser.parse_args()

    topic = args.topic
    output = args.output or str(OUTPUT_DIR / f"{topic.lower().replace(' ', '_')}_output.json")

    try:
        run_pipeline(topic, output, prompt_id=args.prompt_id)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
