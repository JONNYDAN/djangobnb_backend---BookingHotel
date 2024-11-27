import hashlib
import hmac
import json
import requests
import logging
from typing import Dict
from datetime import datetime, timedelta
from django.conf import settings
import hmac
import hashlib

# Replace these values with your actual configuration

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
        'x-client-id': settings.PAYMENT["CLIENT_ID"],
        'x-api-key': settings.PAYMENT["API_KEY"],
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
    print(settings.PAYMENT)
    secret_key = settings.PAYMENT["CHECKSUM_KEY"].encode('utf-8')  # Assuming the checksum key is stored in the config
    h = hmac.new(secret_key, transaction_str.encode('utf-8'), hashlib.sha256)
    
    # Get the resulting signature and convert it to a hexadecimal string
    signature = h.hexdigest()
    
    return signature

def create_pay_url(req)-> str:
        # Set expiration time to 10 minutes from now
        expired_time = datetime.now() + timedelta(minutes=10)

        # Create payment request data
        data =  {
            "orderCode": req["order_code"],
            "amount": int(req["amount"]),
            "description": "Payment for booking",
            "buyerName": req["buyer_name"],
            "buyerEmail": "",
            "buyerPhone": "",
            "buyerAddress": "",
            "items": [],
            "cancelUrl": settings.PAYMENT["PAYMENT_CANCEL_URL"],
            "returnUrl": settings.PAYMENT["PAYMENT_RETURN_URL"],
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



def convertObjToQueryStr(obj: dict) -> str:
    query_string = []

    for key, value in obj.items():
        value_as_string = ""
        if isinstance(value, (int, float, bool)):
            value_as_string = str(value)
        elif value in [None, 'null', 'NULL']:
            value_as_string = ""
        elif isinstance(value, list):
            value_as_string = json.dumps([sortObjDataByKey(item) for item in value], separators=(',', ':')).replace('None', 'null')
        else:
            value_as_string = str(value)
        query_string.append(f"{key}={value_as_string}")

    return "&".join(query_string)

def sortObjDataByKey(obj: dict) -> dict:
    return dict(sorted(obj.items()))

def isValidData(data,signature,key):
    sorted_data_by_key = sortObjDataByKey(data)
    data_query_str = convertObjToQueryStr(sorted_data_by_key)
    print(data_query_str)
    data_to_signature =  hmac.new(key.encode("utf-8"), msg=data_query_str.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()

    return data_to_signature == signature