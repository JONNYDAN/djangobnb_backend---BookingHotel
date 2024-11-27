import hashlib
import hmac
import json
import requests
import logging
from typing import Dict
from datetime import datetime, timedelta
# Replace these values with your actual configuration
CLIENT_ID = ""
API_KEY = ""
CHECKSUM_KEY = ""
API_CREATE_PAYMENT = "https://api-merchant.payos.vn/v2/payment-requests"

class PaymentModel:
    class CreatePaymentPayOSRequest:
        def __init__(self, amount: int, cancel_url: str, description: str, order_code: int, return_url: str):
            self.amount = amount
            self.cancel_url = cancel_url
            self.description = description
            self.order_code = order_code
            self.return_url = return_url

    class CreatePaymentPayOSRes:
        def __init__(self, status_code: int, data: Dict):
            self.status_code = status_code
            self.data = data

    class WebhookData:
        def __init__(self, data: Dict, signature: str):
            self.data = data
            self.signature = signature

# Function to create a payment request
def create_payment_payos_request(payload):
    headers = {
        'x-client-id': CLIENT_ID,
        'x-api-key': API_KEY,
    }

    print(payload)
    try:
        response = requests.post(API_CREATE_PAYMENT, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error: {response.status_code}, {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None

# Function to check the webhook signature
def check_signature_webhook(transaction: PaymentModel.WebhookData) -> bool:
    # Sort the keys of the data dictionary
    sorted_keys = sorted(transaction.data.keys())
    
    # Build the transaction string
    transaction_str_arr = []
    for key in sorted_keys:
        value = transaction.data[key]
        snake_key = key[0].lower() + key[1:]
        transaction_str_arr.append(f"{snake_key}={value}")
    
    transaction_str = "&".join(transaction_str_arr)
    
    # Generate the HMAC SHA256 signature
    generated_signature = generate_signature(transaction_str)
    
    return generated_signature == transaction.signature

# Function to generate the signature
def generate_signature(req: dict) -> str:
    # Construct the transaction string similar to the Go function
    transaction_str = f"amount={req['amount']}&cancelUrl={req['cancelUrl']}&description={req['description']}&orderCode={req['orderCode']}&returnUrl={req['returnUrl']}"
    
    # Generate the HMAC using SHA256
    secret_key = CHECKSUM_KEY.encode('utf-8')  # Assuming the checksum key is stored in the config
    h = hmac.new(secret_key, transaction_str.encode('utf-8'), hashlib.sha256)
    
    # Get the resulting signature and convert it to a hexadecimal string
    signature = h.hexdigest()
    
    return signature
def create_pay_url(req)-> str:
        # Set expiration time to 10 minutes from now
        expired_time = datetime.now() + timedelta(minutes=10)

        # Create payment request data
        data =  {
            "orderCode": 123467,
            "amount": 1000,
            "description": "Payment for booking",
            "buyerName": "John Doe",
            "buyerEmail": "",
            "buyerPhone": "",
            "buyerAddress": "",
            "items": [],
            "cancelUrl": "http://localhost:8000",
            "returnUrl": "http://localhost:8000",
            "expiredAt": int(expired_time.timestamp()),
        }
        print(data)
        # Generate signature (assuming GenerateSignature is a function you have in your Python code)
        data['signature'] = generate_signature(data)

        # Call external function to create payment (assuming CreatePaymentPayOSRequest is implemented in Python)
        pay_data = create_payment_payos_request(data)

        # Log the payment request (assuming payment_repo.CreatePaymentQRRequestLog is a method in Python)
        print("response")
        print(pay_data)
        return pay_data["data"]["checkoutUrl"]