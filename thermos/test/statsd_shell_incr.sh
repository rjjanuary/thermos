#!/bin/bash
# https://influxdata.com/blog/getting-started-with-sending-statsd-metrics-to-telegraf-influxdb/
echo "sending increment packets to statsd"

for x in {1..20}
do
  echo "example,city=olathe,state=ks:1|c" | nc -uw 1 localhost 8125
  echo "increment sent"
  sleep .5
done;
