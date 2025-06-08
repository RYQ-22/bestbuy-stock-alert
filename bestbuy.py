import argparse
import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
from twilio.rest import Client
import smtplib
from email.message import EmailMessage

load_dotenv("bestbuy.env")

# Environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
MESSAGING_SERVICE_SID = os.getenv("MESSAGING_SERVICE_SID")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")
GOOGLE_APPLICATION_PASSWORD = os.getenv("GOOGLE_APPLICATION_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

DEFAULT_URL = "https://www.bestbuy.com/site/nvidia-geforce-rtx-5080-16gb-gddr7-graphics-card-gun-metal/6614153.p" # Default: 5080 fe
DEFAULT_PROVIDER = "twilio"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def check_button_status(target_url):
    """
    Checks the status of the purchase button on a Best Buy product page, prioritizing data-test-id.

    Args:
        target_url (str): The full URL of the product page.

    Returns:
        str: A description of the button's status, or an error message.
    """
    try:
        # Send a GET request to retrieve the page content
        response = requests.get(target_url, headers=HEADERS, timeout=15) # Set timeout
        response.raise_for_status()  # Check if the request was successful

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Try to find the button using possible data-test-ids
        possible_test_ids = ["add-to-cart", "sold-out", "coming-soon", "check-stores", "get-notified", "in-store-only"]
        found_state = "Unknown"
        found_test_id = None

        for test_id in possible_test_ids:
            # Build a selector based on data-test-id
            selector = f'button[data-test-id="{test_id}"]'
            # print(f"Trying selector: {selector}")
            button_candidate = soup.select_one(selector)

            if button_candidate:
                found_test_id = test_id
                found_state = found_test_id.replace('-', ' ').title()
                break # Stop searching once a button is found

        return found_state

    except requests.exceptions.Timeout:
        return "Error: Time Out"
    except requests.exceptions.HTTPError as http_err:
        return f"Error: HTTP Error: {http_err} (Status Code: {response.status_code})"
    except requests.exceptions.RequestException as req_err:
        return f"Error: Request Error: {req_err}"
    except Exception as e:
        return f"Error: Unknown Error: {e}"

def send_msg(msg_title, msg_body):
    if provider == "twilio":
        send_msg_via_twilio(msg_title, msg_body)
    elif provider == "gmail":
        send_msg_via_gmail(msg_title, msg_body)

def send_msg_via_twilio(msg_title, msg_body):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        messaging_service_sid=MESSAGING_SERVICE_SID,
        body=msg_title+"\n"+msg_body,
        to=RECIPIENT_PHONE_NUMBER
    )

def send_msg_via_gmail(msg_title, msg_body):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(SENDER_EMAIL, GOOGLE_APPLICATION_PASSWORD)
    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = msg_title
    msg.set_content(msg_body)
    s.send_message(msg)
    s.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Best Buy product availability.")
    parser.add_argument(
        "url",
        type=str,
        nargs='?',
        default=DEFAULT_URL,
        help="The URL of the product page to check (optional, defaults to 5080FE)."
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["twilio", "gmail"],
        default=DEFAULT_PROVIDER,
        help="The service provider to send messages (optional, defaults to twilio)"
    )
    args = parser.parse_args()
    url = args.url
    provider = args.provider

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking status for: {url} ...")

    status = check_button_status(url)

    if status == "Sold Out":
        print("Result: Sold Out\n")       # Sold Out
    elif status == "Add to Cart":
        print("Result: Add to Cart\n")    # Add to Cart
        product_name = url.split('/')[-2].replace('-', ' ').title() # Get product name from url
        msg_title = f"Best Buy Stock Alert!"
        msg_body = f"Product: {product_name}\nStatus: Add to Cart!\nLink: {url}"
        send_msg(msg_title, msg_body, provider)
    elif "Error" in status:
        print(f"{status}\n")              # Error
    else:
        print(f"{status}\n")              # Others
