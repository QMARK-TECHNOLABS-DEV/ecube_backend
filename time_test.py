# from pyfcm import FCMNotification
 
# push_service = FCMNotification(api_key="AAAAqbxPQ_Q:APA91bGWil8YXU8Zr1CLa-tqObZ-DVJUqq0CrN0O76bltTApN51we3kOqrA4rRFZUXauBDtkcR3nWCQ60UPWuroRZpJxuCBhgD6CdHAnjqh8V2zPIzLvuvERmbipMHIoJJxuBegJW3a3")

# registration_ids = ["dREWgJKnS5yw3KJ_0w0OaS:APA91bGFBliKfQI4itzjmdhDRCqkBDywYeSQjJvIB1f3bHYEF9QLuD70lHyi3AI9QXDofqxzbjaXXEKdeolg8bGboQQPQXeJuLluw0K3Y-h_GEhHg47Ln_OiioGMiWKpqYX-xnXSUk7b"]
# message_title = 'Hello alvin ikka' 
# message_body = 'I love you so much'
# result=push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)
 
# print (result)

import requests
import json

def send_notification(registration_ids, message_title, message_desc, message_type):
    fcm_api = "AAAAqbxPQ_Q:APA91bGWil8YXU8Zr1CLa-tqObZ-DVJUqq0CrN0O76bltTApN51we3kOqrA4rRFZUXauBDtkcR3nWCQ60UPWuroRZpJxuCBhgD6CdHAnjqh8V2zPIzLvuvERmbipMHIoJJxuBegJW3a3"
    url = "https://fcm.googleapis.com/fcm/send"

    headers = {
        "Content-Type": "application/json",
        "Authorization": 'key=' + fcm_api
    }

    payload = {
        "registration_ids": registration_ids,
        "priority": "high",
        "notification": {
            "body": message_desc,
            "title": message_title,
        },
        "data": {
            "type": message_type,
        }
    }

    result = requests.post(url, data=json.dumps(payload), headers=headers)
    print(result.json())

def send():
    registration = ['dREWgJKnS5yw3KJ_0w0OaS:APA91bGFBliKfQI4itzjmdhDRCqkBDywYeSQjJvIB1f3bHYEF9QLuD70lHyi3AI9QXDofqxzbjaXXEKdeolg8bGboQQPQXeJuLluw0K3Y-h_GEhHg47Ln_OiioGMiWKpqYX-xnXSUk7b']
    result = send_notification(registration, 'nayeente mone', 'oooooooooooooooooooooooooooooooooooooooooooooooooooommmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'attendence')
    print(result)

if __name__ == "__main__":
    send()