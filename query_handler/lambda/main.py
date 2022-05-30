import datetime
import json


def main(event, context):
    print(event)

    print(context)

    result = {'response': f'Hello.  The time is now {datetime.datetime.now()}'}

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': result
    }
