Product Price Tracker

This Python script scrapes a product's price from an e-commerce website and sends an email alert if the price drops below a specified threshold.
Features

    --Scrapes product title and price.

    --Saves the latest scraped data to a JSON file.

    --Sends an email alert when the price drops.

    --Configurable settings via a config.json file.

    --Error handling for network and scraping issues.

Prerequisites

    Python 3.12 or more

    requests library

    beautifulsoup4 library

You can install the required libraries using pip:

    sh``` 
    pip install requests beautifulsoup4

Setup & Configuration

    Clone the Repository:

    git clone https://github.com/itzzdev09/price-tracker
    cd price-trakcer

    Configure config.json:

        Open the config.json file.

        product_url: Set the URL of the product you want to track.

        price_threshold: Define the price (as a number) below which you want to receive an alert.

        smtp_server: The SMTP server for your email provider (default is for Gmail).

        smtp_port: The SMTP port (default is 587 for TLS).

        email_sender: Your email address from which the alert will be sent.

        email_receiver: The email address where you want to receive the alert.

    Set Environment Variable for Email Password:
    For security reasons, the script retrieves your email password from an environment variable named EMAIL_PASSWORD.

        Linux/macOS:

        export EMAIL_PASSWORD="your_email_password"

        Windows (Command Prompt):

        set EMAIL_PASSWORD="your_email_password"

        Windows (PowerShell):

        $env:EMAIL_PASSWORD="your_email_password"

    Important: If you are using Gmail, you may need to generate an "App Password" to use for SMTP.

Usage

Once the setup is complete, you can run the script from your terminal:

python price_tracker.py

The script will run once, check the price, and then wait for 24 hours before the next check.
Scheduling Script Execution

For the script to run automatically at regular intervals, you should use a scheduling tool.
Using the schedule library (Pythonic way):

    Install the library:

    pip install schedule

    You can modify price_tracker.py to include a scheduler loop at the end of the file.

    # (in price_tracker.py)
    # ... (rest of the script)

    # if __name__ == "__main__":
    #     import schedule
    #
    #     schedule.every().day.at("09:00").do(track_price)
    #
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(1)

Using cron (Linux/macOS):

    Open your crontab file:

    crontab -e

    Add a new line to schedule the script. For example, to run it every day at 9 AM:

    0 9 * * * /usr/bin/python3 /path/to/your/price_tracker.py

    Make sure to use the correct absolute paths for your Python interpreter and script.

How It Works

    Configuration: The script starts by loading your settings from the config.json file.

    Scraping: It sends an HTTP GET request to the product_url with a User-Agent header to mimic a real browser.

    Parsing: It uses BeautifulSoup to parse the HTML content of the product page. It then finds the product title and price using specific HTML tags and their attributes (e.g., <span id="productTitle">).

        Note: These selectors are specific to Amazon product pages and will need to be changed if you are tracking a product on a different website.

    Data Cleaning: The extracted price is cleaned by removing currency symbols and commas, then converted to a floating-point number.

    Data Storage: The scraped information (title, price, URL) is saved into products.json.

    Price Check & Alert: The script compares the current price with your price_threshold. If it's lower, it calls the send_email_alert function.

    Email Notification: An email is sent using smtplib, which connects to your specified SMTP server and sends the alert.

    Error Handling: The script includes try...except blocks to gracefully handle potential issues like network failures, HTTP errors, or problems finding the required HTML elements on the page.
