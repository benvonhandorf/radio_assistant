from asyncore import file_dispatcher
import datetime
import json
from jsonpath_ng.ext import parse
import boto3

s3_client = None

def get_band_status_info():
    global s3_client

    if not s3_client:
        s3_client = boto3.client('s3')

    band_status_object = s3_client.get_object(Bucket='radio-assitant-data-free-moose', Key='band_status.json')

    file_contents = band_status_object['Body'].read()

    band_status_info = json.loads(file_contents)

    return band_status_info

def main(event, context):
    try:
        print(event)

        print(context)

        request = json.loads(event['body'])

        session_path = parse('$..session.id')

        session_id = session_path.find(request)[0].value

        intent_path = parse('$..intent.name')
        
        intent = intent_path.find(request)[0].value

        print(f'Intent: {intent}')

        response_speech = ""

        band_status_info = get_band_status_info()

        print(f'Retrieved band status:{band_status_info}')

        if intent == "band_selection":
            print(f'Band selection')

            band_string = parse('$..intent.params.band.resolved').find(request)[0].value

            print(f'Band selection: {band_string}')

            # ?(@.band=='{band_string}')

            # band_path = f"$..bands[0]"

            # print(f'Band string: {band_path}')

            # parsed_path = parse(band_path)

            # print(f'Parsed path: {parsed_path}')

            # band_results = parsed_path.find(band_status_info)

            band_results = [{"value": band_status_info["bands"][0]}]

            print(f'Band Results: {band_results}')

            if band_results:
                print(f'Found band results')

                band = band_results[0]['value']

                print(f'Band Info: {band}')

                response_speech = f'{band["band"]} is currently {band["status"]}.'
            else:
                response_speech = f'I don\'t have any information for {band_string}.'


        elif intent == "all_band_status":
            band_results = parse(f'bands[*]').find(band_status_info)

            if band_results:
                band_summary = '  '.join([f'{band.value["band"]} is {band.value["status"]}.' for band in band_results])

                response_speech = f'Right now, {band_summary}'
            else:
                response_speech = f'I\'m afraid I can\'t tell right now.'

        print(f'Response: {response_speech} {session_id}')

        result = {
            'session': {
                'id' : session_id,
                'params': {}
            }, 
            'prompt': {
                'firstSimple': {
                    'speech': response_speech
                }
            },
            'scene': {
                'next': {
                    'name': 'PromptForBand'
                }
            }
        }

        print(f'Result: {result}')

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }
    except Exception as exception:
        print(f'Unable to process request: {exception}')

if __name__ == "__main__":    
    with open('sample_request.json', 'r') as sample_file:
        input_json = json.load(sample_file)

    test_context = {}

    aws_session = boto3.Session(profile_name='radio_assistant_admin')
    s3_client = aws_session.client('s3')
    
    result = main(input_json, test_context)

    print(json.dumps(result))
