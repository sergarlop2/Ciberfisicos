#!/bin/bash
mosquitto_pub -h broker.hivemq.com -p 1883 -t SCF/sejuja/moni/1 -m "1"
