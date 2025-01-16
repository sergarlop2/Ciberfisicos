#!/bin/bash

# Configuración del locale para que use el punto como separador decimal
export LC_NUMERIC="en_US.UTF-8"

# Configuración
BROKER="broker.hivemq.com"
PORT=1883
TOPIC="ciberfisicos/aceleraciones"

# Frecuencia de la señal y número de muestras
FREQ=6  # Frecuencia de la onda senoidal en Hz
SAMPLES=64
PERIOD=$(echo "scale=6; 1 / $FREQ" | bc) # Periodo de la señal
INTERVAL=$(echo "scale=6; $PERIOD / $SAMPLES" | bc) # Intervalo entre muestras

# Generar y enviar los mensajes
START_TIME=$(date +%s.%N) # Tiempo inicial en segundos con nanosegundos
for i in $(seq 0 $((SAMPLES - 1)))
do
  # Calcular el tiempo relativo desde el inicio
  ELAPSED_TIME=$(echo "scale=6; $i * $INTERVAL" | bc)
  CURRENT_TIME=$(echo "$START_TIME + $ELAPSED_TIME" | bc)
  TIMESTAMP=$(date -u -d @$CURRENT_TIME +%Y-%m-%dT%H:%M:%S.%3NZ)

  # Calcular los valores senoidales
  X=$(printf "%.6f" $(echo "s($i * 2 * 4 * a(1) / $SAMPLES)" | bc -l))
  Y=$(printf "%.6f" $(echo "s($i * 2 * 4 * a(1) / $SAMPLES + a(1)/3)" | bc -l))
  Z=$(printf "%.6f" $(echo "s($i * 2 * 4 * a(1) / $SAMPLES + 2 * a(1)/3)" | bc -l))

  # Publicar el mensaje
  MESSAGE="{\"acel_x\": $X, \"acel_y\": $Y, \"acel_z\": $Z, \"timestamp\": \"$TIMESTAMP\"}"
  mosquitto_pub -h $BROKER -p $PORT -t $TOPIC -m "$MESSAGE"

  # Pausa entre envíos
  sleep $INTERVAL
done