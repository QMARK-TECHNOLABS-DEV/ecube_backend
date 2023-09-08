import boto3
import random

# Initialize the Amazon SNS client
client = boto3.client("sns")

# Generate a random OTP (6 digits)
otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

# Define the phone number where you want to send the OTP
phone_number = '+919746330679'  # Include the country code without spaces

# Send the OTP via SMS
response = client.publish(
    PhoneNumber=phone_number,
    Message=f'Your OTP is: {otp}',
)

# Check the response
if response['ResponseMetadata']['HTTPStatusCode'] == 200:
    print(f'OTP sent successfully to {phone_number}')
else:
    print('Failed to send OTP')

    