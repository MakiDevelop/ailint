from ailint.parser import parse, flatten_sections


def test_parse_empty():
    assert parse("") == []


def test_parse_single_section():
    sections = parse("## Hello\nSome content here.")
    assert len(sections) == 1
    assert sections[0].heading == "Hello"
    assert sections[0].level == 2


def test_parse_nested():
    text = "## Parent\nParent content\n### Child\nChild content"
    sections = parse(text)
    assert len(sections) == 1
    assert sections[0].heading == "Parent"
    assert len(sections[0].children) == 1
    assert sections[0].children[0].heading == "Child"


def test_parse_line_numbers():
    text = "# Title\nLine 2\n## Section\nLine 4"
    sections = parse(text)
    assert sections[0].line_start == 1
    flat = flatten_sections(sections)
    assert flat[1].line_start == 3


def test_parse_no_headings():
    sections = parse("Just some text\nwithout any headings")
    assert sections == []


def test_flatten():
    text = "# A\n## B\n### C\n## D"
    sections = parse(text)
    flat = flatten_sections(sections)
    headings = [s.heading for s in flat]
    assert headings == ["A", "B", "C", "D"]
