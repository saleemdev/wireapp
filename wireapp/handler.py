import frappe
import erpnext
import requests
import json


short_code = "603021"
test_consumer_key = "Ku3732GN5Y5zczJ50lrb6uhIkLgolG9A"
test_consumer_secret = "OxIKi5blQBqJi40H"

# mpesa event handlers

def get_access_token():

    consumer_key = test_consumer_key
    consumer_secret = test_consumer_secret
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    r = requests.get(api_URL, auth=requests.auth.HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = json.loads(r.text)

    return access_token['access_token']

@frappe.whitelist(allow_guest=True)
def register_urls():

    access_token = get_access_token()
    
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {
        "ShortCode": short_code,
        "ResponseType": "Completed",
        "ConfirmationURL": "https://wire.bizpok.com/api/method/wireapp.handler.confirm",
        "ValidationURL": "https://wire.bizpok.com//api/method/wireapp.handler.validate"
    }
    response = requests.post(api_url, json=options, headers=headers)
    response = json.loads(response.text)

    frappe.local.response.update(response)

@frappe.whitelist(allow_guest=True)
def confirm(*args, **kwargs):

    data = kwargs
    frappe.logger("frappe.web").debug(kwargs)
    amount = kwargs['TransAmount']
    account_number = data['BillRefNumber']
    tx_reference = data['TransID']
    phone_number = data['MSISDN']


    try:
        payment = frappe.get_doc({
            "doctype":"MPESA Payments",
            "phone_number":phone_number,
            "reference_number":tx_reference,
            "bill_reference_number": account_number,
            "raw_json_response":json.dumps(data),
            "amount": amount,
            "transaction_time":data['TransTime'],
            "sender_name":  "{} {} {}".format(data['FirstName'], data['MiddleName'], data['LastName']) 
        })
        payment.run_method('set_missing_values')
        payment.insert(
            ignore_permissions=True,
            ignore_links=True,
        )
        payment.submit()
        frappe.db.commit()
        payment.notify_update()
        
        frappe.logger("frappe.web").debug(payment)

    except Exception as e:
        frappe.logger("frappe.web").debug({"error":str(e)})

    frappe.local.response.update({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        })


@frappe.whitelist(allow_guest=True)
def validate(*args, **kwargs):
    frappe.logger("frappe.web").debug(kwargs)

    try:
        if (1 > 0):
            frappe.local.response.update({
                "ResultCode": 0,
                "ResultDesc": "Accepted"
            })

    except Exception as e:
        frappe.local.response.update({
            "ResultCode":1, 
            "ResultDesc":"Failed"
        })



@frappe.whitelist(allow_guest=True)
def simulate_tx(*args, **kwargs):

    access_token = get_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "ShortCode": short_code,
        "CommandID": "CustomerPayBillOnline",
        "Amount": kwargs['amount'],
        "Msisdn": "254708374149",
        "BillRefNumber": kwargs['account_no']
    }
    response = requests.post(api_url, json=request, headers=headers)
    response = json.loads(response.text)

    frappe.local.response.update(response)
