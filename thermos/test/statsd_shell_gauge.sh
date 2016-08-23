#!/bin/bash
echo "sending single packet to statsd"
echo "example_gauge,city=austin,state=tx:114|g" | nc -uw 1 localhost 8125

