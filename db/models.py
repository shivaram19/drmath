"""SQLAlchemy ORM models for Dr. Math."""
import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.database import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    question_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    generations: Mapped[List["Generation"]] = relationship("Generation", back_populates="prompt")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    generations: Mapped[List["Generation"]] = relationship("Generation", back_populates="topic")


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    prompt_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("prompts.id"), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    output_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_questions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty_distribution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    adapted_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    questions_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_html_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    antigravity_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    meta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="generations")
    prompt: Mapped[Optional["Prompt"]] = relationship("Prompt", back_populates="generations")
    evaluations: Mapped[List["Evaluation"]] = relationship("Evaluation", back_populates="generation", cascade="all, delete-orphan")
    grounding_logs: Mapped[List["GroundingLog"]] = relationship("GroundingLog", back_populates="generation", cascade="all, delete-orphan")

    @property
    def avg_rating(self) -> Optional[float]:
        if not self.evaluations:
            return None
        return sum(e.rating for e in self.evaluations) / len(self.evaluations)

    @property
    def difficulty_dict(self) -> dict:
        if self.difficulty_distribution:
            return json.loads(self.difficulty_distribution)
        return {}


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    generation_id: Mapped[int] = mapped_column(Integer, ForeignKey("generations.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluated_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    generation: Mapped["Generation"] = relationship("Generation", back_populates="evaluations")


class GroundingLog(Base):
    __tablename__ = "grounding_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    generation_id: Mapped[int] = mapped_column(Integer, ForeignKey("generations.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_status: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    generation: Mapped["Generation"] = relationship("Generation", back_populates="grounding_logs")
