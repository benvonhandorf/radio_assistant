import os
import boto3
import argparse
from botocore.exceptions import ClientError

# session = boto3.Session(profile_name='radio_assistant_writer')
# s3_client = session.client('s3')

# try:
#     s3_client.upload_file('sample_data.json', 'radio-assitant-data-free-moose', 'band_status.json')
# except ClientError as e:
#     print(e)

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--influx_server', default="littlerascal.local",
        help="InfluxDB Server")
    argument_parser.add_argument('--influx_token', default=os.environ['INFLUX_TOKEN'],
        help="InfluxDB Auth Token")
    argument_parser.add_argument('--aws_profile', default='radio_assistant_writer',
        help="AWS Profile")

    args = argument_parser.parse_args()

    