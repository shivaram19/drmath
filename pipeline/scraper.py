"""Scraper using the local Obscura headless browser."""
import subprocess
import re
from pathlib import Path
from typing import List, Tuple

from pipeline.config import OBSCURA_BINARY, IXL_BASE, MATHISFUN_BASE


def _obscura_fetch(url: str) -> str:
    """Fetch a page via Obscura and return raw HTML."""
    cmd = [
        OBSCURA_BINARY,
        "fetch",
        url,
        "--user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"Obscura failed: {result.stderr}")
    return result.stdout


def fetch_ixl_topics() -> List[Tuple[str, str]]:
    """Return list of (topic_name, category) from IXL Class VII."""
    html = _obscura_fetch(IXL_BASE)
    # IXL stores skill names inside <span class="skill-name"> tags
    names = re.findall(r'skill-name"[^>]*>([^<]+)', html)
    # Simple grouping — everything is under Class VII
    return [(name.strip(), "Class VII Maths") for name in names]


def fetch_mathisfun_page(slug: str) -> str:
    """Fetch a MathIsFun page by slug (e.g. 'positive-negative-integers.html')."""
    url = f"{MATHISFUN_BASE}/{slug}"
    return _obscura_fetch(url)


def search_mathisfun_topic(topic: str) -> tuple[str, str]:
    """Heuristic: map topic keywords to known MathIsFun slugs.
    
    Returns (html, url_used).
    """
    topic_lower = topic.lower()
    mapping = {
        "integer": "positive-negative-integers.html",
        "number line": "number-line.html",
        "absolute value": "numbers/absolute-value.html",
        "fraction": "fractions.html",
        "decimal": "decimals.html",
        "ratio": "numbers/ratio.html",
        "proportion": "algebra/proportions.html",
        "percentage": "percentage.html",
        "algebra": "algebra/index.html",
        "equation": "algebra/index.html",
        "exponent": "numbers/exponent.html",
        "geometry": "geometry/index.html",
        "triangle": "geometry/triangles.html",
        "circle": "geometry/circle.html",
        "area": "area.html",
        "perimeter": "perimeter.html",
        "volume": "geometry/cuboids-volumes.html",
        "probability": "data/probability.html",
        "mean": "data/mean.html",
        "median": "data/median.html",
        "mode": "data/mode.html",
        "data": "data/index.html",
        "graph": "data/graphs-index.html",
        "congruence": "geometry/congruent.html",
        "symmetry": "geometry/symmetry.html",
        "angle": "geometry/angles.html",
        "parallel": "geometry/parallel-lines.html",
        "pythagoras": "geometry/pythagorean-theorem.html",
        "rational": "rational-numbers.html",
        "sequence": "numberpatterns.html",
        "hcf": "numbers/hcf.html",
        "lcm": "numbers/lcm.html",
        "prime": "numbers/prime-factorization.html",
    }
    for keyword, slug in mapping.items():
        if keyword in topic_lower:
            url = f"{MATHISFUN_BASE}/{slug}"
            return fetch_mathisfun_page(slug), url
    # Fallback: try the topic as a slug directly
    slug = f"{topic_lower.replace(' ', '-')}.html"
    url = f"{MATHISFUN_BASE}/{slug}"
    return fetch_mathisfun_page(slug), url
