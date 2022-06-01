import boto3
from botocore.exceptions import ClientError

session = boto3.Session(profile_name='radio_assistant_writer')
s3_client = session.client('s3')

try:
    s3_client.upload_file('sample_data.json', 'radio-assitant-data-free-moose', 'band_status.json')
except ClientError as e:
    print(e)