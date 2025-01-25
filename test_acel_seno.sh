#!/bin/bash

# Configuración MQTT
BROKER="broker.hivemq.com"
PORT=1883
TOPIC="SCF/sejuja/data/aceleracion"

# Parámetros
SAMPLES=1024         # Número de muestras
FREQ_HZ=6            # Frecuencia del seno en Hz
FS=50                # Frecuencia de muestreo (Hz)
AMPLITUDE=250        # Amplitud del seno
START_TIME=$(date -u +"%d-%m-%yT%H:%M:%S.%3N")

# Generar datos
JSON_DATA="{\"l\":$SAMPLES,\"s\":["  
START_TIMESTAMP=$(date -u --date="$START_TIME" +%s.%3N)
for ((i=0; i<$SAMPLES; i++)); do
  # Calcular el timestamp válido
  CURRENT_TIMESTAMP=$(echo "$START_TIMESTAMP + $i / $FS" | bc -l)
  FORMATTED_TIMESTAMP=$(date -u -d@"$CURRENT_TIMESTAMP" +"%d-%m-%yT%H:%M:%S.%3N")

  # Calcular el valor del seno
  VALUE=$(awk -v amp=$AMPLITUDE -v freq=$FREQ_HZ -v fs=$FS -v i=$i \
    'BEGIN {printf "%d", amp * sin(2 * 3.14159265359 * freq * i / fs) + 500}')
  
  # Añadir rizado aleatorio al seno (muy pequeño)
  RANDOM_NOISE_SINE=$(awk -v min=-2 -v max=2 'BEGIN{srand(); print min + (max-min+1)*rand()}')
  VALUE=$(echo "$VALUE + $RANDOM_NOISE_SINE" | bc)

  # Añadir rizado aleatorio a los valores 100 y 200
  RANDOM_NOISE_100=$(awk -v min=-5 -v max=5 'BEGIN{srand(); print int(min + (max-min+1)*rand())}')
  RANDOM_NOISE_200=$(awk -v min=-5 -v max=5 'BEGIN{srand(); print int(min + (max-min+1)*rand())}')
  VALUE_100=$((100 + RANDOM_NOISE_100))
  VALUE_200=$((200 + RANDOM_NOISE_200))

  # Agregar al JSON
  JSON_DATA+="{\"t\":\"$FORMATTED_TIMESTAMP\",\"a\":[$VALUE,$VALUE_100,$VALUE_200]}"
  if (( i < SAMPLES - 1 )); then
    JSON_DATA+=","
  fi
done
JSON_DATA+="]}"

# Publicar mensaje
echo "Publicando mensaje JSON al broker MQTT..."
mosquitto_pub -h "$BROKER" -p "$PORT" -t "$TOPIC" -m "$JSON_DATA"

# Mostrar salida
echo "Mensaje publicado correctamente:"
echo "$JSON_DATA"
