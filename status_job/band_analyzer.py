from influxdb_client import InfluxDBClient, Point

class BandAnalyzer():
    def __init__(self, client):
        self.client = client

    def list_bands(self, timespan_minutes):
        
