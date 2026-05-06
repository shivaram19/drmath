# MCP Integration — Dart/Flutter Model Context Protocol

**Single Responsibility:** Connect AI assistants to Flutter development tools.

## Problem

AI assistants generate code blindly. They cannot introspect the widget tree, run `flutter analyze`, or verify their output. MCP bridges this gap.

## Dart/Flutter MCP Server

The official MCP server enables AI to:
- **Introspect widget tree** — Visualize layout hierarchy
- **Manage dependencies** — Search pub.dev, add packages
- **Control runtime** — Trigger hot reload, hot restart
- **Fix errors** — Analyze static and runtime errors with deep context

## Installation

```bash
# Add to project
dart pub global activate dart_mcp_server

# Or use with Gemini CLI / Claude Code
# The MCP server is bundled with Flutter AI Toolkit
```

## Capabilities

### 1. Widget Tree Introspection

```json
{
  "tool": "flutter_inspect_widget_tree",
  "arguments": {
    "route": "/practice",
    "depth": 3
  }
}
```

AI receives:
```
PracticeQuestionScreen
  └── Scaffold
      ├── AppBar (title: "Practice")
      ├── Column
      │   ├── QuestionCard
      │   │   └── Text ("What is the sum of angles?")
      │   └── OptionsList
      │       ├── ElevatedButton ("90°")
      │       ├── ElevatedButton ("180°")
      │       └── ...
      └── BottomNavigationBar
```

### 2. Dependency Management

```json
{
  "tool": "pub_add",
  "arguments": {
    "package": "riverpod",
    "version": "^2.4.0"
  }
}
```

AI can add dependencies and verify resolution.

### 3. Runtime Control

```json
{
  "tool": "flutter_hot_reload",
  "arguments": {}
}
```

### 4. Error Analysis

```json
{
  "tool": "flutter_analyze",
  "arguments": {
    "fatal_infos": true
  }
}
```

AI receives structured error output with file paths and line numbers.

## Agentic Workflow with MCP

```
1. AI receives task ("Add Riverpod state management to quiz screen")
2. AI reads .kimi/rules/flutter.md
3. AI uses MCP to inspect current widget tree
4. AI generates code changes
5. AI uses MCP to run flutter analyze
6. If errors: AI fixes and re-analyzes (loop)
7. AI uses MCP to run flutter test
8. If failures: AI fixes and re-tests (loop)
9. AI presents final diff for human review
```

## Configuration

```yaml
# .kimi/config.yaml (project-level MCP config)
mcp_servers:
  flutter:
    command: dart
    args: ["mcp", "server"]
    env:
      FLUTTER_ROOT: /home/shivaramgoud/flutter
```

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| AI generates without MCP context | Always enable MCP for Flutter projects |
| AI ignores analyze output | Gate generation on `flutter analyze` pass |
| AI adds packages without version constraints | Always specify `^x.y.z` |
| AI modifies generated files (`.g.dart`) | Exclude from edits |

## Expert Sources

Flutter Team. "Dart and Flutter MCP server." https://docs.flutter.dev/ai/mcp  
Flutter Team. "Build with AI." https://docs.flutter.dev/ai
