#!/bin/bash
echo "sending single packet to statsd"
echo "os_threads,host=globalzone,zone=zonename:114|g" | nc -uw 1 localhost 8125

