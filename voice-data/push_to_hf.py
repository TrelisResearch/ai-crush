import os
import json
import argparse
import glob
from pathlib import Path
from datetime import datetime
import pandas as pd
from huggingface_hub import HfApi
from tqdm import tqdm
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def create_metadata(recordings_dir):
    """Create metadata from recordings and their JSON files."""
    console.print("[bold cyan]Creating dataset metadata...[/bold cyan]")
    
    all_data = []
    wav_files = glob.glob(os.path.join(recordings_dir, "*.wav"))
    
    for wav_file in tqdm(wav_files):
        base_name = os.path.splitext(os.path.basename(wav_file))[0]
        json_file = os.path.join(recordings_dir, f"{base_name}.json")
        
        if not os.path.exists(json_file):
            console.print(f"[yellow]Warning: No JSON file found for {base_name}.wav. Skipping.[/yellow]")
            continue
            
        with open(json_file, 'r') as f:
            try:
                metadata = json.load(f)
                entry = {
                    "text": metadata["text"],
                    "audio": {"path": os.path.basename(wav_file)},
                    "source": "recording",
                    "timestamp": metadata["timestamp"]
                }
                all_data.append(entry)
            except json.JSONDecodeError:
                console.print(f"[yellow]Warning: Invalid JSON in {json_file}. Skipping.[/yellow]")
                continue
    
    return all_data

def push_to_huggingface(recordings_dir, repo_id, token=None, private=False):
    """Push recordings to Hugging Face Hub as a dataset."""
    # Initialize HF API
    api = HfApi(token=token)
    repo_url = f"https://huggingface.co/datasets/{repo_id}"
    
    console.print(Panel(
        f"[bold cyan]Pushing Voice Recordings to Hugging Face Hub[/bold cyan]\n\n"
        f"Repository: [green]{repo_id}[/green]\n"
        f"URL: [blue]{repo_url}[/blue]",
        title="🤗 Hugging Face Upload",
        border_style="yellow"
    ))
    
    # Create metadata
    metadata = create_metadata(recordings_dir)
    
    if not metadata:
        console.print("[bold red]Error: No valid recordings found to upload![/bold red]")
        return
    
    console.print(f"[green]Found {len(metadata)} recordings to upload.[/green]")
    
    # Create a temporary directory for organizing files
    temp_dir = os.path.join(recordings_dir, "hf_upload")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create dataset parquet file
    df = pd.DataFrame(metadata)
    parquet_path = os.path.join(temp_dir, "data.parquet")
    df.to_parquet(parquet_path, index=False)
    
    # Create README with dataset card information
    readme_content = f"""---
language: en
license: mit
pretty_name: Voice Recordings Dataset
task_categories:
- audio-classification
task_ids:
- audio-classification
---

# Voice Recordings Dataset

This dataset contains voice recordings created using the Audio Recorder tool.

## Dataset Description

- **Created**: {datetime.now().strftime('%Y-%m-%d')}
- **Number of samples**: {len(metadata)}
- **Languages**: English
- **Format**: WAV audio files with text transcriptions

## Dataset Structure

Each sample contains:
- `text`: The text that was read aloud
- `audio`: Path to the audio file
- `source`: Source of the recording 
- `timestamp`: When the recording was made

## Usage

This dataset can be loaded using the Hugging Face Datasets library:

```python
from datasets import load_dataset

dataset = load_dataset("{repo_id}")
```
"""
    
    # Write README to a file
    card_path = os.path.join(temp_dir, "README.md")
    with open(card_path, "w") as f:
        f.write(readme_content)
    
    # Push to Hugging Face
    console.print("[bold cyan]Pushing files to Hugging Face Hub...[/bold cyan]")
    
    try:
        # Check if repository exists, if not create it
        try:
            api.repo_info(repo_id=repo_id, repo_type="dataset")
            console.print("[green]Repository already exists. Updating...[/green]")
        except Exception:
            console.print("[yellow]Repository doesn't exist. Creating new repository...[/yellow]")
            api.create_repo(repo_id=repo_id, repo_type="dataset", private=private)
        
        # Upload dataset card
        api.upload_file(
            path_or_fileobj=card_path,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset"
        )
        
        # Upload parquet file
        api.upload_file(
            path_or_fileobj=parquet_path,
            path_in_repo="data.parquet",
            repo_id=repo_id,
            repo_type="dataset"
        )
        
        # Upload all WAV files
        audio_files = glob.glob(os.path.join(recordings_dir, "*.wav"))
        for audio_file in tqdm(audio_files, desc="Uploading audio files"):
            audio_filename = os.path.basename(audio_file)
            api.upload_file(
                path_or_fileobj=audio_file,
                path_in_repo=audio_filename,
                repo_id=repo_id,
                repo_type="dataset"
            )
        
        console.print(f"[bold green]Successfully pushed dataset to {repo_url}[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error during upload: {str(e)}[/bold red]")
    finally:
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="Push voice recordings to Hugging Face Hub")
    parser.add_argument("--dir", type=str, default="recordings", help="Directory containing recordings")
    parser.add_argument("--repo", type=str, required=True, help="Hugging Face repository ID (username/repo-name)")
    parser.add_argument("--token", type=str, help="Hugging Face API token")
    parser.add_argument("--private", action="store_true", help="Make the repository private")
    
    args = parser.parse_args()
    
    # Get recordings directory
    if os.path.isabs(args.dir):
        recordings_dir = args.dir
    else:
        # Default to "recordings" in the current voice-data directory
        voice_data_dir = os.path.dirname(os.path.abspath(__file__))
        recordings_dir = os.path.join(voice_data_dir, args.dir)
    
    if not os.path.exists(recordings_dir):
        console.print(f"[bold red]Error: Recordings directory '{recordings_dir}' not found![/bold red]")
        return
    
    # Check if token is provided or in environment
    token = args.token
    if not token:
        token = os.environ.get("HF_TOKEN")
        if not token:
            console.print("[yellow]Warning: No Hugging Face token provided. Using anonymous access.[/yellow]")
            console.print("[yellow]To set a token, use --token or set the HF_TOKEN environment variable.[/yellow]")
    
    # Push to Hugging Face
    push_to_huggingface(recordings_dir, args.repo, token, args.private)

if __name__ == "__main__":
    main() 