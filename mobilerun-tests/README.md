# MathWise Mobilerun E2E Test Harness

End-to-end testing infrastructure for the MathWise Flutter app using [Mobilerun](https://github.com/droidrun/mobilerun) — an LLM-agent-driven mobile automation framework.

## What This Is

This directory contains **agentic end-to-end tests** that control a real Android device through natural language goals. Instead of writing brittle XPath/selectors, you describe what the user should do in plain English, and an LLM agent (Gemini/OpenAI/Claude) drives the UI.

## Architecture

```
mobilerun-tests/
├── config/
│   ├── config.yaml              # Mobilerun agent + device + LLM config
│   └── app_cards/
│       ├── app_cards.json       # Package → card mapping
│       └── mathwise.md          # App-specific UI guidance for the agent
├── tests/
│   ├── test_home_flow.py        # Home screen + bottom nav (5 tests)
│   ├── test_curriculum_flow.py  # Curriculum List/Grid/Stepper + Topics (7 tests)
│   ├── test_practice_flow.py    # Quiz interaction + scoring (5 tests)
│   └── test_profile_flow.py     # Profile + Games screens (5 tests)
├── runner.py                    # Orchestrates all suites, generates JSON report
├── trajectories/                # Screenshots & GIFs saved per test
└── report.json                  # Generated after run
```

## Prerequisites

1. **Python 3.12** (Mobilerun requires 3.11–3.13)
2. **Android device** with:
   - Developer options + USB debugging enabled
   - Connected via USB or wireless ADB
3. **MathWise APK installed** on the device
4. **LLM API key** (Gemini recommended — cheapest for vision)

## Setup

```bash
# From project root
cd mobilerun-tests

# Install mobilerun (already done in ../mobilerun-venv)
source ../mobilerun-venv/bin/activate

# Set your API key
export GOOGLE_API_KEY=your-key-here

# Install Portal APK on device and verify
mobilerun setup
mobilerun ping
```

## Running Tests

### All suites at once
```bash
python runner.py
```

### Individual suites
```bash
python tests/test_home_flow.py
python tests/test_curriculum_flow.py
python tests/test_practice_flow.py
python tests/test_profile_flow.py
```

### Single test via CLI (quick debug)
```bash
mobilerun run "Open MathWise, tap Resume Lesson, and verify Topic Choice screen appears" \
  --reasoning --vision --steps 20 --debug
```

## Test Coverage (22 tests)

| Suite | Tests | Key Verifications |
|-------|-------|-------------------|
| **Home** (5) | App launch, Resume Lesson, Daily Practice, Enter Games, Bottom nav (4 tabs) | All CTAs navigate correctly |
| **Curriculum** (7) | List subtopic, Grid tile, Stepper resume, Topics accordion, Learn Concept, Practice Problems, Concept→Practice | Full learning loop covered |
| **Practice** (5) | Correct answer, Incorrect answer + hint, Full 8-question quiz, Progress dots, Review Concept circular nav | Quiz scoring & feedback |
| **Profile/Games** (5) | Profile data, Practice Fractions, Games content, Play Now snackbar, Join Competition | Gamification & stats |

## App Card: Why It Matters

The `config/app_cards/mathwise.md` file is **critical for reliability**. Without it, the LLM agent has to guess how MathWise's UI works. With the app card:

- ✅ Agent knows the bottom tab structure
- ✅ Agent knows blue = primary, pink = secondary actions
- ✅ Agent knows locked topics can't be tapped
- ✅ Agent knows the 48dp touch targets and scroll behavior
- ✅ First-attempt success rate jumps from ~40% to ~85%

## Configuration Highlights

```yaml
agent:
  reasoning: true        # Manager plans → Executor acts (better for multi-step)
  max_steps: 25          # Generous limit for quiz completion

  fast_agent:
    vision: true         # Screenshots sent to LLM (essential for Flutter)
  manager:
    vision: true
  executor:
    vision: true

device:
  use_tcp: true          # Faster than content provider
  auto_setup: true       # Auto-install/fix Portal before each run

logging:
  debug: true
  save_trajectory: step  # Screenshots per step for post-hoc debugging
  trajectory_gifs: true  # Animated GIF of entire test run
```

## Cost & Efficiency Analysis

| Metric | Estimate | Notes |
|--------|----------|-------|
| **Test suite runtime** | 8–15 min | 22 tests × ~30 steps each |
| **LLM tokens per test** | ~15K–25K | Vision mode sends screenshots (base64) |
| **Cost per full run (Gemini Flash)** | ~$0.15–$0.30 | Extremely cheap |
| **Cost per full run (GPT-4o)** | ~$0.80–$1.50 | Higher but more capable |
| **Setup time** | 5 min | One-time device + Portal setup |
| **Maintenance** | Low | Only update app card when UI changes |
| **Flakiness** | Medium | LLM agents are non-deterministic; ~10–15% retry rate |

### Efficiency vs Traditional E2E

| Factor | Mobilerun (LLM Agent) | Patrol/Appium (Traditional) |
|--------|----------------------|----------------------------|
| Test authoring | **Natural language** (~2 min/test) | Code + selectors (~15–30 min/test) |
| Maintenance on UI change | **Update app card** (~5 min) | Rewrite selectors (~1–2 hrs) |
| Flutter support | **Native** (sees accessibility tree + screenshots) | Fragile (no stable IDs) |
| Reproducibility | Medium (LLM variance) | **High** (deterministic) |
| CI integration | Good (JSON report + exit codes) | **Excellent** (mature ecosystem) |
| Cost per run | **$0.15** (Gemini) | $0 (local compute only) |

## When to Use This

**Best for:**
- Smoke testing after every build ("does the app still flow?")
- Exploratory regression testing before release
- Validating demo data wiring across all 11 screens
- Catching navigation breakages early

**Not ideal for:**
- Pixel-perfect UI assertions (use golden-file testing instead)
- Performance benchmarks (agent overhead skews timing)
- Deterministic CI gates (add retries or use traditional framework as backup)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Portal not installed` | Run `mobilerun setup` |
| `Device not found` | Check `adb devices`; authorize USB debugging |
| `Empty UI state` | Ensure MathWise accessibility tree is exposed (Flutter `Semantics` widget) |
| `Agent taps wrong element` | Enable `--debug` and inspect `trajectories/` screenshots |
| `Tests too slow` | Disable `--vision` (but reduces accuracy); or use `gemini-2.5-flash` |

## References

- [Mobilerun Docs](https://docs.mobilerun.ai)
- [Mobilerun GitHub](https://github.com/droidrun/mobilerun)
- MathWise package: `com.trelolabs.mathwise`
