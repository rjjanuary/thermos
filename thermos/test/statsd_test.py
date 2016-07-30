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

statsd_client = StatsClient(host='ets-vvaprd-metrics-a01')

# for x in range(100,1000,100):
#     tstart = datetime.utcnow()
#     sleep(float(x)/float(1000))
#     tdelta = datetime.utcnow()-tstart
#     print tdelta.microseconds
#     ms=float((tdelta.days*86400000)+(tdelta.seconds*1000)+(tdelta.microseconds/1000))
#     print '{0:0.2f} ms'.format(ms)
#     statsd_client.timing('sd_timing',ms)

# for x in range(100,1000,100):
#     print 'sleeping for {0} ms'.format(x)
#     with statsd_client.timer('sd_timer'):
#         sleep(float(x)/float(1000))
#

# print 'incrementing by 1'
# for x in range(100,1000,100):
#     statsd_client.incr('sd_incr_single')
#     sleep(.5)
#
# print 'incrementing by \"n\"'
# for x in range(100,1000,100):
#     statsd_client.incr('sd_incr_count')
#     print 'increment by {}'.format(x)
#     sleep(.1)

'''
strange interoperation, stopping telegraf does not stop metrics from persisting
'''
# for x in range(100,1000,100):
#     statsd_client.gauge('sd_gauge',x)
#     print 'setting gauge to {} '.format(x)
#     sleep(1)

'''
starting to include tags (remember: tags have to be strings)
'''
# for x in range(100,1000,100):
#     print 'sleeping for {0} ms'.format(x)
#     with statsd_client.timer('sd_timer,tag1=foo,x={}'.format(x)):
#         sleep(float(x)/float(1000))


