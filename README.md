# ailint

Lint AI agent configuration files for structural problems that agents silently ignore.

## What it does

- Scans CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, .windsurfrules for bloat, vague language, redundancy, dead references, and contradictions.
- Reports problems with file:line:column, severity, rule ID, and suggested fixes.
- Provides `--deep` mode for semantic contradiction analysis via the Claude CLI.

## Quick start

```bash
pip install ailint
```

```bash
ailint                    # auto-detects config file in current directory
ailint CLAUDE.md          # specify a file
ailint --deep AGENTS.md   # add LLM-powered semantic analysis
```

## Example output

```
$ ailint CLAUDE.md

CLAUDE.md:3:20  warning [R002] Vague phrase 'try to' is hard to enforce.
  suggestion: Replace it with a concrete condition, threshold, or required action.
CLAUDE.md:27:1  warning [R005] Possible contradiction in section 'Task Execution': ...
  suggestion: Clarify the condition that decides whether action is automatic or requires confirmation.
CLAUDE.md:145:5 error   [R004] Referenced path does not exist: rules/deploy-sop.md
  suggestion: Fix the path, create the referenced file, or remove the stale reference.

✖ 3 problems (1 error, 2 warnings)
```

Clean file:

```
$ ailint CLAUDE.md

✔ No problems found
```

## Rules

| ID | Name | Default Severity | What it catches |
|----|------|-----------------|-----------------|
| R001 | bloat | warning / error | File >500 lines (warn) or >1000 (error). Sections >100 lines. |
| R002 | vague-language | warning | Unenforceable phrases: "try to", "when possible", "盡量", "適當", etc. Skips definition context (e.g. "forbidden: 大概"). |
| R003 | redundancy | warning | Sections with >70% TF-IDF cosine similarity. Skips parent-child pairs. |
| R004 | dead-reference | error | Local file paths that don't exist. Filters out version numbers, cloud IAM roles, and wildcards. |
| R005 | contradiction | warning | Keyword pairs that conflict: "always" vs "never", "直接做" vs "先確認", etc. |

## Deep mode

`ailint --deep` invokes the `claude` CLI to perform semantic contradiction detection beyond keyword matching. It finds contradictions that static rules miss — like "use barrel files" conflicting with "never use barrel exports" in the same config.

Requires [Claude Code](https://claude.ai/claude-code) installed and authenticated.

## Install

```bash
pip install ailint          # standard
pipx install ailint         # recommended on macOS with Homebrew Python
```

## CLI reference

```
usage: ailint [-h] [--deep] [--format {text,json,github}]
              [--severity {info,warning,error}] [--no-color] [--version]
              [path]

positional arguments:
  path           Path to config file (auto-detects if omitted)

options:
  --deep         LLM-powered semantic analysis (requires claude CLI)
  --format       Output format: text (default), json, github
  --severity     Minimum severity to report: info, warning, error
  --no-color     Disable ANSI colors
  --version      Show version
```

## The story

I spent months adding rules to my CLAUDE.md until it hit 3,550 lines. Then I analyzed which rules Claude actually followed — turns out, text rules have near-zero enforcement. I refactored to ~400 lines and moved everything else to hooks. This tool checks for the structural problems I found in my own file.

## Contributing

Issues and pull requests welcome. To run tests:

```bash
pip install -e ".[test]"
pytest
```

## License

MIT
