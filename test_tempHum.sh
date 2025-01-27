#!/bin/bash

# Envia 5 mensajes de temperatura y humedad
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 22.5, "humedad": 55.0, "timestamp": "2025-01-16T20:05:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 23.0, "humedad": 56.0, "timestamp": "2025-01-16T20:10:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 21.8, "humedad": 54.5, "timestamp": "2025-01-16T20:15:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 22.2, "humedad": 53.8, "timestamp": "2025-01-16T20:20:00Z"}'
mosquitto_pub -h broker.hivemq.com -p 1883 -t ciberfisicos/temp_hum -m '{"temperatura": 21.5, "humedad": 52.3, "timestamp": "2025-01-16T20:25:00Z"}'
