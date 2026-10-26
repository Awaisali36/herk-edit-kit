#!/usr/bin/env bash
# One-shot setup for a fresh Claude Code cloud session (or any Linux box).
# Installs the kit, HyperFrames' headless Chrome, and WhisperX for local transcription.
#
# Usage: bash scripts/cloud-setup.sh
# Model downloads need huggingface.co allowed in the environment's network policy.
set -euo pipefail

cd "$(dirname "$0")/.."

command -v ffmpeg >/dev/null || { sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg; }

npm ci
npm run setup
npx hyperframes browser ensure

python3 -c "import whisperx" 2>/dev/null || pip install -q whisperx

# Expose the kit's skills to Claude Code from any working directory.
mkdir -p ~/.claude/skills
for s in "$PWD"/.claude/skills/*; do
  ln -sfn "$s" ~/.claude/skills/"$(basename "$s")"
done

npm test
echo "Setup complete. Transcribe with: python3 scripts/transcribe-whisperx.py <media> <out.json>"
