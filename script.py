from dotenv import load_dotenv
import os
import datetime
import json
import logging
import boto3
from botocore.exceptions import ClientError

# Open the file in read mode and read the entire content as a string
with open('speedoutput.txt', 'r') as file:
    content = file.read()

# edit the json to remove server and client 
# Convert string to dictionary
data = json.loads(content) 

# Remove 'interface' info
data.pop('interface', None)

# Rename keys to title case
data = {key.title(): value for key, value in data.items()}

# Convert back to string
output = json.dumps(data, indent=4)

#write the updated j

#create timestamp
timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')

#create output filename
filename = f'speedoutput_{timestamp}.json'

#Pull in values from secrets
load_dotenv()
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
ACCESS_SECRET = os.getenv("AWS_SECRET")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

#create a client authenticating with s3
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=ACCESS_SECRET
    )

#try and upload the json, log an error if not
try:
    #upload the json to s3
    response = s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=output)
    print(response)
except ClientError as e:
    logging.error(e)