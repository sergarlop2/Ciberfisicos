#!/bin/bash

# Broker MQTT y tópico
BROKER="broker.hivemq.com"
PORT=1883
TOPIC="SCF/sejuja/data/aceleracion"

# Mensaje con 1024 muestras
MESSAGE=''

# Publicar el mensaje
mosquitto_pub -h $BROKER -p $PORT -t $TOPIC -m "$MESSAGE"
