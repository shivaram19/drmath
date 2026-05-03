# ADR-001: Headless Browser Selection

**Date:** 2026-05-03  
**Scope:** Web scraping infrastructure  
**Research Phase:** BFS completed; DFS on Obscura internals pending  
**Status:** Accepted

## Context

The pipeline must scrape two sources:
1. IXL (https://in.ixl.com/maths/class-vii) — skill tree and topic metadata
2. MathIsFun (https://www.mathsisfun.com/) — pedagogical content with visuals

Both sites serve JavaScript-heavy or anti-bot-protected content. curl/wget alone fail to extract meaningful data due to header size limits, Cloudflare-style protection, and dynamic rendering.

## Decision

Use **Obscura**, a Rust-based lightweight headless browser already present on the target machine, as the primary scraping engine.

## Consequences

**Positive:**
- Already available on machine; zero additional dependency cost [^1].
- Stealth mode evades basic bot detection.
- CDP-compatible for future automation expansion.
- Fast startup vs. Chromium-based alternatives.

**Negative:**
- Smaller community than Playwright/Puppeteer; debugging documentation sparse.
- No built-in retry logic; must implement at application layer.
- Rust binary requires specific glibc version on deployment target.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Selenium | Heavy JVM/Chrome dependency; 200MB+ overhead [^2] |
| Playwright | Excellent but adds Node.js + browser download burden |
| curl + regex | Fails on IXL dynamic content; header size errors observed |
| requests + BeautifulSoup alone | MathIsFun blocks; insufficient for JS rendering |

## References

[^1]: Obscura binary validated at `/home/shivaramgoud/tinkering/tinkering-with-claws/picocloth/shared/project/tools/linkedin-scraper/obscura-src/target/release/obscura`.
[^2]: Selenium documentation. https://www.selenium.dev/documentation/
