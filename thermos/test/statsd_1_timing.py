'''
Python statsd client - https://statsd.readthedocs.io/en/latest/reference.html
Telegraf + statsd docs - https://influxdata.com/blog/getting-started-with-sending-statsd-metrics-to-telegraf-influxdb/
Original statsd daemon - https://github.com/etsy/statsd


show measurements with measurement =~ /^sd\_.*$/
select * from /^sd\_.*$/

'''
from statsd import StatsClient
from datetime import datetime
from time import sleep

statsd_client = StatsClient(host='metrics')

for x in range(100,1000,100):                                                         # start of loop
    tstart = datetime.utcnow()                                                        # determine the start time
    sleep(float(x)/float(1000))                                                       # sleep for X milliseconds
    tdelta = datetime.utcnow()-tstart                                                 # determine start time
    print tdelta.microseconds                                                         # print our sleep
    ms=float((tdelta.days*86400000)+(tdelta.seconds*1000)+(tdelta.microseconds/1000)) # convert to ms
    print '{0:0.2f} ms'.format(ms)                                                    # print the sleep time
    statsd_client.timing('sd_timing',ms)                                              # send measurement to statsd
