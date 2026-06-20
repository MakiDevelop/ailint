# ailint

Lint AI agent configuration files for structural problems that agents silently ignore.

## What it does

- Scans CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, .windsurfrules for bloat, vague language, redundancy, dead references, and contradictions.
- Reports problems with file:line:column, severity, rule ID, and suggested fixes.
- Provides --deep mode for semantic analysis via the claude CLI.

## Quick start

```bash
pip install ailint
ailint
ailint CLAUDE.md
ailint --deep AGENTS.md
```

## Example output

See [examples/sample_output.txt](examples/sample_output.txt).

Typical run:

```
$ ailint CLAUDE.md

CLAUDE.md:1:1   info    [R001] File has 487 lines (approaching recommended limit of 500)
CLAUDE.md:45:3  warning [R002] Vague language: "盡量不要" — rephrase as a concrete prohibition or remove
...
✖ 6 problems (1 error, 5 warnings)
```

Clean file:

```
$ ailint CLAUDE.md

✔ No problems found
```

## Rules

| ID   | Name            | Severity     | Description                                      |
|------|-----------------|--------------|--------------------------------------------------|
| R001 | bloat           | warning/error| File or section too long                         |
| R002 | vague-language  | warning      | Unenforceable language that agents can't act on  |
| R003 | redundancy      | warning      | Duplicate rules written different ways           |
| R004 | dead-reference  | error        | References to files/paths that don't exist       |
| R005 | contradiction   | warning      | Rules that contradict each other                 |

R001 triggers warning above 500 lines, error above 1000. Sections longer than 100 lines also flagged.

## Deep mode

`ailint --deep` invokes the `claude` CLI to perform semantic contradiction detection beyond the built-in keyword rules. Requires Claude Code CLI to be installed and authenticated. Falls back gracefully with an error if unavailable.

## CLI reference

```
usage: ailint [-h] [--deep] [--format {text,json,github}]
              [--severity {info,warning,error}] [--no-color] [--version]
              [path]

positional arguments:
  path                  Path to CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, or .windsurfrules.

options:
  --deep                Use claude CLI for semantic contradiction analysis.
  --format {text,json,github}
                        Output format.
  --severity {info,warning,error}
                        Minimum severity to report.
  --no-color            Disable ANSI colors in text output.
  --version             Show version and exit.
```

If no path is given, ailint looks for known filenames in the current directory.

## The story

I spent months adding rules to my CLAUDE.md until it hit 3,550 lines. Then I analyzed which rules Claude actually followed — turns out, text rules have near-zero enforcement. I refactored to ~400 lines and moved everything else to hooks. This tool checks for the structural problems I found in my own file.

## Contributing

Issues and pull requests welcome. Run tests with your preferred Python tooling. Keep changes focused and include example inputs that trigger the rule.

## License

MIT License. See LICENSE.
