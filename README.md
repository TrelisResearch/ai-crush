# QR Code Generator

A simple Python program to convert a URL into a QR code and display it.

## Features

- Generates a QR code from a URL
- Saves the QR code as an image file
- Displays the QR code using matplotlib

## Requirements

- Python 3.6+
- Required packages (see requirements.txt):
  - qrcode
  - pillow (PIL)
  - matplotlib

## Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:

```bash
python qr_code_generator.py
```

2. The script will:
   - Generate a QR code for the URL: https://forms.gle/JH1KHPFprntnErsL9
   - Save the QR code as qrcode.png in the current directory
   - Display the QR code in a new window

## Customization

To generate a QR code for a different URL, edit the `url` variable in the `main()` function of the `qr_code_generator.py` file.

```python
def main():
    # Change this URL to generate a different QR code
    url = "https://forms.gle/JH1KHPFprntnErsL9"
    ...
``` 