#!/usr/bin/env bash
set -euo pipefail
printf '\n[1] Sistema e Python\n'
uname -srm
python3 --version
printf '\n[2] Runner GitHub (processos)\n'
pgrep -af 'Runner.Listener|Runner.Worker' || true
printf '\n[3] Ollama API\n'
curl --fail --silent --show-error http://127.0.0.1:11434/api/tags | python3 -m json.tool | sed -n '1,70p'
printf '\n[4] Modelo instalado\n'
ollama show qwen2.5-coder:3b-instruct > /dev/null && echo 'OK: qwen2.5-coder:3b-instruct'
