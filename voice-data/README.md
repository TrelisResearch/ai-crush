# Voice Recording Interface

An elegant command-line interface for recording audio snippets by reading text shown on screen.

## Features

- Select which audio input device to use for recording
- Display text snippets to read aloud
- Start/stop recording with the Enter key
- Save recordings with metadata and text
- Beautiful command-line interface with colorful feedback

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Install dependencies using `uv`:

```bash
cd voice-data
uv pip install -r requirements.txt
```

## Usage

There are two ways to run the script:

### 1. Using the shell script (recommended)

```bash
cd voice-data
chmod +x record.sh
./record.sh
```

### 2. Running the Python script directly

```bash
cd voice-data
uv run audio_recorder.py
```

### Recording Process

1. Select an audio input device from the list
2. For each text snippet:
   - The snippet will be displayed in a panel
   - Press Enter to start recording
   - Read the text aloud
   - Press Enter again to stop recording
   - The recording will be saved with metadata
   - Choose whether to continue to the next snippet

## Output

Recordings are saved in the `voice-data/recordings` directory with:
- `.wav` file containing the audio
- `.json` file containing metadata (text, timestamp, duration, etc.)

## Customizing the Snippets

The default snippets are loaded from `snippets.txt`. You can modify this file to add your own text snippets. Each line in the file will be treated as a separate snippet.

## Audio Feature Generation

The script automatically extracts simple audio features from the recording and stores them in the JSON metadata file. These features can be used for machine learning or other analysis purposes.

## Implementation Details

The application uses:
- `sounddevice` for audio recording
- `soundfile` for saving audio in WAV format
- `rich` for the beautiful command-line interface
- `numpy` for audio data processing 