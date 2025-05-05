# AI Crush Demos

This repository contains three main projects:

## 1. Sheets

A Google Forms processing system that automates the workflow of collecting, reviewing, and responding to form submissions.

**Key Features:**
- Fetches responses from Google Forms via Google Sheets API
- Converts responses to markdown files for easy review and commenting
- Generates and sends email responses based on your comments
- Tracks processed entries to avoid duplication

**Technologies:**
- Python with Google API integration
- OAuth2 authentication for Google services
- Markdown processing

## 2. Google App Scripts

Contains JavaScript code for Google Apps Script to automate tasks within Google Workspace applications.

**Key Features:**
- Email automation script that monitors Gmail for specific messages and sends automatic responses
- Processes unread emails containing specific keywords
- Can be set up with time-based triggers for regular execution

**Technologies:**
- Google Apps Script (JavaScript)
- Gmail API integration

## 3. Voice Data

A toolkit for collecting, processing, and sharing voice recordings for AI training or research purposes.

**Key Features:**
- Command-line interface for recording audio snippets by reading displayed text
- Professional audio recording workflow with user-friendly controls
- Tools for uploading collected data to Hugging Face datasets
- Metadata generation for each recording

**Technologies:**
- Python-based audio recording and processing
- Shell scripts for simplified usage
- Integration with Hugging Face Hub for dataset sharing

## Getting Started

Each project folder contains its own README with detailed setup and usage instructions. 