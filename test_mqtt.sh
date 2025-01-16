#!/bin/bash

# Envia 5 mensajes de aceleraciones
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 1.23, "acel_y": 4.56, "acel_z": 7.89, "timestamp": "2025-01-16T20:05:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 6.34, "acel_y": 5.67, "acel_z": 8.90, "timestamp": "2025-01-16T20:10:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 1.45, "acel_y": 3.78, "acel_z": 9.01, "timestamp": "2025-01-16T20:15:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 3.56, "acel_y": 11.89, "acel_z": 10.12, "timestamp": "2025-01-16T20:20:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/aceleraciones -m '{"acel_x": 5.67, "acel_y": 4.90, "acel_z": 11.23, "timestamp": "2025-01-16T20:25:00Z"}'

# Envia 5 mensajes de temperatura y humedad
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 22.5, "humedad": 55.0, "timestamp": "2025-01-16T20:05:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 23.0, "humedad": 56.0, "timestamp": "2025-01-16T20:10:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 21.8, "humedad": 54.5, "timestamp": "2025-01-16T20:15:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 22.2, "humedad": 53.8, "timestamp": "2025-01-16T20:20:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 21.5, "humedad": 52.3, "timestamp": "2025-01-16T20:25:00Z"}'