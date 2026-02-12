import os
import time
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from playwright.sync_api import sync_playwright

def download_mint_pdf():
    """Download the Mint newspaper PDF using Playwright"""
    
    print("Setting up browser...")
    
    download_dir = os.path.abspath(".")
    pdf_filename = None
    
    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                accept_downloads=True,
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            print("Navigating to website...")
            page.goto("https://www.tradingref.com/mint", timeout=60000)
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            
            # Get today's date
            today = datetime.now()
            date_str = today.strftime("%Y-%m-%d")
            
            print(f"Filling form for date: {date_str}")
            
            # Fill in the date
            page.fill('#date', date_str)
            time.sleep(0.5)
            
            # Select language (English)
            page.select_option('#language', 'english')
            time.sleep(0.5)
            
            # Select newspaper (Mint)
            page.select_option('#newspaper', 'mint')
            time.sleep(0.5)
            
            # Select edition (Mumbai)
            page.select_option('#edition', 'mumbai')
            time.sleep(1)
            
            print("Clicking download button...")
            
            # Set up download handler
            with page.expect_download(timeout=120000) as download_info:
                # Click the download button
                page.click('#downloadBtn')
                download = download_info.value
                
                # Save the download
                pdf_filename = f"Mint_Mumbai_{today.strftime('%d_%b_%Y')}.pdf"
                download.save_as(pdf_filename)
                print(f"✅ PDF downloaded: {pdf_filename}")
            
            browser.close()
            return pdf_filename
        
    except Exception as e:
        print(f"❌ Error downloading PDF: {str(e)}")
        import traceback
        traceback.print_exc()
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
    
    # Add body
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
        import traceback
        traceback.print_exc()
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
