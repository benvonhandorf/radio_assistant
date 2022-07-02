import os

import argparse

import boto3
from botocore.exceptions import ClientError

from band_analyzer import BandAnalyzer

from influxdb_client import InfluxDBClient, Point

import logging

from datetime import datetime

import plotly.graph_objects as go

import plotly.express as px

# session = boto3.Session(profile_name='radio_assistant_writer')
# s3_client = session.client('s3')

# try:
#     s3_client.upload_file('sample_data.json', 'radio-assitant-data-free-moose', 'band_status.json')
# except ClientError as e:
#     print(e)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--influx_server', default="http://littlerascal.local:8086",
        help="InfluxDB Server")
    argument_parser.add_argument('--influx_token', default=os.environ['INFLUX_TOKEN'],
        help="InfluxDB Auth Token")
    argument_parser.add_argument('--influx_org', default='skyiron',
        help="InfluxDB Organization")
    argument_parser.add_argument('--aws_profile', default='radio_assistant_writer',
        help="AWS Profile")
    argument_parser.add_argument('--duration', default=60, type=int,
        help="Minutes of data to include")

    args = argument_parser.parse_args()

    influx_client = InfluxDBClient(url=args.influx_server, token=args.influx_token, org=args.influx_org)

    query_api = influx_client.query_api()

    band_analyzer = BandAnalyzer(query_api)

    bands = band_analyzer.list_bands(timespan_minutes=args.duration)

    logging.info(f'Bands Found: {bands}')

    # figure = go.Figure()

    for band in bands:
        logging.info(f'Retrieving band {band}')

        band_polar_data = band_analyzer.retrieve_band_polar_data(band, timespan_minutes=args.duration)

        logging.debug(band_polar_data.to_string())

        # figure.add_trace(go.Barpolar(band_polar_data,
        #     name = band,
        #     theta = "segment",
        #     r = "_value"
        # ))

        figure = px.bar_polar(band_polar_data,
            r="distance_relative", 
            theta="segment",
            color="snr",
            template="plotly_dark",
            color_discrete_sequence= px.colors.sequential.Plasma_r)

        break

    if not os.path.exists("images"):
        os.mkdir("images")

    figure.write_image("images/output.png")
    