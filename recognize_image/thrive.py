import requests
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# function to get customer details
def get_customer_details(customer_email, mode):
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("THRIVE_API_KEY")}',
            'Content-Type': 'application/json',
            'X-TC-Mode': mode
        }

        payload = {
            'email':customer_email
        }

        response = requests.post(
            "https://thrivecart.com/api/external/customer",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            customer_data = response.json()
            return customer_data

        else:
            return f"Error {response.status_code}: {response.text}"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = f"Failed to get thrivecart customer, error: {str(e)} at line {exc_tb.tb_lineno}"
        return error_message

#res = get_customer_details()
def cancel_subscription(order_id , subscription_id , mode):
    try:
        url = "https://thrivecart.com/api/external/cancelSubscription"

        headers = {
        'Authorization': f'Bearer {os.getenv("THRIVE_API_KEY")}',
        'Content-Type': 'application/json',
        'X-TC-Mode': mode
        }

        payload = {"order_id": order_id, "subscription_id": subscription_id}
        response = requests.request("POST", url, headers=headers, json=payload)
        return response.json()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = f"Failed to cancel subscription of thrivecart payment, error: {str(e)} at line {exc_tb.tb_lineno}"
        return error_message
    
def get_subscription_id(email , mode):
    try:
        url = "https://thrivecart.com/api/external/customer"
        headers = {
            'Authorization': f'Bearer {os.getenv("THRIVE_API_KEY")}',
            'Content-Type': 'application/json',
            'X-TC-Mode': mode  
        }

        payload = {"email": email.strip()}
        print(f"Sending payload: {payload}")

        response = requests.post(url, headers=headers, json=payload)

        return response.json()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = f"Failed to fetch ThriveCart data: {str(e)} at line {exc_tb.tb_lineno}"
        return error_message
    
