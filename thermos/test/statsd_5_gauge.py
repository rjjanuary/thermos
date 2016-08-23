from statsd import StatsClient
from datetime import datetime
from time import sleep

statsd_client = StatsClient(host='metrics')

'''
strange interoperation, stopping telegraf does not stop metrics from persisting
'''
# for x in range(100,1000,100):
#     statsd_client.gauge('sd_gauge',x)
#     print 'setting gauge to {} '.format(x)
#     sleep(1)
