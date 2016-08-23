from statsd import StatsClient
from datetime import datetime
from time import sleep

statsd_client = StatsClient(host='metrics')

'''
starting to include tags (remember: tags have to be strings)
'''
for x in range(100,1000,100):
    print 'sleeping for {0} ms'.format(x)
    with statsd_client.timer('sd_timer,tag1=foo,x={}'.format(x)):
        sleep(float(x)/float(1000))

