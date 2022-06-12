from asyncore import file_dispatcher
import datetime

import json
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_band_status_info(s3_client):
    band_status_object = s3_client.get_object(Bucket='radio-assitant-data-free-moose', Key='band_status.json')

    file_contents = band_status_object['Body'].read()

    band_status_info = json.loads(file_contents)

    return band_status_info

def process_request(event, context, s3_client):
    try:
        logging.debug(json.dumps(event))

        request = json.loads(event['body'])

        logging.debug(json.dumps(request))

        band_string_path =  parse('$..intent.params.band.resolved')

        session_path = parse('$..session.id')

        session_id = session_path.find(request)[0].value

        intent_path = parse('$..intent.name')
        
        intent = intent_path.find(request)[0].value

        logging.debug(f'Intent: {intent}')

        response_speech = ""

        band_status_info = get_band_status_info(s3_client)

        logging.debug(f'Retrieved band status:{band_status_info}')

        if intent == "band_selection":
            logging.debug(f'Band selection')

            logging.debug(f'Band string path: {band_string_path}')

            band_string = band_string_path.find(request)[0].value

            logging.debug(f'Band selection: {band_string}')

            band_path = f"$..bands[?(@.band=='{band_string}')]"

            logging.debug(f'Band string: {band_path}')

            parsed_path = parse(band_path)

            logging.debug(f'Parsed path: {parsed_path}')

            band_results = parsed_path.find(band_status_info)


            logging.debug(f'Band Results: {band_results}')

            if band_results:
                logging.debug(f'Found band results')

                band = band_results[0].value

                logging.debug(f'Band Info: {band}')

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

        logging.info(f'Response: {response_speech} {session_id}')

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
    except Exception as e:
        logging.error(f'Unable to process request: {e}')

def main(event, context):
    s3_client = boto3.client('s3')
    
    process_request(event, context, s3_client)