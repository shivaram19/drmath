# Flutter Educational Games Integration — Research Document

**Date:** 2026-05-13  
**Scope:** How to build and integrate low-latency educational games into the Dr. Math Flutter app  
**Research Phase:** BFS (Breadth-First Landscape Mapping)  
**Branch:** `games-integration`

---

## 1. Research Questions

1. What Flutter game engines and frameworks exist for educational games?
2. What latency budgets must we hit for 60fps gameplay on mid-range Android devices?
3. How do successful educational apps integrate games without disrupting the learning flow?
4. What game mechanics build mathematical curiosity rather than just drill-and-practice?
5. How do we keep game code isolated from the main app architecture?

---

## 2. Flutter Game Engine Landscape

### 2.1 Flame (Most Popular)
- **GitHub:** `flame-engine/flame` — 10k+ stars, active community
- **Pros:** Full 2D game engine, component system, collision detection, sprite animation, particle effects
- **Cons:** Adds ~2-3MB to APK, learning curve for non-game devs
- **Latency:** 60fps achievable on devices with Flutter's Skia/Impeller renderers
- **Use case:** Complex games with physics, animations, real-time interactions

### 2.2 flutter_chess_board / Custom Canvas
- **Pros:** Zero dependencies, full control, smallest APK impact
- **Cons:** Reinvent the wheel for common game patterns
- **Latency:** Best possible — direct CustomPainter with no engine overhead
- **Use case:** Simple board games, number puzzles, drag-and-drop activities

### 2.3 Rive
- **Pros:** Designer-friendly, state machines, tiny runtime, 60fps guaranteed
- **Cons:** Requires Rive editor, less suitable for procedural gameplay
- **Latency:** Excellent — vector-based, GPU-accelerated
- **Use case:** Animated characters, interactive tutorials, reward animations

### 2.4 Decision Matrix

| Engine | APK Impact | Learning Curve | Flexibility | 60fps on Low-End | Best For |
|--------|-----------|----------------|-------------|------------------|----------|
| Flame | ~2-3MB | Medium | High | Yes | Physics games, platformers |
| Custom Canvas | 0KB | High | Unlimited | Yes | Simple puzzles, board games |
| Rive | ~200KB | Low | Medium | Yes | Characters, UI animations |

**Preliminary recommendation:** Start with Custom Canvas for math puzzles (zero overhead), evaluate Flame for complex games, use Rive for character/reward animations.

---

## 3. Latency & Performance Requirements

### 3.1 Frame Budget
- **60fps target:** 16.67ms per frame
- **Flutter's overhead:** ~2-4ms (widget tree, layout, paint)
- **Game logic budget:** ~8-10ms remaining
- **Jank threshold:** > 100ms frame time = noticeable stutter

### 3.2 Performance Techniques
1. **`RepaintBoundary`** — Isolate game canvas from rest of widget tree
2. **`CustomPainter` + `Ticker`** — Manual animation loop, bypass widget rebuilds
3. **Object pooling** — Reuse game objects instead of allocating per frame
4. **Image atlas** — Single texture for all sprites vs. individual images
5. **Impeller renderer** — Flutter's new renderer (3.27+), better GPU utilization
6. **Avoid `setState` in game loop** — Use `ValueNotifier`, `Stream`, or direct canvas invalidation

### 3.3 Device Baseline
- **Target:** Android 8+ (API 26), 3GB RAM, Mali-G51 / Adreno 505
- **Test device reference:** Xiaomi Redmi 9A, Samsung Galaxy A12
- **Metric:** Consistent 55+ fps during gameplay, <100ms tap-to-response

---

## 4. Curiosity-Building Game Mechanics

### 4.1 Core Principle
> "The game should make the child *want* to know the math, not just *have* to do it."

### 4.2 Mechanic Patterns

#### Pattern A: Discovery Through Play
- Child manipulates objects, pattern emerges naturally
- Example: Dragging fractions onto a number line — "Why does 1/2 + 1/2 fill the whole?"
- No explicit "solve this" prompt — the question arises from play

#### Pattern B: Progressive Revelation
- Start with simple, visually satisfying interactions
- Complexity unlocks gradually as mastery emerges
- Example: Number bonds start with visual blocks, progress to abstract equations

#### Pattern C: Narrative Anchoring
- Math concepts embedded in a story the child cares about
- Example: "Help the astronaut fuel the rocket — you need exactly 3/4 tank"
- Wrong answers are story events, not failures

#### Pattern D: Peer-like Competition
- Compete against previous self, not others (avoid anxiety)
- "Beat your best time" vs. "Beat your friend"
- Leaderboards optional, personal progress primary

