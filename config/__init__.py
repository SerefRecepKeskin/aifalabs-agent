import json
import os
import sys
from pathlib import Path

from addict import Dict

# First try to get config from environment
raw_config = os.getenv('CONFIG_FILE')
if raw_config:
    try:
        config = json.loads(raw_config)
    except json.JSONDecodeError:
        print("Error: CONFIG_FILE environment variable contains invalid JSON")
        sys.exit(1)
# Fallback to default config if no environment variable
else:
    default_path = Path(__file__).parent / 'default.json'
    try:
        with open(default_path, encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: No configuration found. Set CONFIG_FILE environment variable or ensure {default_path} exists")
        sys.exit(1)

config = Dict(config)
