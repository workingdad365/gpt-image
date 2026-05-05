import base64
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from openai import AzureOpenAI
from prompt_toolkit.shortcuts import prompt


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"{name} 환경 변수가 비어 있음.")
    return value


def _build_client() -> tuple[AzureOpenAI, str]:
    endpoint = _required_env("AZURE_OPENAI_ENDPOINT")
    api_version = _required_env("OPENAI_API_VERSION")
    deployment = _required_env("DEPLOYMENT_NAME")
    api_key = _required_env("AZURE_OPENAI_API_KEY")

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )
    return client, deployment


def _generate_with_progress(
    client: AzureOpenAI,
    deployment: str,
    prompt_text: str,
    size: str,
):
    stop = threading.Event()

    def _tick() -> None:
        t0 = time.perf_counter()
        while not stop.wait(0.35):
            dt = time.perf_counter() - t0
            sys.stdout.write(f"\r이미지 생성 중... {dt:.1f}초")
            sys.stdout.flush()
        sys.stdout.write("\r" + " " * 72 + "\r")
        sys.stdout.flush()

    th = threading.Thread(target=_tick, daemon=True)
    th.start()
    try:
        return client.images.generate(
            model=deployment,
            prompt=prompt_text,
            n=1,
            quality="high",
            size=size,
        )
    finally:
        stop.set()
        th.join(timeout=5.0)


def main() -> None:
    client, deployment = _build_client()

    user_prompt = prompt("프롬프트를 입력하세요: ").strip()
    if not user_prompt:
        raise SystemExit("프롬프트가 비어 있음.")

    print("화면비를 선택하세요:")
    print("  1. Auto")
    print("  2. 1024x1024")
    print("  3. 1024x1536")
    print("  4. 1536x1024")
    ratio_map = {
        "1": "auto",
        "2": "1024x1024",
        "3": "1024x1536",
        "4": "1536x1024",
    }
    ratio_choice = prompt("번호 선택 (Enter=1): ").strip()
    if not ratio_choice:
        ratio_choice = "1"
    if ratio_choice not in ratio_map:
        raise SystemExit("1~4 중 번호를 입력하거나 Enter만 누름.")
    image_size = ratio_map[ratio_choice]

    t_start = time.perf_counter()
    result = _generate_with_progress(client, deployment, user_prompt, image_size)

    if not result.data:
        raise SystemExit("응답에 data 없음.")

    item = result.data[0]
    if not item.b64_json:
        raise SystemExit("b64_json 없음. 응답을 확인함.")

    ext = (result.output_format or "png").lower()
    if ext not in ("png", "webp", "jpeg"):
        ext = "png"
    stem = datetime.now().strftime("image_%Y%m%d_%H%M%S")
    out_dir = Path.cwd() / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}.{ext}"
    out_path.write_bytes(base64.b64decode(item.b64_json))
    elapsed_sec = time.perf_counter() - t_start
    print(f"생성완료: {out_path} (소요 {elapsed_sec:.1f}초)")


if __name__ == "__main__":
    main()