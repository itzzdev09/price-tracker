import requests
from bs4 import BeautifulSoup
import smtplib
import json
import time
import os
import re
from dotenv import load_dotenv


dotenv_loaded = load_dotenv()

try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Error: config.json not found. Please create it.")
    exit()
except json.JSONDecodeError:
    print("Error: Could not decode config.json. Please check its format.")
    exit()


PRODUCT_URL = config.get('product_url', '')
PRICE_THRESHOLD = config.get('price_threshold', float('inf'))
SMTP_SERVER = config.get('smtp_server', 'smtp.gmail.com')
SMTP_PORT = config.get('smtp_port', 587)
EMAIL_SENDER = config.get('email_sender', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD') 
EMAIL_RECEIVER = config.get('email_receiver', '')

if not all([PRODUCT_URL, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
    print("\nError: Configuration is incomplete.")
    print("Please check that:")
    print("1. Your .env file is in the same folder as the script and contains your EMAIL_PASSWORD.")
    print("2. Your config.json file is filled out completely.")
    exit()

def get_product_info(url):
    """
    Scrapes the product title and price from the given URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        title_element = soup.find("span", {"id": "productTitle"})
        
        price_element = soup.select_one(".a-price-whole")
        if not price_element:
            price_element = soup.select_one(".a-offscreen")

        if not title_element or not price_element:
            print("Warning: Could not find title or price elements. Amazon's page structure may have changed or you may be blocked.")
            return None, None

        title = title_element.get_text().strip()
        
        price_str = price_element.get_text().strip()
        price_match = re.search(r'[\d,]+(?:\.\d+)?', price_str)
        
        if price_match:
            cleaned_price_str = price_match.group(0).replace(',', '')
            price = float(cleaned_price_str)
        else:
            print(f"Warning: Could not parse a valid price from the string: '{price_str}'")
            return title, None

        return title, price

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        return None, None

def save_data(data, filename="products.json"):
    """
    Saves scraped data to a JSON file.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")

def send_email_alert(subject, body):
    """
    Sends an email alert.
    """
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message.encode('utf-8'))
        print("Email alert sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP authentication failed. Check your email and App Password.")
    except Exception as e:
        print(f"Error sending email: {e}")

def track_price():
    """
    Main function to track the product price and send alerts.
    """
    print(f"\nTracking product: {PRODUCT_URL}")
    title, price = get_product_info(PRODUCT_URL)

    if title and price is not None:
        print(f"Current Price for '{title}': ₹{price:,.2f}")

        product_data = {
            "title": title,
            "price": price,
            "url": PRODUCT_URL
        }
        save_data(product_data)

        if price < PRICE_THRESHOLD:
            print(f"Price drop alert! Current price (₹{price:,.2f}) is below the threshold (₹{PRICE_THRESHOLD:,.2f}).")
            subject = f"Price Drop Alert for {title}"
            body = f"The price of '{title}' has dropped to ₹{price:,.2f}.\n\nYou can buy it here: {PRODUCT_URL}"
            send_email_alert(subject, body)
        else:
            print(f"Price (₹{price:,.2f}) is not below the threshold (₹{PRICE_THRESHOLD:,.2f}). No alert sent.")

if __name__ == "__main__":
    while True:
        track_price()
        print("\nNext check in 24 hours...")
        time.sleep(24 * 60 * 60)
#smtp is failing