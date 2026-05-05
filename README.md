# gpt-image

Azure OpenAI 이미지 생성 API를 터미널에서 실행하는 CLI 도구다.

## 요구 사항

- Python 3.12 이상
- uv
- Azure OpenAI 이미지 생성 배포

## 환경 변수 설정

이 도구는 `.env` 파일을 읽지 않는다. 전역 설치된 `gpt-image` 명령은 실행 위치와 무관하게 동작해야 하므로, 설정값을 사용자 환경 변수나 시스템 환경 변수로 관리한다.

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
```

생성된 이미지는 명령을 실행한 현재 디렉터리의 `output/` 폴더에 저장된다.

## 로컬 실행

설치하지 않고 프로젝트 안에서 실행할 수도 있다.

```powershell
uv run gpt-image
```

