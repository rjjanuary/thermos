from statsd import StatsClient
from datetime import datetime
from time import sleep

statsd_client = StatsClient(host='metrics')

for x in range(100,1000,100):                 # start of loop
    print 'sleeping for {0} ms'.format(x)     # print sleep time
    with statsd_client.timer('sd_timer'):     # begin statsd timer
        sleep(float(x)/float(1000))           # sleep X milliseconds
