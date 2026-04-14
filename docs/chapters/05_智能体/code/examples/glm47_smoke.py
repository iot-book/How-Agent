"""Tiny GLM 4.7 online smoke check via BigModel's OpenAI-compatible API."""

from __future__ import annotations

import os
import sys

BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
MODEL = "glm-4.7"


def main() -> int:
    try:
        from openai import OpenAI
    except ImportError:
        print("GLM smoke failed: openai package is not installed.", file=sys.stderr)
        return 2

    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("GLM smoke failed: GLM_API_KEY is not set.", file=sys.stderr)
        return 2

    try:
        client = OpenAI(api_key=api_key, base_url=BASE_URL, timeout=30)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Reply with pong."}],
            max_tokens=8,
        )
    except Exception as exc:  # pragma: no cover - network/service dependent
        print(f"GLM smoke failed: {exc}", file=sys.stderr)
        return 1

    if not response.choices:
        print("GLM smoke failed: no choices returned.", file=sys.stderr)
        return 1

    reply = (response.choices[0].message.content or "").strip()
    print(f"GLM smoke ok: model={MODEL} reply={reply!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
