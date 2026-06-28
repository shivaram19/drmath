"""Pipeline use case orchestrating content generation behind a stable API.

`GenerateContentUseCase` depends only on the ports defined in
`pipeline/interfaces.py`. The legacy `run_pipeline()` function in
`pipeline/run.py` is a thin compatibility wrapper that wires concrete adapters
into this use case.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pipeline import interfaces as pi


class GenerateContentUseCase:
    """Generate adaptive math content for a topic and persist the result."""

    def __init__(
        self,
        topic_source: pi.TopicSource,
        content_source: pi.PedagogicalContentSource,
        llm: pi.LLMPort,
        content_store: pi.ContentStore,
        generation_tracker: pi.GenerationTracker,
        prompt_lookup: Optional[pi.PromptLookup] = None,
    ):
        self.topic_source = topic_source
        self.content_source = content_source
        self.llm = llm
        self.content_store = content_store
        self.generation_tracker = generation_tracker
        self.prompt_lookup = prompt_lookup

    def execute(
        self, topic: str, output_path: Optional[str] = None, prompt_id: Optional[str] = None
    ) -> Dict[str, Any]:
        print(f"\n🚀 Dr. Math Pipeline — Topic: {topic}\n")

        slug = topic.lower().replace(" ", "_")
        custom = self._load_prompt(prompt_id)
        prompt_name = custom["name"] if custom else "Default (Anti-Gravity)"
        print(f"🎨 Using prompt style: {prompt_name}\n")

        generation_id = self.generation_tracker.start(topic, slug, prompt_id)

        try:
            # Step 1: Match curriculum topics
            print("[1/5] Fetching IXL topic list via Obscura...")
            ixl_topics = self.topic_source.fetch_topics()
            matched = [t for t, _ in ixl_topics if topic.lower() in t.lower()]
            if matched:
                print(f"  ✅ Found {len(matched)} matching skills on IXL")
            else:
                print(f"  ⚠️  Topic not found in IXL. Proceeding anyway.")
            scraped_at = datetime.utcnow()

            # Step 2: Fetch reference content
            print("[2/5] Fetching MathIsFun content via Obscura...")
            scraped = self.content_source.fetch_content(topic)
            print(f"  ✅ Fetched {len(scraped.raw_html)} chars of raw HTML")

            raw_html_path = self.content_store.save_raw_html(slug, scraped.raw_html)
            print(f"  💾 Saved raw HTML to {raw_html_path}")

            # Step 3: Adapt content
            print("[3/5] Adapting content via LLM...")
            adapted = self.llm.adapt_content(
                topic,
                scraped.raw_html,
                custom_system=custom.get("system_prompt") if custom else None,
                custom_user=custom.get("system_prompt") if custom else None,
            )
            adapted_content = adapted.text
            print(f"  ✅ Generated {len(adapted_content)} chars of adapted content")

            antigravity_path = self.content_store.save_adapted_content(slug, adapted_content)
            print(f"  💾 Saved adapted content to {antigravity_path}")

            # Step 4: Generate questions
            print("[4/5] Generating 40 structured questions via LLM...")
            question_set = self.llm.generate_questions(
                topic,
                adapted_content,
                custom_question_prompt=custom.get("question_prompt") if custom else None,
                count=40,
            )
            questions = question_set.questions
            diff_counts = question_set.difficulty_distribution
            print(f"  ✅ Parsed {len(questions)} questions")
            print(f"  📊 Difficulty distribution: {diff_counts}")

            # Step 5: Assemble and persist output
            print("[5/5] Saving output...")
            output = {
                "topic": topic,
                "prompt_id": prompt_id,
                "prompt_name": prompt_name,
                "source_ixl_skills": matched[:10],
                "antigravity_content": adapted_content,
                "questions": questions,
                "meta": {
                    "total_questions": len(questions),
                    "difficulty_distribution": diff_counts,
                },
            }

            saved_at = datetime.utcnow()
            final_output_path = self.content_store.save_output(slug, output, output_path)

            result = pi.PipelineResult(
                topic=topic,
                prompt_id=prompt_id,
                prompt_name=prompt_name,
                source_ixl_skills=matched[:10],
                mathisfun_url=scraped.source_url,
                raw_html=scraped.raw_html,
                antigravity_content=adapted_content,
                questions=questions,
                difficulty_distribution=diff_counts,
                output_path=final_output_path,
                raw_html_path=raw_html_path,
                antigravity_path=antigravity_path,
                scraped_at=scraped_at,
                adapted_at=adapted.generated_at,
                questions_generated_at=question_set.generated_at,
                saved_at=saved_at,
            )
            self.generation_tracker.record_success(generation_id, result)

            print(f"\n🎉 Done! Output saved to {final_output_path}\n")
            return output

        except Exception as exc:
            self.generation_tracker.record_error(generation_id, exc)
            print(f"\n❌ Pipeline failed: {exc}\n")
            raise

    def _load_prompt(self, prompt_id: Optional[str]) -> Optional[Dict[str, Any]]:
        if not prompt_id or self.prompt_lookup is None:
            return None
        return self.prompt_lookup(prompt_id)
