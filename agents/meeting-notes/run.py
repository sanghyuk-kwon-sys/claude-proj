import argparse
import sys

import anthropic

from prompts import SYSTEM_PROMPT

PRIMARY_MODEL = "claude-sonnet-5"
FALLBACK_MODEL = "claude-opus-5"


def read_transcript(path: str | None) -> str:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def run(transcript: str) -> str:
    client = anthropic.Anthropic()
    request = dict(
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": transcript}],
    )

    model = PRIMARY_MODEL
    try:
        response = client.messages.create(model=model, **request)
    except (anthropic.NotFoundError, anthropic.BadRequestError) as e:
        print(
            f"모델 '{model}' 호출 중 오류가 발생하여 '{FALLBACK_MODEL}'로 재시도합니다: {e.message}",
            file=sys.stderr,
        )
        model = FALLBACK_MODEL
        response = client.messages.create(model=model, **request)

    return "\n".join(block.text for block in response.content if block.type == "text")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="회의록 자동화 에이전트")
    parser.add_argument(
        "input",
        nargs="?",
        help="회의 녹취 텍스트 파일 경로 (미지정 시 표준 입력에서 읽음)",
    )
    args = parser.parse_args()

    transcript = read_transcript(args.input)

    try:
        result = run(transcript)
    except anthropic.AuthenticationError:
        print("오류: API 키가 유효하지 않습니다.", file=sys.stderr)
        sys.exit(1)
    except anthropic.PermissionDeniedError:
        print("오류: API 키에 필요한 권한이 없습니다.", file=sys.stderr)
        sys.exit(1)
    except anthropic.RateLimitError:
        print("오류: 요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIStatusError as e:
        print(f"오류: API 요청이 실패했습니다 ({e.status_code}): {e.message}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("오류: 네트워크 연결에 실패했습니다.", file=sys.stderr)
        sys.exit(1)

    print(result)


if __name__ == "__main__":
    main()
