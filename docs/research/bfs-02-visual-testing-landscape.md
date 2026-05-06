# BFS-02: Visual Testing Landscape for Flutter Mobile Apps

**Date:** 2026-05-05  
**Scope:** Screenshot capture, pixel analysis, accessibility scanning, and AI-powered visual evaluation for Flutter  
**Research Phase:** BFS (Breadth-First Landscape Mapping)  
**Informs:** ADR-011, `mathwise_build/scripts/*` visual testing pipeline  

---

## 1. Decomposition

Visual testing for a Flutter educational app decomposes into:

1. **Screenshot capture** — How to render and capture screens at multiple viewports
2. **Pixel/layout analysis** — How to verify colors, spacing, typography against design tokens
3. **Accessibility scanning** — How to detect WCAG 2.1 AA violations automatically
4. **AI vision evaluation** — How to assess visual hierarchy, cognitive load, and UX quality
5. **Report generation** — How to aggregate findings into actionable human-readable output
6. **CI integration** — How to gate merges on visual quality (future consideration)

---

## 2. Landscape Scan

### 2.1 Screenshot Capture Tools

| Tool | Type | Flutter Integration | Multi-Viewport | Interaction Support | Cost |
|------|------|--------------------:|---------------:|--------------------:|------|
| `flutter test --update-goldens` | Framework native | Excellent | Via `tester.view.physicalSize` | Full (widget tester) | $0 |
| `integration_test` + `screenshot` | Framework native | Excellent | Via `WidgetTester` | Full (tap, drag, etc.) | $0 |
| Playwright (Chromium) | Browser automation | Good (web build) | Excellent (viewport API) | Click, type, wait | $0 |
| `flutter screenshot` (CLI) | CLI tool | Good | No (device frame only) | None | $0 |
| Firebase Test Lab | Cloud device farm | Excellent | Many real devices | Automated robo test | $$$ |
| Mobilerun (physical device) | Custom agentic | Excellent | One device at a time | LLM-driven | ~$0.15/run |

**Key Finding:** For a local pipeline testing 11 screens × 5 viewports = 55 screenshots, Playwright against a Flutter web build offers the best trade-off: zero cost, deterministic, multi-viewport, and interaction-capable [^1]. Golden files (`matchesGoldenFile`) are platform-dependent and require Ahem font lockdown for CI consistency [^2]. Physical device testing (Mobilerun) is valuable for E2E validation but cannot scale to 55 shots per run economically.

### 2.2 Pixel / Layout Analysis Tools

| Tool | Language | What It Detects | Flutter Suitability |
|------|----------|----------------|--------------------|
| PIL / Pillow (Python) | Python | Color histograms, bounding boxes, pixel diffs | Excellent (PNG input) |
| OpenCV | Python/C++ | Advanced CV, edge detection, OCR | Good but heavy dependency |
| `image` (Dart) | Dart | Pixel-level inspection within Flutter tests | Good but slower than Python |
| Applitools / Percy | SaaS | AI-powered visual diff | Excellent UI, proprietary lock-in, $$$ |
| Chromatic | SaaS | Storybook-based visual testing | Not applicable (no Storybook) |
| axe-core | JS/Python | Accessibility rules engine | Good via Playwright |
| `accessibility_tools` (Flutter) | Dart | Touch target, contrast in widget tests | Excellent but widget-test only |

**Key Finding:** Pillow (PIL) provides sufficient pixel-level analysis for design token validation at zero cost and zero lock-in [^3]. OpenCV adds capability (contour detection, OCR) but increases dependency weight by ~80MB. For our use case — verifying colors, spacing, and touch target sizes against a token manifest — Pillow is the optimal choice per Decision Authority #1 (boring, well-understood).

### 2.3 AI Vision Evaluation Models

| Model | Provider | Cost/Image | Vision Quality | Speed | Open Source? |
|-------|----------|-----------:|---------------|-------|-------------|
| Gemini 2.0 Flash | Google | ~$0.0003 | Excellent (UI understanding) | Fast | No |
| GPT-4o-mini | OpenAI | ~$0.0006 | Very good | Fast | No |
| GPT-4o | OpenAI | ~$0.005 | Excellent | Medium | No |
| LLaVA 1.6 | Community | $0 (self-hosted) | Good | Slow (local GPU) | Yes |
| Moondream 2 | Community | $0 (self-hosted) | Moderate | Medium | Yes |
| Claude 3.5 Sonnet | Anthropic | ~$0.003 | Excellent | Medium | No |

