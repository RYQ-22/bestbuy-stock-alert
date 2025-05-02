import argparse
import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
from twilio.rest import Client 

load_dotenv("bestbuy.env")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
MESSAGING_SERVICE_SID = os.getenv("MESSAGING_SERVICE_SID")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER") 

print(TWILIO_ACCOUNT_SID)

DEFAULT_URL = "https://www.bestbuy.com/site/nvidia-geforce-rtx-5080-16gb-gddr7-graphics-card-gun-metal/6614153.p"
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
        possible_test_ids = ["add-to-cart", "sold-out", "coming-soon", "check-stores", "get-notified"]
        button = None
        found_state = "Unknown"
        found_test_id = None

        for test_id in possible_test_ids:
            # Build a selector based on data-test-id
            selector = f'button[data-test-id="{test_id}"]'
            # print(f"Trying selector: {selector}")
            button_candidate = soup.select_one(selector)

            if button_candidate:
                button = button_candidate
                found_test_id = test_id
                # print(f"Found button, using data-test-id: '{found_test_id}'")
                break # Stop searching once a button is found

        # --- Check button status ---
        if button:
            # Get text from the button, either from a span inside or directly from the button
            button_text_element = button.find('span')
            button_text = button_text_element.text.strip() if button_text_element else button.text.strip()
            # print(f"Button text: '{button_text}'")

            # Determine the state based on the found test_id or button text
            if found_test_id == "add-to-cart":
                found_state = "Add to Cart"
            elif found_test_id == "sold-out":
                found_state = "Sold Out"
            elif found_test_id == "coming-soon":
                 found_state = "Coming Soon"
            elif found_test_id == "check-stores":
                 found_state = "Check Stores"
            elif found_test_id == "get-notified":
                 found_state = "Get Notified"
            else:
                button_text_lower = button_text.lower()
                found_state = f"Unknown: {button_text}"

        return found_state

    except requests.exceptions.Timeout:
        return "Error: Time Out"
    except requests.exceptions.HTTPError as http_err:
        return f"Error: HTTP Error: {http_err} (Status Code: {response.status_code})"
    except requests.exceptions.RequestException as req_err:
        return f"Error: Request Error: {req_err}"
    except Exception as e:
        return f"Error: Unknown Error: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Best Buy product availability.")
    parser.add_argument(
        "url",
        type=str,
        nargs='?',
        default=DEFAULT_URL,
        help="The URL of the product page to check (optional, defaults to DEFAULT_URL)."
    )
    args = parser.parse_args()
    url = args.url

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking status for: {url} ...")

    status = check_button_status(url)

    if status == "Sold Out":
        print("Result: Sold Out\n")       # Sold Out
    elif status == "Add to Cart":
        print("Result: Add to Cart\n")    # Add to Cart
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        product_name = url.split('/')[-2].replace('-', ' ').title() # Get product name from url
        sms_body = f"Best Buy Stock Alert!\nProduct: {product_name}\nStatus: Add to Cart!\nLink: {url}"
        message = client.messages.create(
            messaging_service_sid=MESSAGING_SERVICE_SID,
            body=sms_body,
            to=RECIPIENT_PHONE_NUMBER
        )
    elif "Error" in status:
        print(f"{status}\n")              # Error
    else:
        print(f"{status}\n")              # Unknown
