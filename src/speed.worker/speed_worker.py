from nameko.timer import timer
import datetime
import logging
import os
import speedtest
from dotenv import load_dotenv
from influxdb import InfluxDBClient

current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path="{}/.env".format(current_dir))


class SpeedService:
    name = "speed"

    def __init__(self):
        self.influx_client = InfluxDBClient(
            host=os.getenv("INFLUXDB_HOST"),
            port=os.getenv("INFLUXDB_PORT"),
            database=os.getenv("INFLUXDB_DATABASE")
        )

    @timer(interval=3600)
    def speedTest(self):
        logging.info("speedTest")
        current_time = datetime.datetime.utcnow().isoformat()
        speed = self.get_speed()

        self.persists(measurement='download', fields={"value": speed['download']}, time=current_time)
        self.persists(measurement='upload', fields={"value": speed['upload']}, time=current_time)
        self.persists(measurement='ping', fields={"value": speed['ping']}, time=current_time)

    def persists(self, measurement, fields, time):
        logging.info("{} {} {}".format(time, measurement, fields))
        self.influx_client.write_points([{
            "measurement": measurement,
            "time": time,
            "fields": fields
        }])

    @staticmethod
    def get_speed():
        logging.info("Calculating speed ...")
        s = speedtest.Speedtest()
        s.get_best_server()
        s.download()
        s.upload()

        return s.results.dict()
