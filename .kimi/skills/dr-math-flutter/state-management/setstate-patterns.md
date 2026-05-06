# StatefulWidget Patterns — When setState Is Enough

**Single Responsibility:** Use `StatefulWidget` correctly without creating maintenance debt.

## Problem

`setState` is not bad. Misuse of `setState` is bad. The failure mode: rebuilding the entire widget tree for a localized state change.

## Correct Usage

### 1. Localize State to the Lowest Common Ancestor

```dart
// BAD: State at top rebuilds everything
class _HomeScreenState extends State<HomeScreen> {
  bool _isLoading = false; // Only needed in one section

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Header(),
          _isLoading ? CircularProgressIndicator() : Content(), // BAD
          Footer(),
        ],
      ),
    );
  }
}

// GOOD: Extract state to dedicated widget
class _LoadingSection extends StatefulWidget {
  @override
  State<_LoadingSection> createState() => _LoadingSectionState();
}

class _LoadingSectionState extends State<_LoadingSection> {
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return _isLoading
      ? const CircularProgressIndicator()
      : const Content();
  }
}
```

### 2. Use `const` to Stop Rebuild Propagation

```dart
// GOOD: Header and Footer are const — they NEVER rebuild
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: const [
          Header(),        // const = no rebuild
          LoadingSection(), // only this rebuilds
          Footer(),        // const = no rebuild
        ],
      ),
    );
  }
}
```

**Rule:** Every widget that does NOT depend on changing state should be `const`.

### 3. Controllers Over setState for Input

```dart
// BAD: setState on every keystroke
class _BadFormState extends State<BadForm> {
  String _email = '';

  @override
  Widget build(BuildContext context) {
    return TextField(
      onChanged: (value) => setState(() => _email = value),
    );
  }
}

// GOOD: Controller handles input without setState
class _GoodFormState extends State<GoodForm> {
  final _emailController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose(); // ALWAYS dispose
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(controller: _emailController);
  }
}
```

### 4. AnimationController Is State Management

```dart
// BAD: Manual animation with setState
Timer.periodic(Duration(milliseconds: 16), (_) => setState(() => _progress += 0.01));

// GOOD: AnimationController
class _AnimatedProgressState extends State<AnimatedProgress>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (_, __) => CircularProgressIndicator(value: _controller.value),
    );
  }
}
```

## The `mounted` Guard

```dart
void _loadData() async {
  final data = await repository.fetch();
  if (!mounted) return; // CRITICAL: widget may be disposed during async
  setState(() => _data = data);
}
```

**Without `mounted` check:** `setState() called after dispose()` — runtime crash.

## Performance Checklist

- [ ] Is the state truly local to this widget? → `StatefulWidget`
- [ ] Does any descendant NOT depend on this state? → Make it `const`
- [ ] Is this input/animation/scroll? → Use controller, not setState
- [ ] Is there an async gap before setState? → Check `mounted`
- [ ] Is the state needed by parent or sibling? → Lift to `ValueNotifier` or Riverpod

## Expert Sources

Hráček, F. "Flutter Performance Best Practices." https://docs.flutter.dev/perf/best-practices  
Flutter Team. "StatefulWidget class." https://api.flutter.dev/flutter/widgets/StatefulWidget-class.html
