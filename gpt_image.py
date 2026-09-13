import base64
import os
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from dotenv import load_dotenv
from openai import AzureOpenAI
from prompt_toolkit.shortcuts import prompt

IMAGE_DEPLOYMENTS = (
    "gpt-image-2.5-flare",
    "gpt-image-2.5-sunburst",
)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"{name} 환경 변수가 비어 있음.")
    return value


def _select_deployment() -> str:
    print("사용할 모델을 선택하세요:")
    for index, deployment in enumerate(IMAGE_DEPLOYMENTS, start=1):
        print(f"  {index}. {deployment}")

    choice = prompt("번호 선택 (Enter=1): ").strip() or "1"
    if not choice.isdigit() or not 1 <= int(choice) <= len(IMAGE_DEPLOYMENTS):
        raise SystemExit(
            f"1~{len(IMAGE_DEPLOYMENTS)} 중 번호를 입력하거나 Enter만 누름."
        )
    return IMAGE_DEPLOYMENTS[int(choice) - 1]


def _build_client() -> tuple[AzureOpenAI, str]:
    load_dotenv(dotenv_path=Path.cwd() / ".env")

    endpoint = _required_env("AZURE_OPENAI_ENDPOINT")
    api_version = _required_env("OPENAI_API_VERSION")
    deployment = _select_deployment()
    api_key = _required_env("AZURE_OPENAI_API_KEY")

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )
    return client, deployment


def _validate_custom_size(value: str) -> str:
    match = re.fullmatch(r"(\d+)[xX](\d+)", value.strip())
    if not match:
        raise SystemExit("해상도는 WIDTHxHEIGHT 형식으로 입력함.")

    width, height = (int(dimension) for dimension in match.groups())
    pixels = width * height
    if width % 16 or height % 16:
        raise SystemExit("가로와 세로는 모두 16px 배수여야 함.")
    if max(width, height) > 3840:
        raise SystemExit("가장 긴 변은 3840px 이하여야 함.")
    if max(width, height) > min(width, height) * 3:
        raise SystemExit("가로세로비는 1:3~3:1 범위여야 함.")
    if not 655_360 <= pixels <= 8_294_400:
        raise SystemExit("총 픽셀 수는 655,360~8,294,400 범위여야 함.")
    return f"{width}x{height}"


def _select_image_size() -> str:
    size_options = (
        ("auto", "Auto"),
        ("1024x1024", "1024x1024"),
        ("1024x1536", "1024x1536"),
        ("1536x1024", "1536x1024"),
        ("2048x2048", "2048x2048 (2K 정사각형)"),
        ("2560x1440", "2560x1440 (QHD 가로)"),
        ("1440x2560", "1440x2560 (QHD 세로)"),
        ("3840x2160", "3840x2160 (4K 가로, 실험적)"),
        ("2160x3840", "2160x3840 (4K 세로, 실험적)"),
    )

    print("해상도를 선택하세요:")
    for index, (_, label) in enumerate(size_options, start=1):
        print(f"  {index}. {label}")
    custom_choice = len(size_options) + 1
    print(f"  {custom_choice}. 직접 입력")

    choice = prompt("번호 선택 (Enter=1): ").strip() or "1"
    if choice == str(custom_choice):
        return _validate_custom_size(prompt("해상도 입력 (WIDTHxHEIGHT): "))
    if not choice.isdigit() or not 1 <= int(choice) <= len(size_options):
        raise SystemExit(f"1~{custom_choice} 중 번호를 입력하거나 Enter만 누름.")
    return size_options[int(choice) - 1][0]


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
            size=cast(Any, size),
        )
    finally:
        stop.set()
        th.join(timeout=5.0)


def main() -> None:
    client, deployment = _build_client()

    user_prompt = prompt("프롬프트를 입력하세요: ").strip()
    if not user_prompt:
        raise SystemExit("프롬프트가 비어 있음.")

    image_size = _select_image_size()

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