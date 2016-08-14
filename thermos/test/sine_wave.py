import argparse, datetime, time, pytz, math
import string, random  # needed for string name
from influxdb import InfluxDBClient

'''
inputs: cycles per minute, amplitude, bias, samples per minute

rads_per_ms = 2pi * (desired_cycles_per_minute / 60 / 1000)
sleep_time = 60 / desired_samples_per_minute
point = amplitude * sin(ms_since_midnight * rads_per_ms) + bias
'''

now = datetime.datetime.now()
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
local_tz = pytz.timezone('US/Central')


def run(cmdargs):
    wavename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    rads_per_ms = (2 * math.pi) * (cmdargs.cycles_per_minute / 60 / 1000)
    sleep_time = 60.0 / cmdargs.samples_per_minute
    influx_client = InfluxDBClient(host=cmdargs.host, port=cmdargs.port, database=cmdargs.database)
    print '{0:.4f}'.format(math.pi)
    print 'cpm: {2} rads_per_ms: {0:.4f} sleep_time:{1}'.format(rads_per_ms, sleep_time, cmdargs.cycles_per_minute)
    while True:
        now = datetime.datetime.now()
        tdelta = (now - midnight)
        ms_since_midnight = (tdelta.microseconds / 1000) + (tdelta.seconds * 1000)
        utctime = local_tz.localize(now).astimezone(pytz.utc)
        cur_y = cmdargs.amplitude * math.sin(ms_since_midnight * rads_per_ms) + cmdargs.bias
        #        print 'wavename: {1} value: {0:.4f} ms_since_midnight: {2}'.format(cur_y,wavename,ms_since_midnight)
        influx_client.write_points([{
            "measurement": "sinewave",
            "tags": {"wavename": wavename},
            "time": utctime,
            "fields": {"value": cur_y}
        }])
        time.sleep(sleep_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Process Commandline options')
    parser.add_argument('--cycles', dest='cycles_per_minute', type=float, default=10,
                        help='Frequency (X axis length) of sine wave')
    parser.add_argument('--amplitude', dest='amplitude', type=float, default=1,
                        help='Amplitude (Y axis height) of sine wave')
    parser.add_argument('--bias', dest='bias', type=float, default=0, help='Y axis offset of sine wave')
    parser.add_argument('--samples', dest='samples_per_minute', type=int, default=60,
                        help='Number of samples to collect per minute')
    parser.add_argument('--batchsize', dest='influx_batchsize', type=int, default=0,
                        help='number of items to batch to influx at a given time')
    parser.add_argument('--host', type=str, required=False, default='localhost', help='hostname influxdb http API')
    parser.add_argument('--port', type=int, required=False, default=8086, help='port influxdb http API')
    parser.add_argument('--database', type=str, required=False, default='example', help='database to write to')
    cmdargs = parser.parse_args()
    run(cmdargs)