### 4.3 Anti-Patterns to Avoid
- ❌ Timed pressure on conceptual learning (creates math anxiety)
- ❌ Extrinsic rewards for every correct answer (undermines intrinsic motivation)
- ❌ Gamification without gameplay (badges for worksheet completion)
- ❌ Disconnect between game mechanic and math concept (trivia skins)

---

## 5. Integration Architecture

### 5.1 Isolation Boundary

```
lib/
├── main.dart              ← App entry (untouched by games)
├── features/
│   ├── home/
│   ├── practice/
│   ├── games/             ← NEW: Game screens & navigation
│   │   ├── screens/
│   │   ├── widgets/
│   │   ├── models/        ← Game state (isolated)
│   │   └── engine/        ← Custom game loop (if not using Flame)
│   └── profile/
├── games/                 ← NEW: Reusable game components
│   ├── components/        ← Canvas painters, sprites, animations
│   ├── mechanics/         ← Curiosity-building pattern implementations
│   └── utils/             ─ Game math, collision, etc.
└── core/
```

### 5.2 State Management
- **Game state:** `flutter_bloc` or plain `ChangeNotifier` (isolated from app state)
- **Progress sync:** Game completion → event → `ProfileBloc` (fire-and-forget)
- **No circular deps:** `games/` never imports from `features/practice/` or `pipeline/`

### 5.3 Navigation
- Games launched via deep links or in-app navigation
- Each game is a self-contained route: `/games/{game-id}`
- Back gesture pauses game, shows "Exit? Progress saved" dialog

---

## 6. Reference Apps for Deep Study

### 6.1 Prodigy Math Game
- **Platform:** Web + Mobile
- **Mechanic:** RPG-style battles where spells require math answers
- **Lesson:** Narrative anchoring works — kids willingly do hundreds of problems
- **Caution:** Heavy extrinsic reward loop; we should balance with intrinsic curiosity

### 6.2 DragonBox (WeWantToKnow)
- **Platform:** iOS, Android
- **Mechanic:** Abstract algebra through visual puzzle manipulation
- **Lesson:** Discovery through play — no numbers visible initially, algebra emerges organically
- **Relevance:** Direct model for our "curiosity first" approach

### 6.3 Mathigon
- **Platform:** Web (PWA)
- **Mechanic:** Interactive explorations, manipulatives, storytelling
- **Lesson:** Progressive revelation — each interaction builds on the last
- **Relevance:** Best-in-class for conceptual (not procedural) math

### 6.4 Khan Academy Kids
- **Platform:** iOS, Android
- **Mechanic:** Mini-games mixed with guided learning paths
- **Lesson:** Game sessions should be 3-5 minutes, not 20+ minute marathons
- **Relevance:** Attention span alignment for Class VII (age 12-13)

---

## 7. Next Research Steps (DFS Phase)

1. **Spike:** Build a "Number Line Explorer" prototype with CustomPainter
   - Tap to place fractions, drag to compare, watch equivalence
   - Measure: frame time, memory, APK impact
   - Document: what worked, what didn't

2. **Spike:** Evaluate Flame for a "Fraction Tower" physics game
   - Stack fraction blocks to reach a target height
   - Measure: startup time, battery drain, low-end device performance

3. **Spike:** Rive animation for reward/character system
   - Animated mascot reacts to progress
   - Measure: APK size, loading time, smoothness

4. **User Research:** Interview 3-5 Class VII students
   - What games do they play? (Free Fire, Subway Surfers, etc.)
   - What makes them keep playing?
   - Show DragonBox/Mathigon clips — reactions?

5. **Technical Research:** Profile existing Dr. Math app
   - Current frame times on target devices
   - Memory baseline before adding games
   - Identify headroom for game engine overhead

---

## 8. References

[^1]: Csikszentmihalyi, M. (1990). *Flow: The Psychology of Optimal Experience*. Harper & Row. — Engagement through challenge-skill balance.

[^2]: Devlin, K. (2011). *Mathematics Education for a New Era: Video Games as a Medium for Learning*. A K Peters/CRC Press. — Math games design principles.

[^3]: WeWantToKnow. (2012-2024). *DragonBox* series. — Discovery-based algebra games.

[^4]: Mathigon. (2016-2024). *Mathigon — The Textbook of the Future*. — Interactive conceptual math.

[^5]: Flame Engine. (2024). *Flame Documentation*. https://docs.flame-engine.org/ — Flutter game engine reference.

[^6]: Flutter Team. (2024). *Performance Best Practices*. https://docs.flutter.dev/perf — Rendering optimization.

[^7]: Gee, J. P. (2003). *What Video Games Have to Teach Us About Learning and Literacy*. Palgrave Macmillan. — Learning principles from games.

---

*Document version: 1.0*  
*Next review: After Spike #1 completion*  
*Owner: games-integration branch*
