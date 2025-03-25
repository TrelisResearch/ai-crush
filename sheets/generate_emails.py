#!/usr/bin/env python3
import os
import re
import sys
import argparse
import smtplib
import markdown
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Constants
MD_DIR = 'markdown_files'
PROCESSED_DIR = 'processed_markdown'
EMAIL_PATTERN = r'\*\*Email:\*\*\s*(.*)'
SEND_EMAIL_PATTERN = r'- \[x\] Yes, send email to this respondent'
COMMENTS_PATTERN = r'## Comments\s*(?:<!--.*?-->)?\s*(.*?)(?=\s*##|$)'

def get_markdown_files():
    """Get list of markdown files that haven't been processed yet."""
    if not os.path.exists(MD_DIR):
        print(f"Directory {MD_DIR} does not exist.")
        return []
    
    return [f for f in os.listdir(MD_DIR) if f.endswith('.md')]

def parse_markdown_file(file_path):
    """Parse markdown file to extract necessary information."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract email
        email_match = re.search(EMAIL_PATTERN, content, re.DOTALL)
        email = email_match.group(1).strip() if email_match else None
        
        # Check if email should be sent
        should_send = bool(re.search(SEND_EMAIL_PATTERN, content, re.DOTALL))
        
        # Extract comments
        comments_match = re.search(COMMENTS_PATTERN, content, re.DOTALL)
        comments = comments_match.group(1).strip() if comments_match else ""
        
        return {
            'email': email,
            'should_send': should_send,
            'comments': comments,
            'raw_content': content,
            'file_name': os.path.basename(file_path)
        }
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

def create_email_content(parsed_data):
    """Create HTML email content from parsed markdown data."""
    # Convert the comments to HTML
    comments_html = markdown.markdown(parsed_data['comments'])
    
    # Create basic email template
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 10px; border-bottom: 1px solid #e9ecef; }}
            .content {{ padding: 20px 0; }}
            .footer {{ border-top: 1px solid #e9ecef; padding-top: 15px; font-size: 0.8em; color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Thank you for your feedback!</h2>
            </div>
            <div class="content">
                <p>We appreciate your response to our form.</p>
                
                <div class="comments">
                    {comments_html}
                </div>
                
                <p>Please let us know if you have any questions.</p>
            </div>
            <div class="footer">
                <p>This is an automated email generated based on your form submission.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_email(recipient, subject, html_content, is_production):
    """Send email to recipient (dummy implementation)."""
    if is_production:
        try:
            # This would be the actual email sending logic
            # Using a simple placeholder for now
            print(f"PRODUCTION MODE: Would send email to {recipient}")
            print(f"Subject: {subject}")
            print("This is just a placeholder for actual email sending logic")
            
            # Uncomment and configure this code when ready to send real emails
            """
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = 'your-email@example.com'
            msg['To'] = recipient
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('your-email@example.com', 'your-password')
                server.send_message(msg)
            """
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    else:
        # Just print the email details in non-production mode
        print(f"\n{'=' * 50}")
        print(f"PREVIEW MODE: Email to {recipient}")
        print(f"Subject: {subject}")
        print(f"{'=' * 50}")
        print(html_content)
        print(f"{'=' * 50}\n")
        return True

def move_to_processed(file_path, success):
    """Move markdown file to processed directory after handling."""
    # Create processed directory if it doesn't exist
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Create success and failure subdirectories
    success_dir = os.path.join(PROCESSED_DIR, 'success')
    failure_dir = os.path.join(PROCESSED_DIR, 'failure')
    os.makedirs(success_dir, exist_ok=True)
    os.makedirs(failure_dir, exist_ok=True)
    
    # Determine target directory
    target_dir = success_dir if success else failure_dir
    file_name = os.path.basename(file_path)
    
    # Move the file
    try:
        os.rename(file_path, os.path.join(target_dir, file_name))
        print(f"Moved {file_name} to {target_dir}")
    except Exception as e:
        print(f"Error moving file {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Generate emails from markdown files')
    parser.add_argument('--production', action='store_true', 
                        help='Send actual emails instead of just previewing')
    args = parser.parse_args()
    
    # Get all markdown files
    md_files = get_markdown_files()
    if not md_files:
        print("No markdown files found to process.")
        return
    
    # Process each file
    for file_name in md_files:
        file_path = os.path.join(MD_DIR, file_name)
        parsed_data = parse_markdown_file(file_path)
        
        if not parsed_data:
            print(f"Skipping {file_name} due to parsing error.")
            continue
        
        if not parsed_data['should_send']:
            print(f"Skipping {file_name} - not marked for sending.")
            continue
        
        if not parsed_data['email']:
            print(f"Skipping {file_name} - no email address found.")
            continue
        
        # Generate email content
        html_content = create_email_content(parsed_data)
        
        # Send email
        subject = "Thank you for your feedback"
        success = send_email(
            parsed_data['email'], 
            subject, 
            html_content, 
            args.production
        )
        
        # Move file to processed directory
        move_to_processed(file_path, success)
    
    print("Email generation process completed.")

if __name__ == "__main__":
    main() 