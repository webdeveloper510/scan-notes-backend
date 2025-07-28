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
        error_message = f"Failed to update object, error: {str(e)} at line {exc_tb.tb_lineno}"
        return error_message
    

# import requests

# url = "https://thrivecart.com/api/external/subscribe"

# payload = {"event":"order_refund", 
#            "target_url": "https://fichedetravail.com/api/thrivecart-webhook/",
#            "trigger_fields": {"mode_int": 1}}
# headers = {
#     'Authorization': f'Bearer {os.getenv("THRIVE_API_KEY")}',
#     'Content-Type': 'application/json',
#     'X-TC-Mode': 'test'
# }

# response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)


import requests

url = "https://thrivecart.com/api/external/subscribe"
headers = {
    'Authorization': f'Bearer {os.getenv("THRIVE_API_KEY")}',
    "Content-Type": "application/json",
    "X-TC-Mode": "test"
}
payload = {
    "event": "order_success",
    "target_url": "https://fichedetravail.com/thrivecart-webhook/",
    "trigger_fields": {"mode_int": 1}
}

response = requests.post(url, headers=headers, json=payload)
print(response.status_code, response.text)
