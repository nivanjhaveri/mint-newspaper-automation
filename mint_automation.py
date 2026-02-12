import os
import requests
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import time

def download_mint_pdf():
    """Download the Mint newspaper PDF for today's date"""
    
    # Get today's date
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    print(f"Attempting to download Mint newspaper for {date_str}...")
    
    # The website uses a form submission, we'll need to construct the PDF URL
    # Based on the website structure, the PDF is likely generated/fetched from their backend
    
    # We'll try to make a POST request to the form
    url = "https://www.tradingref.com/mint"
    
    # Set up headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.tradingref.com/mint'
    }
    
    # Parameters for the form submission
    params = {
        'date': date_str,
        'language': 'english',
        'newspaper': 'mint',
        'edition': 'mumbai'
    }
    
    session = requests.Session()
    
    try:
        # First, visit the main page to get any cookies/session
        session.get(url, headers=headers)
        time.sleep(2)
        
        # Try to get the PDF - the actual endpoint might be different
        # We may need to inspect the network requests to find the exact endpoint
        # For now, we'll try a common pattern
        
        pdf_url = f"https://www.tradingref.com/download/mint/{date_str}/mumbai/english"
        
        response = session.get(pdf_url, headers=headers, allow_redirects=True, timeout=30)
        
        # Check if we got a PDF
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            filename = f"Mint_Mumbai_{today.strftime('%d_%b_%Y')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ PDF downloaded successfully: {filename}")
            return filename
        else:
            print(f"❌ Failed to download PDF. Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading PDF: {str(e)}")
        return None

def send_email_with_pdf(pdf_filename):
    """Send email with PDF attachment"""
    
    # Email configuration from environment variables
    sender_email = os.environ.get('GMAIL_USER')
    sender_password = os.environ.get('GMAIL_APP_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    
    if not all([sender_email, sender_password, receiver_email]):
        print("❌ Missing email configuration in environment variables")
        return False
    
    # Create message
    today = datetime.now()
    subject = f"Mint Epaper - {today.strftime('%b %d, %Y')}"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Add body (simple text)
    body = "Your daily Mint newspaper is attached."
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF
    try:
        with open(pdf_filename, 'rb') as attachment:
            part = MIMEBase('application', 'pdf')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
            msg.attach(part)
        
        # Send email
        print("📧 Sending email...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {receiver_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🗞️  Mint Newspaper Automation")
    print("=" * 50)
    
    # Download the PDF
    pdf_file = download_mint_pdf()
    
    if pdf_file:
        # Send email
        success = send_email_with_pdf(pdf_file)
        
        if success:
            print("\n✅ All done! Check your email.")
        else:
            print("\n❌ Failed to send email")
    else:
        print("\n❌ Could not download PDF")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
