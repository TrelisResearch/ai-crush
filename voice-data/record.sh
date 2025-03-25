#!/bin/bash

# Navigate to the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed. Please install it first."
    echo "Visit: https://github.com/astral-sh/uv for installation instructions."
    exit 1
fi

# Check if requirements are installed, install if not
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment and installing dependencies..."
    uv venv
    uv pip install -r requirements.txt
fi

# Run the audio recorder
echo "Starting Audio Recorder..."
uv run audio_recorder.py

# Exit with the exit code of the Python script
exit $? 