import requests

def sendSMS(otp, phone_number):
    url = "https://www.fast2sms.com/dev/bulkV2"
    
    payload = f"variables_values={otp}&route=otp&numbers={phone_number}"
    headers = {
        'authorization': "6n5Yp9LQHNscEkqGXIV1PrOu4ZKmRh0baTMt7gd8vijBf3lSoC9J1onzsCfVBpubTAX0542kP6dea8lO",
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)
    
    return response.text

