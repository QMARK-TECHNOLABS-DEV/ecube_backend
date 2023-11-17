from pyfcm import FCMNotification
 
push_service = FCMNotification(api_key="AAAAqbxPQ_Q:APA91bGWil8YXU8Zr1CLa-tqObZ-DVJUqq0CrN0O76bltTApN51we3kOqrA4rRFZUXauBDtkcR3nWCQ60UPWuroRZpJxuCBhgD6CdHAnjqh8V2zPIzLvuvERmbipMHIoJJxuBegJW3a3")
 
# registration_id = "72651781ed1e567f"
# message_title = "Title"
# message_body = "Hello"
# result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
 
# print (result)
 
# Send to multiple devices by passing a list of ids.
registration_ids = ["eF5_gLolTPeWKeIERkJCpo:APA91bFHa8h6e5Li89FGT0SICYv5gHumjSUouCpT1G56epiPbBuuPm9KquFuNfyDHQAbgPAeCJMeD815jFbKFNuwP9Kt5U5gfcFYFds7xIVQM8qSxptDZNKioVf0dez3aWGhpUHClHMI"]
message_title = 'Hello there' 
message_body = 'Testing 1'
result=push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)
 
print (result)