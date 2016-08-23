#!/bin/bash
echo "sending single packet to statsd"
echo "example,city=austin,state=tx:114|g" | nc -uw 1 localhost 8125

