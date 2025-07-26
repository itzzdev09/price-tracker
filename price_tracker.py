import requests
from bs4 import BeautifulSoup
import smtplib
import json
import time
import os

# Load configuration from config.json
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Error: config.json not found. Please create it.")
    exit()
except json.JSONDecodeError:
    print("Error: Could not decode config.json. Please check its format.")
    exit()

# Product and Email Configuration
PRODUCT_URL = config.get('product_url', '')
PRICE_THRESHOLD = config.get('price_threshold', float('inf'))
SMTP_SERVER = config.get('smtp_server', 'smtp.gmail.com')
SMTP_PORT = config.get('smtp_port', 587)
EMAIL_SENDER = config.get('email_sender', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '') # For security, get from environment variable
EMAIL_RECEIVER = config.get('email_receiver', '')

if not all([PRODUCT_URL, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
    print("Error: Please complete the configuration in config.json and set the EMAIL_PASSWORD environment variable.")
    exit()

def get_product_info(url):
    """
    Scrapes the product title and price from the given URL.
    
    Args:
        url (str): The URL of the product page.
        
    Returns:
        tuple: A tuple containing the product title (str) and price (float),
               or (None, None) if scraping fails.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # --- IDENTIFY TARGET ELEMENTS ---
        # Note: These selectors will need to be adjusted for the actual website.
        title_element = soup.find("span", {"id": "productTitle"})
        price_element = soup.find("span", {"class": "a-price-whole"})

        if not title_element or not price_element:
            print("Warning: Could not find title or price elements. The website structure may have changed.")
            return None, None

        title = title_element.get_text().strip()
        price_str = price_element.get_text().strip().replace(',', '')
        price = float(price_str)

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
    
    Args:
        data (dict): The data to save.
        filename (str): The name of the file to save to.
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
    
    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)
        print("Email alert sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP authentication failed. Check your email and password.")
    except Exception as e:
        print(f"Error sending email: {e}")

def track_price():
    """
    Main function to track the product price and send alerts.
    """
    print(f"Tracking product: {PRODUCT_URL}")
    title, price = get_product_info(PRODUCT_URL)

    if title and price is not None:
        print(f"Current Price for '{title}': ${price:.2f}")

        product_data = {
            "title": title,
            "price": price,
            "url": PRODUCT_URL
        }
        save_data(product_data)

        if price < PRICE_THRESHOLD:
            print(f"Price drop alert! Current price (${price:.2f}) is below the threshold (${PRICE_THRESHOLD:.2f}).")
            subject = f"Price Drop Alert for {title}"
            body = f"The price of '{title}' has dropped to ${price:.2f}.\n\nYou can buy it here: {PRODUCT_URL}"
            send_email_alert(subject, body)
        else:
            print(f"Price (${price:.2f}) is not below the threshold (${PRICE_THRESHOLD:.2f}). No alert sent.")

if __name__ == "__main__":
    # This is a simple loop for demonstration. 
    # For robust scheduling, use 'schedule' library or a cron job.
    while True:
        track_price()
        # Wait for 24 hours before checking again
        print("\nNext check in 24 hours...")
        time.sleep(24 * 60 * 60) 