**Key Finding:** Gemini 2.0 Flash is ~10× cheaper than GPT-4o with sufficient quality for UI screenshot classification and rubric evaluation [^4]. Self-hosted open-source models (LLaVA, Moondream) avoid API costs but require GPU infrastructure and produce lower consistency on fine-grained UI evaluation tasks [^5]. For a cost cap of $0.03/run (11 screens), Gemini Flash is the pragmatic choice.

### 2.4 Accessibility Scanning Tools

| Tool | Type | WCAG Version | Flutter Integration | Cost |
|------|------|-------------|--------------------|------|
| `accessibility_tools` | Flutter package | 2.1 AA | Widget tests | $0 |
| axe-core | JS library | 2.1 AA | Playwright integration | $0 |
| Lighthouse | Chrome DevTools | 2.1 AA | CLI or Playwright | $0 |
| Accessibility Scanner (Android) | Google tool | 2.1 AA | Physical device | $0 |
| `flutter_test` Semantics | Framework | 2.1 AA | Built-in matchers | $0 |

**Key Finding:** For a web-build-based pipeline, axe-core via Playwright provides the most comprehensive automated accessibility scan [^6]. However, Flutter web renders to CanvasKit/SKIA, which may produce DOM structures that confuse HTML-based scanners. `accessibility_tools` running in widget tests is more accurate for Flutter semantics but cannot evaluate rendered screenshots. A hybrid approach — `accessibility_tools` for semantic structure + visual rubric for color/touch targets — covers both domains.

---

## 3. Expert Mapping

| Expert / Project | Contribution | Relevance |
|-----------------|--------------|-----------|
| Flutter Goldens Team | `matchesGoldenFile`, `flutter_test_config.dart` | Golden file best practices [^2] |
| Playwright Team (Microsoft) | Cross-browser automation, viewport API | Screenshot capture engine [^1] |
| Deque (axe-core) | WCAG rule engine, accessibility standards | Automated a11y scanning [^6] |
| Google AI (Gemini) | Vision-language models for UI understanding | AI UX evaluation [^4] |
| Very Good Ventures | `very_good_analysis`, custom lints | Static analysis for Flutter [^7] |
| W3C WAI | WCAG 2.1 AA specification | Accessibility standard of record |

---

## 4. Failure Mode Inventory

| Failure | Tool Observation | Prevention |
|---------|-----------------|------------|
| Platform-dependent goldens | Flutter Team [^2] | Ahem font + `flutter_test_config.dart` |
| CanvasKit DOM opacity | axe-core on Flutter web | Prefer widget-test accessibility over web-scan |
| LLM vision hallucination | OpenAI evals [^5] | Structured rubric + confidence scores + human review |
| Screenshot flakiness (timing) | Playwright docs [^1] | `wait_until="networkidle"` + explicit waits |
| Font rendering variance | Golden file community | Lock font to Ahem or use web build screenshots |
| Oversized API bills | Gemini pricing [^4] | Hash-based caching, cost cap, batching |

---

## 5. References

[^1]: Microsoft. (2024). *Playwright Documentation: Screenshots*. https://playwright.dev/python/docs/screenshots  
[^2]: Flutter Team. (2024). *Golden File Testing*. https://docs.flutter.dev/testing/android-and-ios  
[^3]: Pillow Contributors. (2024). *Pillow (PIL Fork) Documentation*. https://pillow.readthedocs.io  
[^4]: Google. (2024). *Gemini API Pricing*. https://ai.google.dev/pricing  
[^5]: Liu, H., et al. (2024). *LLaVA-NeXT: Improved reasoning, OCR, and world knowledge*. arXiv:2401.06159.  
[^6]: Deque Systems. (2024). *axe-core*. https://github.com/dequelabs/axe-core  
[^7]: Very Good Ventures. (2024). *very_good_analysis*. https://github.com/VeryGoodOpenSource/very_good_analysis
