from main import process_request
import argparse
import json
import logging
import boto3

if __name__ == "__main__":    

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--request', default="../sample_requests/sample_request.json",
        help="Request data to be used.  Will be supplied as a body if no body element exists.")

    args = argument_parser.parse_args()

    with open(args.request, 'r') as sample_file:
        input_json = json.load(sample_file)

    if not 'body' in input_json:
        logging.info('Processing input as body.')
        
        request_body = {
            'body': json.dumps(input_json)
        }
    else:
        request_body = input_json

    test_context = {}

    aws_session = boto3.Session(profile_name='radio_assistant_admin')
    s3_client = aws_session.client('s3')
    
    result = process_request(request_body, test_context, s3_client)

    logging.info(json.dumps(result))
