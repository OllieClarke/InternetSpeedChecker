from dotenv import load_dotenv
import os
import sys
import datetime
import json
import logging
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)

with open('speedoutput.txt', 'r') as file:
    content = file.read()

if not content.strip():
    logging.error("speedoutput.txt is empty - speedtest likely failed")
    sys.exit(1)

data = json.loads(content)

# Strip identifying info 
data.pop('interface', None)
data.pop('isp', None)

# Convert bandwidth from bytes/sec to Mbps for continuity with old data
data['download_mbps'] = round(data['download']['bandwidth'] * 8 / 1_000_000, 2)
data['upload_mbps'] = round(data['upload']['bandwidth'] * 8 / 1_000_000, 2)
data['ping_ms'] = data['ping']['latency']

output = json.dumps(data, indent=4)

timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
filename = f'speedoutput_{timestamp}.json'

load_dotenv()
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
ACCESS_SECRET = os.getenv("AWS_SECRET")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=ACCESS_SECRET
)

try:
    response = s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=output)
    logging.info(f"Uploaded {filename}")
except ClientError as e:
    logging.error(e)
    sys.exit(1)