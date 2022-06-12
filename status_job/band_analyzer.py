from influxdb_client import InfluxDBClient, Point

class BandAnalyzer():
    def __init__(self, client):
        self.client = client

    def list_bands(self, timespan_minutes):
        """Returns a list of the bands seen in the last `timespan_minutes` minutes."""
        pass

