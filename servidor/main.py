import json
import time
import logging
import paho.mqtt.client as mqtt
import os
import psycopg2
import numpy as np

# Numero de datos a recibir
NUM_DATOS = 5

# Configuramos el logger para imprimir por consola
logging.basicConfig(
    level=logging.DEBUG,  # Establece el nivel mínimo de logging
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato del log
)

# Leer las variables de entorno
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")  # Valor por defecto si no está definido
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))  # Convertimos a entero
TOPIC_ACEL = "ciberfisicos/aceleraciones"  # Tópico de aceleraciones
TOPIC_TEMP_HUM = "ciberfisicos/temp_hum" # Tópico de temperatura y humedad

# Configuración de la base de datos PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "tu_base_de_datos")
DB_USER = os.getenv("DB_USER", "tu_usuario")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tu_contraseña")

# Variables globales
aceleraciones_x = []
aceleraciones_y = []
aceleraciones_z = []
timestamps_acel = []

# Función para crear una conexión con la base de datos
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Función para almacenar los datos de aceleración en la base de datos
def store_acel_in_db(acel_x, acel_y, acel_z, timestamp):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Guardamos los datos de aceleración en la base de datos
        cur.execute(
            "INSERT INTO aceleraciones (x, y, z, timestamp) VALUES (%s, %s, %s, %s)",
            (acel_x, acel_y, acel_z, timestamp)
        )

        conn.commit()  # Confirmamos la transacción
        cur.close()
        conn.close()
        logging.info(f"Aceleraciones {[acel_x, acel_y, acel_z]} almacenadas en la base de datos con timestamp {timestamp}.")

    except Exception as e:
        logging.error(f"Error al almacenar datos de aceleración en la base de datos: {e}")

# Función para almacenar los resultados de las FFTs en la base de datos
def store_fft_in_db(fft_x, fft_y, fft_z, timestamp):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Guardamos los datos de las FFTs en la base de datos
        cur.execute(
            "INSERT INTO fft (x, y, z, timestamp) VALUES (%s, %s, %s, %s)",
            (fft_x, fft_y, fft_z, timestamp)
        )

        conn.commit()  # Confirmamos la transacción
        cur.close()
        conn.close()
        logging.info(f"Datos de las FFTs {[fft_x, fft_y, fft_z]} almacenados en la base de datos con timestamp {timestamps_acel}.")

    except Exception as e:
        logging.error(f"Error al almacenar los datos de las FFTs en la base de datos: {e}")

# Función para almacenar los resultados de las FFTs en la base de datos
def store_temp_hum_in_db(temperatura, humedad, timestamp):
    try:
        # Guardamos los datos en la base de datos
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO temperatura (temperatura, timestamp) VALUES (%s, %s)",
            (temperatura, timestamp)
        )

        cur.execute(
            "INSERT INTO humedad (humedad, timestamp) VALUES (%s, %s)",
            (humedad, timestamp)
        )

        conn.commit()  # Confirmamos la transacción
        cur.close()
        conn.close()

        logging.info(f"Datos de temperatura y humedad almacenados en la base de datos: Temperatura={temperatura}, Humedad={humedad}, Timestamp={timestamp}.")

    except Exception as e:
        logging.error(f"Error al almacenar los datos de temperatura y humedad en la base de datos: {e}")

# Funcion para gestionar un mensaje de aceleraciones
def handle_aceler(msg):

    # Parseamos el mensaje como JSON
    data = json.loads(msg.payload.decode())
        
    # Extraemos las aceleraciones y el timestamp del mensaje
    acel_x = data.get("acel_x")
    acel_y = data.get("acel_y")
    acel_z = data.get("acel_z")
    timestamp = data.get("timestamp")

    if acel_x is not None and acel_y is not None and acel_z is not None and timestamp is not None:

        # Almacenamos las aceleraciones en las listas globales
        aceleraciones_x.append(acel_x)
        aceleraciones_y.append(acel_y)
        aceleraciones_z.append(acel_z)
        timestamps_acel.append(timestamp)

        # Si hemos recibido 5 mensajes, calculamos las FFTs
        if len(aceleraciones_x) == NUM_DATOS:
            logging.info(f"Recibidos {NUM_DATOS} mensajes, calculando FFTs.")
            
            # Calculamos la FFT para cada componente de aceleración
            fft_x = [float(np.abs(val)) for val in np.fft.fft(aceleraciones_x)]
            fft_y = [float(np.abs(val)) for val in np.fft.fft(aceleraciones_y)]
            fft_z = [float(np.abs(val)) for val in np.fft.fft(aceleraciones_z)]

            # Almacenamos los resultados de la FFT en la base de datos
            for i in range(len(fft_x)):
                store_fft_in_db(fft_x[i], fft_y[i], fft_z[i], timestamps_acel[i])
            
            # Almacenamos las aceleraciones en la base de datos
            for i in range(len(aceleraciones_x)):
                store_acel_in_db(aceleraciones_x[i],
                                 aceleraciones_y[i],
                                 aceleraciones_z[i],
                                 timestamps_acel[i])

            # Limpiamos las listas para el siguiente lote de datos
            aceleraciones_x.clear()
            aceleraciones_y.clear()
            aceleraciones_z.clear()
            timestamps_acel.clear()
    else:
        logging.warning("Mensaje recibido sin datos completos de aceleraciones o timestamp")

# Función para gestionar un mensaje de temperatura y humedad
def handle_temp_hum(msg):
    try:
        # Parseamos el mensaje como JSON
        data = json.loads(msg.payload.decode())

        # Extraemos la temperatura, humedad y el timestamp del mensaje
        temperatura = data.get("temperatura")
        humedad = data.get("humedad")
        timestamp = data.get("timestamp")

        if temperatura is not None and humedad is not None and timestamp is not None:
            store_temp_hum_in_db(temperatura, humedad, timestamp)
        else:
            logging.warning("Mensaje recibido sin datos completos de temperatura, humedad o timestamp.")

    except Exception as e:
        logging.error(f"Error al almacenar datos de temperatura y humedad en la base de datos: {e}")

# Función que se llama cuando se recibe un mensaje MQTT
def on_message(client, userdata, msg):
    try:

        if msg.topic == TOPIC_ACEL:
            handle_aceler(msg)
        elif msg.topic == TOPIC_TEMP_HUM:
            handle_temp_hum(msg)

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

    # Nos suscribimos a los tópicos
    client.subscribe(TOPIC_ACEL)
    client.subscribe(TOPIC_TEMP_HUM)

    # Bucle infinito del cliente MQTT
    client.loop_forever()

if __name__ == "__main__":
    main()
