from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_clean(run_cli):
    result = run_cli([str(FIXTURES / "good.md"), "--no-color"])
    assert result.returncode == 0
    assert "No problems found" in result.stdout or "0 errors" in result.stdout


def test_cli_errors(run_cli):
    result = run_cli([str(FIXTURES / "dead_refs.md"), "--no-color"])
    assert result.returncode == 1


def test_cli_file_not_found(run_cli):
    result = run_cli(["/nonexistent/path/CLAUDE.md"])
    assert result.returncode == 2


def test_cli_json_format(run_cli):
    result = run_cli([str(FIXTURES / "vague.md"), "--format", "json"])
    assert result.returncode == 0
    import json
    data = json.loads(result.stdout)
    assert isinstance(data, list)


def test_cli_severity_filter(run_cli):
    result = run_cli([str(FIXTURES / "vague.md"), "--severity", "error", "--no-color"])
    assert "warning" not in result.stdout.lower().split("[")[-1] if "[" in result.stdout else True


def test_cli_version(run_cli):
    result = run_cli(["--version"])
    assert "ailint" in result.stdout
    assert result.returncode == 0
