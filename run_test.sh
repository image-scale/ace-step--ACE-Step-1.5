#!/usr/bin/env bash
set -eo pipefail

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export CI=true

cd /workspace/ACE-Step-1.5

rm -rf .pytest_cache __pycache__

# Run unittest discovery for both naming patterns (-v for verbose output)
# Combine both patterns by running sequentially; capture exit codes separately
# so one failing pattern doesn't prevent the other from running.
EXIT_CODE=0
python -m unittest discover -s . -p "*_test.py" -v 2>&1 || EXIT_CODE=$?
python -m unittest discover -s . -p "test_*.py" -v 2>&1 || { code=$?; [ $code -gt $EXIT_CODE ] && EXIT_CODE=$code; }
exit $EXIT_CODE

