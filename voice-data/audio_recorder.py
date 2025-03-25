import os
import sys
import json
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import colorama
from colorama import Fore, Style, Back
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress
from datetime import datetime

# Initialize colorama
colorama.init()

# Initialize Rich console
console = Console()

class AudioRecorder:
    def __init__(self):
        self.samplerate = 44100
        self.channels = 1
        self.frames = []
        self.recording = False
        self.recording_thread = None
        self.repo_path = os.path.join(os.getcwd(), "voice-data", "recordings")
        self.snippets = []
        self.current_snippet = None
        self.selected_device = None
        self.available_devices = []

        # Create directory if it doesn't exist
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
            
    def list_devices(self):
        """List all available audio input devices."""
        self.available_devices = []
        console.print("\n[bold cyan]Available Audio Input Devices:[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Device Name")
        table.add_column("Channels", justify="right")
        table.add_column("Sample Rate", justify="right")
        
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:  # if it has input channels
                self.available_devices.append((i, device))
                table.add_row(
                    str(len(self.available_devices) - 1), 
                    device['name'], 
                    str(int(device['max_input_channels'])),
                    str(int(device['default_samplerate']))
                )
        
        console.print(table)
        
        if not self.available_devices:
            console.print("[bold red]No audio input devices found![/bold red]")
            sys.exit(1)
            
        return self.available_devices

    def select_device(self):
        """Allow user to select an audio input device."""
        devices = self.list_devices()
        if len(devices) == 1:
            self.selected_device = devices[0][0]
            console.print(f"\n[green]Auto-selected the only available device: {devices[0][1]['name']}[/green]")
            return
            
        while True:
            try:
                selection = Prompt.ask(
                    "\n[bold cyan]Select audio device by number[/bold cyan]", 
                    default="0"
                )
                idx = int(selection)
                if 0 <= idx < len(devices):
                    self.selected_device = devices[idx][0]
                    console.print(f"\n[green]Selected device: {devices[idx][1]['name']}[/green]")
                    # Update sample rate to device's default
                    self.samplerate = int(devices[idx][1]['default_samplerate'])
                    break
                else:
                    console.print("[bold red]Invalid selection. Please try again.[/bold red]")
            except ValueError:
                console.print("[bold red]Please enter a number.[/bold red]")

    def start_recording(self):
        """Start recording audio."""
        self.frames = []
        self.recording = True
        
        # Create a new thread to record audio
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()
        
        # Display recording indicator
        console.print(f"\n{Back.RED}{Fore.WHITE} RECORDING {Style.RESET_ALL} Press Enter to stop...")

    def _record(self):
        """Record audio in a separate thread."""
        def callback(indata, frames, time, status):
            if status:
                console.print(f"[bold red]Status: {status}[/bold red]")
            self.frames.append(indata.copy())
            
        with sd.InputStream(
            samplerate=self.samplerate,
            device=self.selected_device,
            channels=self.channels,
            callback=callback
        ):
            while self.recording:
                sd.sleep(100)  # Small sleep to reduce CPU usage

    def stop_recording(self):
        """Stop recording audio."""
        self.recording = False
        if self.recording_thread:
            self.recording_thread.join()
        console.print(f"\n[green]Recording stopped.[/green]")
        
        # Calculate duration
        if self.frames:
            duration = len(self.frames) * 100 / 1000  # 100ms per callback
            console.print(f"[bold cyan]Recorded approximately {duration:.2f} seconds of audio[/bold cyan]")
        
        return True

    def save_recording(self, text_snippet):
        """Save the recorded audio and metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snippet_{timestamp}"
        audio_path = os.path.join(self.repo_path, f"{filename}.wav")
        json_path = os.path.join(self.repo_path, f"{filename}.json")
        
        if not self.frames:
            console.print("[bold red]No audio data to save![/bold red]")
            return None, None
            
        # Combine all frames
        audio_data = np.concatenate(self.frames, axis=0)
        
        # Save audio file
        sf.write(audio_path, audio_data, self.samplerate)
        
        # Calculate audio features - simple averaging of amplitudes
        # Take every 1000th sample (or fewer if less data) for a compact representation
        step = max(1, len(audio_data) // 1000)
        compact_feature = audio_data[::step].flatten().tolist()
        
        # Save metadata
        metadata = {
            "text": text_snippet,
            "timestamp": timestamp,
            "duration": len(audio_data) / self.samplerate,
            "sample_rate": self.samplerate,
            "audio_file": f"{filename}.wav",
            "audio_feature": compact_feature[:1000]  # Limit size for JSON
        }
        
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        console.print(f"[green]Saved audio to:[/green] {audio_path}")
        console.print(f"[green]Saved metadata to:[/green] {json_path}")
        
        return audio_path, json_path

    def load_snippets(self, file_path=None):
        """Load text snippets from a file or use examples."""
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    snippets = [line.strip() for line in f.readlines() if line.strip()]
                console.print(f"[green]Loaded {len(snippets)} snippets from {file_path}[/green]")
                self.snippets = snippets
                return snippets
            except Exception as e:
                console.print(f"[bold red]Error loading snippets from file: {e}[/bold red]")
        
        # Default snippets if no file provided or error
        example_snippets = [
            "Can you please tell me how to get to the train station?",
            "I would like a cup of coffee with milk and sugar.",
            "I'm planning to go on vacation next month to Spain.",
            "The latest advancements in artificial intelligence are remarkable.",
            "Could you recommend a good book to read this weekend?",
            "I need to schedule a meeting with the team for next week.",
            "What's the weather forecast for tomorrow?",
            "The concert last night was amazing, the band played all my favorite songs."
        ]
        
        self.snippets = example_snippets
        return example_snippets

    def display_snippet(self, index):
        """Display a text snippet for recording."""
        if index < len(self.snippets):
            self.current_snippet = self.snippets[index]
            console.print(Panel(
                f"[bold white]{self.current_snippet}[/bold white]",
                title=f"Snippet {index+1}/{len(self.snippets)}",
                title_align="left",
                border_style="cyan"
            ))
            return self.current_snippet
        return None

    def cleanup(self):
        """Clean up resources."""
        colorama.deinit()
        console.print("\n[bold green]Recording session completed. Thank you![/bold green]")

def main():
    console.print(Panel(
        "[bold cyan]Voice Recording Interface[/bold cyan]\n\n"
        "This tool allows you to record audio snippets by reading displayed text.\n"
        "Each snippet will be saved along with its text and features.",
        title="🎙️ Audio Recorder",
        border_style="yellow"
    ))
    
    recorder = AudioRecorder()
    
    try:
        # Select audio device
        recorder.select_device()
        
        # Check for snippets file
        snippets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snippets.txt")
        
        # Load snippets
        snippets = recorder.load_snippets(snippets_file)
        console.print(f"\n[bold cyan]Loaded {len(snippets)} text snippets for recording[/bold cyan]")
        
        # Record each snippet
        for i in range(len(snippets)):
            snippet_text = recorder.display_snippet(i)
            
            console.print("\n[bold yellow]Press Enter to START recording...[/bold yellow]")
            input()
            
            recorder.start_recording()
            
            # Wait for user to press Enter to stop recording
            input()
            
            recorder.stop_recording()
            
            # Save the recording
            audio_path, json_path = recorder.save_recording(snippet_text)
            
            # Ask if user wants to continue
            if i < len(snippets) - 1:
                continue_recording = Prompt.ask(
                    "\n[bold cyan]Continue to next snippet?[/bold cyan]", 
                    choices=["y", "n"], 
                    default="y"
                )
                if continue_recording.lower() != "y":
                    break
        
        recorder.cleanup()
        
    except KeyboardInterrupt:
        console.print("\n[bold red]Recording session interrupted.[/bold red]")
        recorder.cleanup()
        
if __name__ == "__main__":
    main() 