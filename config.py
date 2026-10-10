"""Fixed configuration. Change a value here, and the run config changes with it."""
import os

# Models (LiteLLM names). The agent runs on a local Ollama model.
AGENT_MODEL = os.environ.get("AGENT_MODEL", "ollama_chat/llama3.2:3b")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gemini/gemini-3.5-flash-lite")
SIM_USER_MODEL = os.environ.get("SIM_USER_MODEL", AGENT_MODEL)

# Agent run settings. These stay fixed for every version, so runs compare fairly.
TEMPERATURE = 0.5
MAX_TOKENS = 512
MAX_STEPS = 15          # maximum model calls in one trial
NUM_CTX = 8192          # Ollama context window
N_TRIALS = 4            # trials per task (the brief requires 4 or more)
WORKERS = int(os.environ.get("WORKERS", "2"))

# Notional price in USD per 1M tokens. The local model costs nothing.
# These numbers let us compute "cost per success". They are NOT real invoices.
NOTIONAL_PRICE_IN = 1.00
NOTIONAL_PRICE_OUT = 5.00

# The fixed "today" for the store world.
TODAY = "2026-10-01"

# Gate settings (see docs/gate.md).
CATEGORY_REGRESSION_LIMIT = 0.10   # a category may not lose more than 10 points

# Judge settings. The free API tier has request limits, so calls are spaced out.
JUDGE_MIN_INTERVAL = float(os.environ.get("JUDGE_MIN_INTERVAL", "4.0"))   # seconds between calls
JUDGE_PROMPT_VERSION = "j1"
