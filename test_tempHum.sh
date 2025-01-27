#!/bin/bash

# Configuración MQTT
BROKER="broker.hivemq.com"
PORT=1883
TOPIC="SCF/sejuja/data/tempHum"

# Número de mensajes a enviar
MESSAGES=5

# Datos
TEMP_VALUES=("22.5" "23.0" "21.8" "22.2" "21.5")
HUM_VALUES=("55.0" "56.0" "54.5" "53.8" "52.3")

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
  
  # Esperar un intervalo entre los mensajes
  sleep 1
done
