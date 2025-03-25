# Google Forms Processor

>![TIP]
>Make sure to use an oauth access approach to building this. Make sure you create the spreadsheet in the correct organisation.

This tool processes responses from a Google Form, creates markdown files for reviewing and adding comments, and generates formatted emails based on your feedback.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

   This version requires:
   - google-api-python-client
   - google-auth
   - google-auth-oauthlib
   - markdown (for formatting email content)

2. Set up Google API access:
   
   a. Go to the [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project or select an existing one
   
   c. Enable the Google Sheets API for your project
   
   d. Create OAuth 2.0 credentials:
      - Go to "APIs & Services" > "Credentials"
      - Click "Create Credentials" > "OAuth client ID"
      - Select "Desktop app" as the application type
      - Name your client and click "Create"
   
   e. Download the credentials JSON file and save it as `credentials.json` in the `sheets` directory

3. Share the spreadsheet with your Google account:
   
   a. Open the spreadsheet in Google Sheets
   
   b. Click the "Share" button in the top right
   
   c. Add your email address and give at least "Viewer" permissions
   
   d. Click "Share"

## Usage

The workflow consists of three main steps:

### 1. Fetch New Entries

Run the following command to fetch new entries from the Google Sheet:

```bash
python fetch_new_entries.py
```

The first time you run this, it will:
1. Open a browser window asking you to sign in to your Google account
2. Request permission to access your Google Sheets
3. After granting permission, the authentication token will be saved locally for future use

This will then:
- Connect to the Google Sheet with ID: `1FmBo8Ceq7sr01lHrpblOBEUf5_aogeMWcJDYnX7Hi0Q`
- Find new responses that haven't been processed yet
- Create markdown files in the `markdown_files` directory, one for each new response

Options:
- `--force-all`: Process all entries, even if they've been processed before
- `--reset-auth`: Reset authentication token and re-authenticate with your Google account

### 2. Review and Add Comments

1. Open the generated markdown files in the `markdown_files` directory.
2. Add your comments in the "Comments" section.
3. Check the "Yes, send email" box if you want to send an email to this respondent.

### 3. Generate Emails

After reviewing and commenting, run:

```bash
python generate_emails.py
```

This will:
- Process all markdown files in the `markdown_files` directory
- For those marked for email sending, generate formatted emails
- In preview mode, display the email content in the console
- Move processed files to `processed_markdown/success` or `processed_markdown/failure`

Options:
- `--production`: Actually send the emails instead of just previewing them

## Troubleshooting

### Permission Errors

If you see a permission error like `"The caller does not have permission"`:

1. Make sure the spreadsheet is shared with the Google account you're using
2. Verify that the sheet name is correct (the script uses "Form Responses 1")
3. Try resetting your authentication and signing in again:

```bash
python fetch_new_entries.py --reset-auth
```

### Wrong Google Account

If you authenticated with the wrong Google account:

1. Delete the token.json file
2. Run the script again with `--reset-auth` to re-authenticate:

```bash
python fetch_new_entries.py --reset-auth
```

## Example workflow

```bash
# Fetch new form responses
python fetch_new_entries.py

# Review generated markdown files and add comments
# (manually edit files in markdown_files directory)

# Preview emails that would be sent
python generate_emails.py

# When ready to send emails
python generate_emails.py --production
```

## File Structure

- `fetch_new_entries.py`: Script to fetch and process new form responses
- `generate_emails.py`: Script to create and send emails based on markdown files
- `credentials.json`: Google API OAuth client credentials
- `token.json`: Saved authentication token
- `processed_entries.json`: Tracks which entries have been processed
- `markdown_files/`: Directory containing generated markdown files for review
- `processed_markdown/`: Directory containing processed markdown files 