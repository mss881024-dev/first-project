#!/usr/bin/env bash
# 취소표 대시보드 실행 스크립트
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY 환경변수를 먼저 설정해 주세요."
  echo "  export ANTHROPIC_API_KEY=sk-ant-..."
  exit 1
fi

# 가상환경 생성 (최초 1회)
if [ ! -d ".venv" ]; then
  echo "▶ 가상환경 생성 중..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# 패키지 설치
pip install -q -r requirements.txt

echo ""
echo "✅ 대시보드 시작: http://localhost:8765"
echo "   종료: Ctrl+C"
echo ""

uvicorn server:app --host 0.0.0.0 --port 8765 --reload
