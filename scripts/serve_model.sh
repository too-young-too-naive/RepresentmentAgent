#!/bin/bash
#SBATCH --job-name=vllm-serve
#SBATCH --gpus=1
#SBATCH --cpus-per-gpu=16
#SBATCH --mem=128G
#SBATCH --time=08:00:00
#SBATCH --output=logs/vllm-%j.out
#SBATCH --error=logs/vllm-%j.err

# ── Configuration ──────────────────────────────────────────────
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen3.5-27B}"
PORT="${PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"
# Set your HuggingFace token for gated models (Llama, etc.)
# export HF_TOKEN="hf_your_token_here"
# ───────────────────────────────────────────────────────────────

mkdir -p logs

echo "============================================"
echo "  vLLM Model Server"
echo "============================================"
echo "Job ID:      $SLURM_JOB_ID"
echo "Node:        $(hostname)"
echo "GPUs:        $SLURM_GPUS_ON_NODE"
echo "Model:       $MODEL_NAME"
echo "Port:        $PORT"
echo "Started at:  $(date)"
echo "============================================"

# Print the connection info for the user
NODE_HOSTNAME=$(hostname)
echo ""
echo ">>> Once the server is ready, connect from your local machine:"
echo ">>>   ssh -L ${PORT}:${NODE_HOSTNAME}:${PORT} <login-node>"
echo ""
echo ">>> Then set in backend/.env:"
echo ">>>   LLM_BASE_URL=http://localhost:${PORT}/v1"
echo ">>>   LLM_MODEL_NAME=${MODEL_NAME}"
echo ">>>   LLM_API_KEY=dummy-key"
echo ""

pip install vllm --quiet 2>&1 | tail -3

echo "Starting vLLM server..."
python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --port "$PORT" \
    --max-model-len "$MAX_MODEL_LEN" \
    --trust-remote-code \
    --enable-auto-tool-choice \
    --tool-call-parser hermes
