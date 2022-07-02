from influxdb_client import InfluxDBClient, Point
import logging
from datetime import datetime, timedelta
import pytz

class BandAnalyzer():
    def __init__(self, query_api):
        self.query_api = query_api

    def construct_start_stop_utc(self, evaluation_time, timespan_minutes):
        time_delta = timedelta(minutes=timespan_minutes)

        start_utc = pytz.utc.localize(evaluation_time - time_delta)
        end_utc = pytz.utc.localize(evaluation_time)

        return (start_utc, end_utc)

    def list_bands(self, evaluation_time=datetime.now(), timespan_minutes=60):
        """Returns a list of the bands seen in the last `timespan_minutes` minutes."""
        
        start_utc, stop_utc = self.construct_start_stop_utc(evaluation_time, timespan_minutes)

        query = f"""from(bucket: "radio/autogen")
  |> range(start: {start_utc.isoformat()} , stop: {stop_utc.isoformat()})
  |> filter(fn: (r) => r["_measurement"] == "spot")
  |> keep(columns: ["band"])
  |> group(columns: ["band"])
  |> distinct()
  |> keep(columns: ["band"])"""

        logging.debug(query)

        results = self.query_api.query_data_frame(query)

        return results['band'].tolist()



    def retrieve_band_polar_data(self, band_name, evaluation_time=datetime.now(), timespan_minutes=60):
        start_utc, stop_utc = self.construct_start_stop_utc(evaluation_time, timespan_minutes)

        query = f"""
import "math"

band = "{band_name}"
start = {start_utc.isoformat()}
stop = {stop_utc.isoformat()}

snr = from(bucket: "radio/autogen")
|> range(start: start, stop: stop)
|> filter(fn: (r) => r["_measurement"] == "spot")
|> filter(fn: (r) => r["power"] == "5.0")
|> filter(fn: (r) => r["band"] == band)
|> filter(fn: (r) => r["_field"] == "snr")
|> rename(columns: {{ _value: "snr" }})
|> drop(columns: ["_field"])

distance = from(bucket: "radio/autogen")
|> range(start: start, stop: stop)
|> filter(fn: (r) => r["_measurement"] == "spot")
|> filter(fn: (r) => r["power"] == "5.0")
|> filter(fn: (r) => r["band"] == band)
|> filter(fn: (r) => r["_field"] == "distance")
|> rename(columns: {{ _value: "distance" }})
|> drop(columns: ["_field"])
 
azimuth = from(bucket: "radio/autogen")
|> range(start: start, stop: stop)
|> filter(fn: (r) => r["_measurement"] == "spot")
|> filter(fn: (r) => r["power"] == "5.0")
|> filter(fn: (r) => r["band"] == band)
|> filter(fn: (r) => r["_field"] == "azimuth")
|> rename(columns: {{ _value: "azimuth" }})
|> map(fn: (r) => ({{ r with segment: (r.azimuth + 22.5 - ((r.azimuth + 22.5) % 45.0)) % 360.0 }}))
|> drop(columns: ["_field"])
  
j1 = join(tables: {{ azimuth: azimuth, snr: snr }}, on: ["_measurement", "_time", "band", "antenna", "callsign", "spotter", "_start", "_stop", "frequency", "type", "mode", "power"])

join(tables: {{j1: j1, distance: distance}}, on: ["_measurement", "_time", "band", "antenna", "callsign", "spotter", "_start", "_stop", "frequency", "type", "mode", "power"])
|> map(fn: (r) => ({{ r with frequency: math.trunc(x: float(v: r.frequency) * 1000.0) / 1000.0 }}))
|> group(columns: ["band", "frequency", "antenna", "callsign", "spotter", "segment", "type", "mode", "power"])
|> max(column: "snr")
|> group(columns: ["segment"])
|> map(fn: (r) => ({{ r with distance_difference: r.distance }}))
|> sort(columns: ["distance"])
|> difference(columns: ["distance_difference"], keepFirst: true)
|> map(fn: (r) => ({{ r with distance_relative: if exists r.distance_difference then r.distance_difference else r.distance }}))
|> sort(columns: ["distance", "snr"])

"""

        logging.debug(query)

        results = self.query_api.query_data_frame(query)

        return results




