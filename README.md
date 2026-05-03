# Dr. Math Content Automation Pipeline

One-command pipeline for Bill:
1. Scrape IXL topic via **Obscura** headless browser
2. Fetch related content from **MathIsFun**
3. Adapt to **Anti-Gravity** style (Indian context, age 12)
4. Generate **40 MCQs** with difficulty levels 1-4

## Quick Start

```bash
cd /home/shivaramgoud/projects/kalyan-anna-dr-math-automation
pip install -r requirements.txt
python -m pipeline.run --topic "Integers"
```

## Output

- `data/{topic}_raw.html` — scraped MathIsFun HTML
- `data/{topic}_antigravity.md` — adapted content
- `output/{topic}_output.json` — 40 questions + content

## How It Works

| Step | Tool | What it does |
|------|------|--------------|
| 1 | Obscura | Fetches IXL topic list & MathIsFun page |
| 2 | BeautifulSoup | Strips HTML to clean text |
| 3 | OpenAI GPT-4o-mini | Adapts text to Anti-Gravity style |
| 4 | OpenAI GPT-4o-mini | Generates 40 JSON MCQs |

## Config

Set env vars or edit `pipeline/config.py`:
- `OBSCURA_BINARY` — path to Obscura executable
- `OPENAI_API_KEY` — your API key
- `OPENAI_MODEL` — model name (default: gpt-4o-mini)
