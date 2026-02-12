import os
import time
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def download_mint_pdf():
    """Download the Mint newspaper PDF using Selenium"""
    
    print("Setting up browser...")
    
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Set download directory
    download_dir = os.path.abspath(".")
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = None
    pdf_filename = None
    
    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("Navigating to website...")
        driver.get("https://www.tradingref.com/mint")
        
        # Wait for page to load
        time.sleep(3)
        
        # Get today's date
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        
        print(f"Filling form for date: {date_str}")
        
        # Wait for and select date
        date_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "date"))
        )
        date_input.clear()
        date_input.send_keys(date_str)
        
        # Select language (English)
        language_select = Select(driver.find_element(By.ID, "language"))
        language_select.select_by_value("english")
        
        # Select newspaper (Mint)
        newspaper_select = Select(driver.find_element(By.ID, "newspaper"))
        newspaper_select.select_by_value("mint")
        
        # Select edition (Mumbai)
        edition_select = Select(driver.find_element(By.ID, "edition"))
        edition_select.select_by_value("mumbai")
        
        time.sleep(1)
        
        print("Clicking download button...")
        
        # Find and click the download button
        download_button = driver.find_element(By.ID, "downloadBtn")
        driver.execute_script("arguments[0].click();", download_button)
        
        # Wait for download to complete (check for file in download directory)
        print("Waiting for PDF download...")
        timeout = 60  # 60 seconds timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Look for PDF files in the download directory
            files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
            if files:
                # Get the most recent PDF file
                pdf_filename = max(files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
                
                # Check if file is completely downloaded (not .crdownload)
                if not pdf_filename.endswith('.crdownload'):
                    print(f"✅ PDF downloaded: {pdf_filename}")
                    break
            time.sleep(2)
        
        if not pdf_filename:
            print("❌ PDF download timed out")
            return None
        
        # Rename the file to a consistent name
        new_filename = f"Mint_Mumbai_{today.strftime('%d_%b_%Y')}.pdf"
        if pdf_filename != new_filename:
            os.rename(pdf_filename, new_filename)
            pdf_filename = new_filename
        
        return pdf_filename
        
    except Exception as e:
        print(f"❌ Error downloading PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if driver:
            driver.quit()

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
