import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import NotFoundError, OpenAI
from openai.types.video import Video
from openai.types.video_seconds import VideoSeconds
from openai.types.video_size import VideoSize
from prompt_toolkit.shortcuts import prompt

MODEL: Literal["sora-2"] = "sora-2"
POLL_INTERVAL_SECONDS = 10.0


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"{name} 환경 변수가 비어 있음.")
    return value


def _build_client() -> OpenAI:
    load_dotenv(dotenv_path=Path.cwd() / ".env")

    endpoint = _required_env("AZURE_OPENAI_ENDPOINT")
    api_key = _required_env("AZURE_OPENAI_API_KEY")
    base_url = endpoint.rstrip("/")
    if not base_url.endswith("/openai/v1"):
        base_url = f"{base_url}/openai/v1"

    return OpenAI(
        api_key=api_key,
        base_url=f"{base_url}/",
    )


def _clear_progress_line() -> None:
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()


def _wait_for_video(client: OpenAI, video: Video) -> Video:
    started_at = time.perf_counter()

    while video.status in {"queued", "in_progress"}:
        elapsed_sec = time.perf_counter() - started_at
        status_text = "대기 중" if video.status == "queued" else "생성 중"
        sys.stdout.write(
            f"\r{status_text}... {video.progress:3d}% (경과 {elapsed_sec:.1f}초)"
        )
        sys.stdout.flush()
        time.sleep(POLL_INTERVAL_SECONDS)
        video = client.videos.retrieve(video.id)

    _clear_progress_line()

    if video.status == "failed":
        if video.error:
            raise SystemExit(
                f"비디오 생성 실패 ({video.error.code}): {video.error.message}"
            )
        raise SystemExit("비디오 생성 실패. API 응답을 확인함.")

    if video.status != "completed":
        raise SystemExit(f"예상하지 못한 비디오 상태: {video.status}")

    return video


def main() -> None:
    client = _build_client()

    user_prompt = prompt("프롬프트를 입력하세요: ").strip()
    if not user_prompt:
        raise SystemExit("프롬프트가 비어 있음.")

    print("해상도를 선택하세요:")
    print("  1. 720x1280 (세로, 기본)")
    print("  2. 1280x720 (가로)")
    size_map: dict[str, VideoSize] = {
        "1": "720x1280",
        "2": "1280x720",
    }
    size_choice = prompt("번호 선택 (Enter=1): ").strip() or "1"
    if size_choice not in size_map:
        raise SystemExit("1~2 중 번호를 입력하거나 Enter만 누름.")
    video_size = size_map[size_choice]

    print("길이를 선택하세요:")
    print("  1. 4초 (기본)")
    print("  2. 8초")
    print("  3. 12초")
    seconds_map: dict[str, VideoSeconds] = {
        "1": "4",
        "2": "8",
        "3": "12",
    }
    seconds_choice = prompt("번호 선택 (Enter=1): ").strip() or "1"
    if seconds_choice not in seconds_map:
        raise SystemExit("1~3 중 번호를 입력하거나 Enter만 누름.")
    video_seconds = seconds_map[seconds_choice]

    total_started_at = time.perf_counter()
    try:
        video = client.videos.create(
            model=MODEL,
            prompt=user_prompt,
            size=video_size,
            seconds=video_seconds,
        )
    except NotFoundError:
        raise SystemExit(
            "Azure Sora Videos API를 찾을 수 없음. AZURE_OPENAI_ENDPOINT와 "
            "Sora 2 배포 이름이 'sora-2'인지 확인함."
        ) from None
    print(f"생성 작업 시작: {video.id}")

    video = _wait_for_video(client, video)

    out_dir = Path.cwd() / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = datetime.now().strftime("video_%Y%m%d_%H%M%S")
    out_path = out_dir / f"{stem}.mp4"

    print("비디오 다운로드 중...")
    with client.videos.with_streaming_response.download_content(video.id) as response:
        response.stream_to_file(out_path)

    elapsed_sec = time.perf_counter() - total_started_at
    print(f"생성완료: {out_path} (소요 {elapsed_sec:.1f}초)")


if __name__ == "__main__":
    main()