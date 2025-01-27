#!/bin/bash

# Configuración MQTT
BROKER="broker.hivemq.com"
PORT=1883
TOPIC="SCF/sejuja/data/tempHum"

# Número de mensajes a enviar
MESSAGES=5

# Datos
TEMP_VALUES=("23.1" "23.7" "23.5" "23.8" "23.4")
HUM_VALUES=("55.0" "54.2" "53.1" "53.4" "52.7")

# Publicar los mensajes
for ((i=0; i<$MESSAGES; i++)); do
  # Obtener el timestamp actual
  TIMESTAMP=$(date -u +"%d-%m-%yT%H:%M:%S.000")

  # Crear el mensaje JSON
  JSON_DATA="{\"temperatura\": ${TEMP_VALUES[$i]}, \"humedad\": ${HUM_VALUES[$i]}, \"timestamp\": \"$TIMESTAMP\"}"

  # Publicar el mensaje
  mosquitto_pub -h "$BROKER" -p "$PORT" -t "$TOPIC" -m "$JSON_DATA"
  
  # Mostrar el mensaje enviado
  echo "Mensaje enviado: $JSON_DATA"

  sleep 0.5
  
done
