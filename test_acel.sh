#!/bin/bash
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 1.23, "acel_y": 4.56, "acel_z": 7.89, "timestamp": "2025-01-16T16:00:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 6.34, "acel_y": 5.67, "acel_z": 8.90, "timestamp": "2025-01-16T17:00:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 1.45, "acel_y": 3.78, "acel_z": 9.01, "timestamp": "2025-01-16T18:00:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 3.56, "acel_y": 11.89, "acel_z": 10.12, "timestamp": "2025-01-16T19:00:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 5.67, "acel_y": 4.90, "acel_z": 11.23, "timestamp": "2025-01-16T20:00:00Z"}'
