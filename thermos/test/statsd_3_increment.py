from statsd import StatsClient
from datetime import datetime
from time import sleep

statsd_client = StatsClient(host='metrics')

print 'incrementing by 1'                 # print start statement
for x in range(100,1000,100):             # start of loop
    statsd_client.incr('sd_incr_single')  # increment by the default of 1