import datetime
import json
from jsonpath_ng import parse, jsonpath

def main(event, context):
    print(event)

    print(context)

    request = json.loads(event['body'])

    intent_path = parse('intent.name')
    
    intent = intent_path.find(request)[0].value

    band_string = ""

    if intent == "band_selection":
        band_string = parse('intent.params.band.resolved').find(request)[0].value
    elif intent == "all_band_status":
        band_string = "ALL THE BANDS"

    result = {
        'session': request['session'],
        'prompt': {
            'firstSimple': {
                 'speech': f'That beam came from AWS Lambda! {intent} {band_string}'
            }
        },
        'scene': {
            'next': {
                'name': 'PromptForBand'
            }
        }
    }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(result)
    }

if __name__ == "__main__":    
    with open('sample_request.json', 'r') as sample_file:
        input_json = json.load(sample_file)

    test_context = {}

    result = main(input_json, test_context)

    print(json.dumps(result))
