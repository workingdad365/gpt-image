# gpt-image / gpt-video

Azure OpenAI 이미지 및 비디오 생성 API를 터미널에서 실행하는 CLI 도구다.

- `gpt-image`: 이미지 생성
- `gpt-video`: `sora-2` 비디오 생성, 작업 상태 확인 및 MP4 다운로드

## 요구 사항

- Python 3.13 이상
- uv
- Azure OpenAI 이미지 및 비디오 생성 권한

## 환경 변수 설정

`gpt-image`는 프로세스 환경변수를 사용한다. `gpt-video`는 실행 위치의 `.env`를 먼저 읽으며, 이미 설정된 프로세스 환경변수는 덮어쓰지 않는다.

`.env` 예시:

```dotenv
AZURE_OPENAI_API_KEY=YOUR_AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT=YOUR_AZURE_OPENAI_ENDPOINT
OPENAI_API_VERSION=YOUR_OPENAI_API_VERSION
DEPLOYMENT_NAME=YOUR_IMAGE_DEPLOYMENT_NAME
```

`OPENAI_API_VERSION`과 `DEPLOYMENT_NAME`은 `gpt-image`에서만 사용한다. `gpt-video`는 Azure OpenAI v1 API를 사용하므로 API 버전이 필요하지 않으며, 모델명은 환경변수와 무관하게 `sora-2`로 고정된다. Azure 리소스에도 배포 이름이 `sora-2`인 Sora 2 모델이 있어야 한다.

전역 설치된 `gpt-image` 명령은 실행 위치와 무관하게 동작해야 하므로, 이미지 도구 설정값은 사용자 환경 변수나 시스템 환경 변수로 관리한다.

PowerShell 예시:

```powershell
[Environment]::SetEnvironmentVariable("AZURE_OPENAI_API_KEY", "YOUR_AZURE_OPENAI_API_KEY", "User")
[Environment]::SetEnvironmentVariable("AZURE_OPENAI_ENDPOINT", "YOUR_AZURE_OPENAI_ENDPOINT", "User")
[Environment]::SetEnvironmentVariable("OPENAI_API_VERSION", "YOUR_OPENAI_API_VERSION", "User")
[Environment]::SetEnvironmentVariable("DEPLOYMENT_NAME", "YOUR_DEPLOYMENT_NAME", "User")
```

환경 변수를 등록한 뒤에는 새 PowerShell을 열어야 반영된다.

Linux 셸 설정 예시:

```sh
cat <<'EOF' >> ~/.bashrc
export AZURE_OPENAI_API_KEY="YOUR_AZURE_OPENAI_API_KEY"
export AZURE_OPENAI_ENDPOINT="YOUR_AZURE_OPENAI_ENDPOINT"
export OPENAI_API_VERSION="YOUR_OPENAI_API_VERSION"
export DEPLOYMENT_NAME="YOUR_DEPLOYMENT_NAME"
EOF
```

Zsh를 사용한다면 `~/.bashrc` 대신 `~/.zshrc`에 추가한다. 설정을 추가한 뒤에는 새 터미널을 열거나 다음 명령으로 현재 셸에 반영한다.

```sh
source ~/.bashrc
```

현재 터미널에서만 임시로 사용할 경우:

```powershell
$env:AZURE_OPENAI_API_KEY = "YOUR_AZURE_OPENAI_API_KEY"
$env:AZURE_OPENAI_ENDPOINT = "YOUR_AZURE_OPENAI_ENDPOINT"
$env:OPENAI_API_VERSION = "YOUR_OPENAI_API_VERSION"
$env:DEPLOYMENT_NAME = "YOUR_DEPLOYMENT_NAME"
```

## 전역 설치

프로젝트 루트에서 다음 명령을 실행한다.

```powershell
uv tool install .
```

개발 중인 로컬 파일 변경을 설치된 명령에 바로 반영하려면 editable 모드로 설치한다.

```powershell
uv tool install --editable .
```

`gpt-image` 명령을 찾지 못하면 uv tool 경로를 셸에 추가한다.

```powershell
uv tool update-shell
```

그 뒤 PowerShell을 새로 열고 실행한다.

```powershell
gpt-image
gpt-video
```

생성된 이미지와 비디오는 명령을 실행한 현재 디렉터리의 `output/` 폴더에 저장된다.

## 로컬 실행

설치하지 않고 프로젝트 안에서 실행할 수도 있다.

```powershell
uv run gpt-image
uv run gpt-video
```

비디오 생성은 비동기 작업으로 실행된다. `gpt-video`는 완료될 때까지 상태를 확인한 뒤 MP4 파일을 자동으로 다운로드한다.

Sora 2 모델과 Videos API는 2026년 9월 24일 종료 예정이다.

