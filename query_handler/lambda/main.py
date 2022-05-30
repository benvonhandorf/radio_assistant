import datetime
import json


def main(event, context):
    print(event)

    print(context)

    request = json.loads(event['body'])

    result = {
        'session': request['session'],
        'prompt': {
            'firstSimple': {
                'speech': 'That beam came from AWS Lambda!'
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
