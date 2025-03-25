# Uploading Your Voice Recordings to Hugging Face Hub

This guide explains how to use the included scripts to upload your voice recordings to Hugging Face Hub as a dataset.

## Prerequisites

1. A Hugging Face account (sign up at https://huggingface.co/join)
2. A Hugging Face API token (create one at https://huggingface.co/settings/tokens)
3. Voice recordings created with the audio_recorder.py script

## Quick Start

The simplest way to upload your recordings is to use the provided shell script:

```bash
cd voice-data
chmod +x push_to_hf.sh
./push_to_hf.sh --repo yourusername/dataset-name --token YOUR_HF_TOKEN
```

Replace `yourusername/dataset-name` with your desired repository path and `YOUR_HF_TOKEN` with your Hugging Face API token.

## Options

The upload script supports the following options:

- `--repo` or `-r`: Hugging Face repository ID (username/repo-name)
  - Example: `yourusername/voice-dataset`
  - If not provided, a default name with timestamp will be used
  
- `--token` or `-t`: Hugging Face API token
  - You can also set this as an environment variable: `export HF_TOKEN=your_token`

- `--private` or `-p`: Make the repository private
  - By default, repositories are public

- `--help` or `-h`: Show help message

## Example Usage

### Basic upload:

```bash
./push_to_hf.sh --repo yourusername/my-voice-dataset --token YOUR_HF_TOKEN
```

### Make repository private:

```bash
./push_to_hf.sh --repo yourusername/my-private-dataset --token YOUR_HF_TOKEN --private
```

### Using environment variable for token:

```bash
export HF_TOKEN=your_token
./push_to_hf.sh --repo yourusername/my-voice-dataset
```

## What Gets Uploaded

The script uploads:

1. All WAV audio files from your recordings directory
2. A metadata file (data.parquet) containing text, audio paths, and other information
3. A README.md file describing the dataset

## Accessing Your Dataset

Once uploaded, your dataset will be available at:
`https://huggingface.co/datasets/yourusername/dataset-name`

You can load it in Python using:

```python
from datasets import load_dataset

dataset = load_dataset("yourusername/dataset-name")
```

## Troubleshooting

- If you encounter permission errors, make sure your API token has write access
- If files fail to upload, check your internet connection
- For other issues, check the error messages displayed by the script 