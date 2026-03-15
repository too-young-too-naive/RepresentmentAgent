#!/bin/bash
# Quick interactive session to test the model server.
# Run this on the login node — it grabs a GPU and starts vLLM.
#
# Usage:
#   ./scripts/serve_interactive.sh                          # defaults
#   MODEL_NAME=Qwen/Qwen3.5-27B ./scripts/serve_interactive.sh

MODEL_NAME="${MODEL_NAME:-Qwen/Qwen3.5-27B}"
PORT="${PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"
TIME="${TIME:-00:30:00}"

echo "Requesting 1 GPU for interactive vLLM session..."
echo "Model: $MODEL_NAME"
echo "Time:  $TIME"
echo ""

srun --gpus=1 --cpus-per-gpu=16 --mem=128G --time="$TIME" --pty bash <<EOF
    NODE=\$(hostname)
    echo "Node: \$NODE"
    echo "Setting up vLLM..."
    pip3 install vllm --quiet 2>&1 | tail -3

    echo ""
    echo ">>> SSH tunnel from your local machine:"
    echo ">>>   ssh -L ${PORT}:\${NODE}:${PORT} <login-node>"
    echo ""

    python3 -m vllm.entrypoints.openai.api_server \
        --model ${MODEL_NAME} \
        --port ${PORT} \
        --max-model-len ${MAX_MODEL_LEN} \
        --trust-remote-code \
        --enable-auto-tool-choice \
        --tool-call-parser hermes
EOF
