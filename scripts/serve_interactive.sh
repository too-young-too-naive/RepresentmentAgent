#!/bin/bash
# Quick interactive session to test the model server.
# Run this on the login node — it grabs a GPU and starts vLLM.
#
# Usage:
#   ./scripts/serve_interactive.sh                          # defaults
#   MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3 ./scripts/serve_interactive.sh

MODEL_NAME="${MODEL_NAME:-meta-llama/Llama-3.1-70B-Instruct}"
PORT="${PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"

echo "Requesting 1 GPU for interactive vLLM session..."
echo "Model: $MODEL_NAME"
echo ""

srun --gpus=1 --cpus-per-gpu=16 --mem=128G --time=02:00:00 --pty bash -c "
    echo 'Node: \$(hostname)'
    echo 'Setting up vLLM...'
    pip install vllm --quiet 2>&1 | tail -3

    echo ''
    echo '>>> SSH tunnel from your local machine:'
    echo '>>>   ssh -L ${PORT}:\$(hostname):${PORT} <login-node>'
    echo ''

    python -m vllm.entrypoints.openai.api_server \
        --model ${MODEL_NAME} \
        --port ${PORT} \
        --max-model-len ${MAX_MODEL_LEN} \
        --trust-remote-code \
        --enable-auto-tool-choice \
        --tool-call-parser hermes
"
