import numpy as np
import time
import logging
import paho.mqtt.client as mqtt
import os

# Configurar el logger para imprimir en consola
logging.basicConfig(
    level=logging.DEBUG,  # Establece el nivel mínimo de logging
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato del log
)

# Leer las variables de entorno
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")  # Valor por defecto si no está definida
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))  # Convertir a entero

MQTT_TOPIC = "ciberfisicos/test"  # Topic al que se publicará el mensaje

# Crear una instancia del cliente MQTT
client = mqtt.Client()

# Conectar al broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Función principal
def main():
    A = np.array([1, 2, 3])
    B = np.array([4, 5, 6])
    i = 0

    while True:
        # Crear el mensaje
        message = f"Iteración {i}, Resultado de B-A: {B - A}"
        
        # Publicar el mensaje en el topic MQTT
        client.publish(MQTT_TOPIC, message)

        logging.info(f"Hola: {i}")
        logging.info(B - A)

        i = i + 1
        time.sleep(3)

if __name__ == "__main__":
   
    client.loop_start()
    main()