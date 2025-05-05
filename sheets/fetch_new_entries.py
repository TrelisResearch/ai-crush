#!/usr/bin/env python3
import os
import sys
import json
import csv
import io
import hashlib
import argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Set up constants
SPREADSHEET_ID = '1FmBo8Ceq7sr01lHrpblOBEUf5_aogeMWcJDYnX7Hi0Q'
RANGE_NAME = 'Form Responses 1'  # Fixed to match the actual sheet name with spaces
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
PROCESSED_FILE = 'processed_entries.json'
OUTPUT_DIR = 'markdown_files'
TOKEN_FILE = 'token.json'

def setup_sheets_api():
    """Set up and return the Google Sheets API client using OAuth."""
    creds = None
    # The token.json file stores the user's access and refresh tokens
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_info(
            json.load(open(TOKEN_FILE)), SCOPES)
    
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if credentials.json exists
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json file not found!")
                print("Please download OAuth 2.0 Client ID credentials from the Google Cloud Console")
                print("and save them as credentials.json in the current directory.")
                sys.exit(1)
                
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('sheets', 'v4', credentials=creds, cache_discovery=False)

def get_sheet_data():
    """Retrieve data from Google Sheets."""
    try:
        print(f"Attempting to access spreadsheet with ID: {SPREADSHEET_ID}")
        print(f"Using range: {RANGE_NAME}")
        
        service = setup_sheets_api()
        sheet = service.spreadsheets()
        
        # First try to get metadata about the spreadsheet
        try:
            metadata = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
            print(f"Successfully accessed spreadsheet: {metadata.get('properties', {}).get('title', 'Unknown')}")
            print(f"Available sheets: {[s.get('properties', {}).get('title', 'Unknown') for s in metadata.get('sheets', [])]}")
        except Exception as e:
            print(f"Error accessing spreadsheet metadata: {e}")
        
        # Now try to get the actual data
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                   range=RANGE_NAME).execute()
        values = result.get('values', [])
        
        if not values:
            print('No data found.')
            return []
            
        print(f"Successfully retrieved {len(values)-1} rows of data")
        
        # Convert to list of dictionaries
        headers = values[0]
        data = []
        
        for row in values[1:]:
            # Create a dictionary for each row
            row_dict = {}
            for i, header in enumerate(headers):
                row_dict[header] = row[i] if i < len(row) else ""
            data.append(row_dict)
            
        return data
    except Exception as e:
        print(f"Error retrieving sheet data: {e}")
        return []

def get_processed_entries():
    """Get list of already processed entry IDs."""
    if not os.path.exists(PROCESSED_FILE):
        return []
    
    try:
        with open(PROCESSED_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading processed entries file: {e}")
        return []

def save_processed_entries(processed_entries):
    """Save the list of processed entry IDs."""
    try:
        with open(PROCESSED_FILE, 'w') as f:
            json.dump(processed_entries, f)
    except Exception as e:
        print(f"Error saving processed entries: {e}")

def generate_entry_id(row):
    """Generate a unique ID for a row entry based on its content."""
    # Create a string from all the row data
    row_str = ''.join(str(item) for item in row.values())
    # Hash it to create a unique identifier
    return hashlib.md5(row_str.encode()).hexdigest()

def create_markdown_file(row, entry_id):
    """Create a markdown file for the entry with space for comments."""
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Extract data - adjusting field names based on the spreadsheet
    timestamp = row.get('Timestamp', 'Unknown Date')
    did_you = row.get('Did you?', 'No Response')
    email = row.get('Email Address', 'No Email')
    
    # Create markdown content
    markdown_content = f"""# New Form Response - {timestamp}

## Details
- **Timestamp:** {timestamp}
- **Did you enjoy AI crush?:** {did_you}
- **Email:** {email}

## Comments
<!-- Add your comments below this line -->


## Send Email?
- [ ] Yes, send email to this respondent

"""
    
    # Write to file
    filename = f"{OUTPUT_DIR}/{entry_id}.md"
    with open(filename, 'w') as f:
        f.write(markdown_content)
    
    return filename

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch new entries from Google Sheets')
    parser.add_argument('--force-all', action='store_true', 
                        help='Process all entries, including previously processed ones')
    parser.add_argument('--reset-auth', action='store_true',
                        help='Reset authentication token and re-authenticate')
    args = parser.parse_args()
    
    # Check if token exists and delete it if requested
    if args.reset_auth and os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print(f"Removed {TOKEN_FILE}. You will need to authenticate again.")
    elif args.force_all and os.path.exists(TOKEN_FILE):
        user_input = input("Do you want to reset authentication credentials as well? (y/n): ").lower()
        if user_input == 'y':
            os.remove(TOKEN_FILE)
            print(f"Removed {TOKEN_FILE}. You will need to authenticate again.")
    
    try:
        # Get sheet data
        rows = get_sheet_data()
        
        if not rows:
            print("No data to process.")
            return
        
        # Get previously processed entries
        processed_entries = get_processed_entries() if not args.force_all else []
        new_processed_entries = processed_entries.copy()
        
        # Process new entries
        new_entries_count = 0
        
        for row in rows:
            entry_id = generate_entry_id(row)
            
            if entry_id not in processed_entries:
                filename = create_markdown_file(row, entry_id)
                new_processed_entries.append(entry_id)
                new_entries_count += 1
                print(f"Created markdown file: {filename}")
        
        # Save processed entries
        save_processed_entries(new_processed_entries)
        
        if new_entries_count > 0:
            print(f"Processed {new_entries_count} new entries.")
        else:
            print("No new entries found.")
    
    except Exception as e:
        if "permission" in str(e).lower():
            print("\n=== PERMISSION ERROR ===")
            print("Your Google account does not have permission to access this spreadsheet.")
            print("\nTo fix this, please ensure:")
            print("1. The spreadsheet is shared with your Google account")
            print(f"2. The correct spreadsheet ID is used: {SPREADSHEET_ID}")
            print("3. The sheet name is correct (case sensitive):", RANGE_NAME)
            print("\nHow to share the spreadsheet:")
            print("- Open the spreadsheet in Google Sheets")
            print("- Click the 'Share' button in the top right")
            print("- Add your email address and give at least 'Viewer' permissions")
            print("- Try running this script again")
            print("\nIf you've authenticated with the wrong account:")
            print("- Delete the token.json file")
            print("- Run the script again to re-authenticate with the correct account")
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 