from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parent.parent.parent / "specs" / "system_prompt.md"

SYSTEM_PROMPT = SPEC_PATH.read_text(encoding="utf-8")
