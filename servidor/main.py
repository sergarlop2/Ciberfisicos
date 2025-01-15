import json
import time
import logging
import paho.mqtt.client as mqtt
import os
import psycopg2

# Configuramos el logger para imprimir por consola
logging.basicConfig(
    level=logging.DEBUG,  # Establece el nivel mínimo de logging
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato del log
)

# Leer las variables de entorno
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")  # Valor por defecto si no está definido
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))  # Convertimos a entero
MQTT_TOPIC = "ciberfisicos/temperatura"  # Tópico al que nos suscribiremos

# Configuración de la base de datos PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "tu_base_de_datos")
DB_USER = os.getenv("DB_USER", "tu_usuario")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tu_contraseña")

# Función para crear una conexión con la base de datos
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Función que se llama cuando se recibe un mensaje MQTT
def on_message(client, userdata, msg):
    try:
        # Parseamos el mensaje como JSON
        data = json.loads(msg.payload.decode())
        
        # Extraemos la temperatura y el timestamp del mensaje
        temperatura = data.get("temperatura")
        timestamp = data.get("timestamp")

        if temperatura is not None and timestamp is not None:
            # Guardamos el valor de temperatura y el timestamp en la base de datos
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO temperatura (temperatura, timestamp) VALUES (%s, %s)",
                (temperatura, timestamp)
            )
            conn.commit()  # Confirmamos la transacción
            cur.close()
            conn.close()
            logging.info(f"Temperatura {temperatura} almacenada en la base de datos con timestamp {timestamp}")
        else:
            logging.warning("Mensaje recibido sin datos completos de temperatura o timestamp")

    except Exception as e:
        logging.error(f"Error al procesar el mensaje: {e}")

# Main
def main():
    # Creamos una instancia del cliente MQTT
    client = mqtt.Client()

    # Establecemos la función de callback para recibir los mensajes
    client.on_message = on_message

    # Nos conectamos al broker
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Nos suscribimos al tópico
    client.subscribe(MQTT_TOPIC)

    # Bucle infinito del cliente MQTT
    client.loop_forever()

if __name__ == "__main__":
    main()
