from . import config
import requests, json


def send_request(amount: int, description: str = "Fin Bot Income, VIP Account", mobile: str = "NaN", email: str = "NaN", order_id: str = None):
    url = "https://api.zarinpal.com/pg/v4/payment/request.json"
    
    data = {
        "merchant_id" : config.MERCHANT,
        "amount" : amount,
        "description" : description,
        "callback_url" : config.CallbackURL,
        "metadata" : {
            "mobile" : mobile,
            "email" : email,
        },
        "order_id" : order_id
    }
    data = json.dumps(data)
    headers = {
        "Content-Type": "application/json",
        "Accept" : "application/json"
    }

    result = requests.post(url=url, headers=headers, data=data)
    return result

def make_link(authority:str):
    url = f"https://www.zarinpal.com/pg/StartPay/{authority}"

    return url