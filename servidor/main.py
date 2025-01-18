import json
import time
import logging
import paho.mqtt.client as mqtt
import os
import psycopg2
import pytz
from datetime import datetime, timedelta
import numpy as np

# Numero de datos a recibir segun el modo
NUM_NORMAL = 64
NUM_CONTINUO = 1024

# Umbrales con histeresis
TEMP_THRESHOLD_HIGH = 30.0  # Umbral superior para temperatura
TEMP_THRESHOLD_LOW = 28.0   # Umbral inferior para temperatura
HUM_THRESHOLD_HIGH = 70.0   # Umbral superior para humedad
HUM_THRESHOLD_LOW = 65.0    # Umbral inferior para humedad

# Umbral FFT
FFT_THRESHOLD = 10 # Consideramos pico como X veces el valor medio de la FFT

# Leer las variables de entorno
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")  # Valor por defecto si no está definido
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))  # Convertimos a entero
TOPIC_CONTROL = "SCF/sejuja/moni" # Topico de control
TOPIC_ACEL = "SCF/sejuja/data/aceleracion"  # Tópico de aceleraciones
TOPIC_TEMP_HUM = "SCF/sejuja/data/tempHum" # Tópico de temperatura y humedad

# Configuración de la base de datos PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "tu_base_de_datos")
DB_USER = os.getenv("DB_USER", "tu_usuario")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tu_contraseña")

# Configuracion de la zona horaria
MADRID_TZ = pytz.timezone(os.getenv("TZ", "Europe/Madrid"))

# Variables globales
aceleraciones_x = []
aceleraciones_y = []
aceleraciones_z = []
timestamps_acel = []
MODO_FUNC = 0 # 0 para el modo normal. 1 para el modo continuo

# Configuramos el logger para imprimir por consola
logging.basicConfig(
    level=logging.DEBUG,  # Establece el nivel mínimo de logging
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato del log
)

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
        logging.info(f"Datos de las FFTs {[fft_x, fft_y, fft_z]} almacenados en la base de datos con timestamp {timestamp}.")

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

# Función para cambiar al modo continuo con histeresis
def check_and_switch_mode(temperatura, humedad, client):
    global MODO_FUNC

    # Modo normal -> continuo si se exceden los umbrales superiores
    if MODO_FUNC == 0 and (temperatura > TEMP_THRESHOLD_HIGH or humedad > HUM_THRESHOLD_HIGH):
        MODO_FUNC = 1
        logging.info(f"Cambiando al modo continuo por temperatura={temperatura} o humedad={humedad}.")

        # Publicamos mensaje en modo continuo
        client.publish(TOPIC_CONTROL, "1")

    # Modo continuo -> normal si se bajan los umbrales inferiores
    elif MODO_FUNC == 1 and (temperatura < TEMP_THRESHOLD_LOW and humedad < HUM_THRESHOLD_LOW):
        MODO_FUNC = 0
        logging.info(f"Volviendo al modo normal: Temperatura={temperatura}, Humedad={humedad}.")

        # Publicamos mensaje en modo normal
        client.publish(TOPIC_CONTROL, "0")
    else:
        logging.info(f"Modo actual ({'continuo' if MODO_FUNC == 1 else 'normal'}): Temperatura={temperatura}, Humedad={humedad}.")

# Función para detectar picos en la FFT y cambiar de modo
def detect_peak_and_switch_mode(fft_data, client):
    global MODO_FUNC
    detected = False

    # Calculamos el valor medio y el valor máximo de la FFT
    fft_mean = np.mean(fft_data)
    fft_max = np.max(fft_data)

    # Si el valor máximo se aleja mucho del valor medio, consideramos que hay un pico
    if fft_max > fft_mean * FFT_THRESHOLD: 
        if MODO_FUNC == 0:
            MODO_FUNC = 1
            detected = True
            # Publicamos mensaje en modo continuo
            client.publish(TOPIC_CONTROL, "1")
            logging.info("Detectado pico en la FFT, cambiando al modo continuo.")
    else:
        if MODO_FUNC == 1:
            MODO_FUNC = 0
            # Publicamos mensaje en modo normal
            client.publish(TOPIC_CONTROL, "0")
            logging.info("No se detectó pico en la FFT, cambiando al modo normal.")

    return detected

# Funcion para gestionar un mensaje de aceleraciones
def handle_aceler(msg, client):

    try:
        # Parseamos el mensaje como JSON
        data = json.loads(msg.payload.decode())

        # Extraemos la longitud y las muestras
        length = data.get("l", 0)
        samples = data.get("s", [])
        
        if length != len(samples):
            logging.warning(f"La longitud del mensaje ({length}) no coincide con el número de muestras ({len(samples)}).")
            return

        for sample in samples:
            timestamp_str = sample.get("t")
            aceleraciones = sample.get("a", [])

            if len(aceleraciones) != 3 or not timestamp_str:
                logging.warning(f"Muestra incompleta: {sample}")
                aceleraciones_x.clear()
                aceleraciones_y.clear()
                aceleraciones_z.clear()
                timestamps_acel.clear()
                return

            # Convertimos el timestamp a datetime y lo asociamos con la zona horaria de Madrid
            timestamp = datetime.strptime(timestamp_str, "%d-%m-%yT%H:%M:%S.%f")
            timestamp = MADRID_TZ.localize(timestamp)
            timestamp = timestamp - timedelta(hours=1)  # Restamos una hora

            # Añadimos las aceleraciones a las listas globales
            aceleraciones_x.append(aceleraciones[0])
            aceleraciones_y.append(aceleraciones[1])
            aceleraciones_z.append(aceleraciones[2])
            timestamps_acel.append(timestamp)

            # Guardamos en la base de datos cada muestra
            store_acel_in_db(aceleraciones[0], aceleraciones[1], aceleraciones[2], timestamp)

        # Comprobamos si se alcanza el número minimo de datos para la FFT
        if len(aceleraciones_x) == NUM_NORMAL or len(aceleraciones_x) == NUM_CONTINUO:  
            logging.info("Calculando FFTs...")

            # Calculamos la FFT para cada componente de aceleración
            fft_x = [float(np.abs(val)) for val in np.fft.fft(aceleraciones_x)]
            fft_y = [float(np.abs(val)) for val in np.fft.fft(aceleraciones_y)]
            fft_z = [float(np.abs(val)) for val in np.fft.fft(aceleraciones_z)]

            # Detectamos picos y cambiamos de modo si es necesario
            if not detect_peak_and_switch_mode(fft_x, client):
                if not detect_peak_and_switch_mode(fft_y, client):
                    detect_peak_and_switch_mode(fft_z, client)

            # Almacenamos los resultados de la FFT en la base de datos
            for i in range(len(fft_x)):
                store_fft_in_db(fft_x[i], fft_y[i], fft_z[i], timestamps_acel[i])

        # Limpiamos las listas para el próximo lote
        aceleraciones_x.clear()
        aceleraciones_y.clear()
        aceleraciones_z.clear()
        timestamps_acel.clear()

    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar JSON: {e}")
    except Exception as e:
        logging.error(f"Error al procesar mensaje de aceleración: {e}")

# Función para gestionar un mensaje de temperatura y humedad
def handle_temp_hum(msg, client):
    try:
        # Parseamos el mensaje como JSON
        data = json.loads(msg.payload.decode())

        # Extraemos la temperatura, humedad y el timestamp del mensaje
        temperatura = data.get("temperatura")
        humedad = data.get("humedad")
        timestamp_str = data.get("timestamp")

        if temperatura is not None and humedad is not None and timestamp_str is not None:
            # Convertimos el timestamp a datetime y lo asociamos con la zona horaria de Madrid
            timestamp = datetime.strptime(timestamp_str, "%d-%m-%yT%H:%M:%S.%f")
            timestamp = MADRID_TZ.localize(timestamp)
            timestamp = timestamp - timedelta(hours=1)  # Restamos una hora

            # Guardamos los datos en la base de datos
            store_temp_hum_in_db(temperatura, humedad, timestamp)

            # Verificar y cambiar al modo según los umbrales con histeresis
            check_and_switch_mode(temperatura, humedad, client)
        else:
            logging.warning("Mensaje recibido sin datos completos de temperatura, humedad o timestamp.")

    except Exception as e:
        logging.error(f"Error al almacenar datos de temperatura y humedad en la base de datos: {e}")

# Función que se llama cuando se recibe un mensaje MQTT
def on_message(client, userdata, msg):
    try:

        if msg.topic == TOPIC_ACEL:
            handle_aceler(msg, client)
        elif msg.topic == TOPIC_TEMP_HUM:
            handle_temp_hum(msg, client)

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

    # Por defecto, publicamos mensaje en modo normal
    client.publish(TOPIC_CONTROL, "0")

    # Bucle infinito del cliente MQTT
    client.loop_forever()

if __name__ == "__main__":
    main()
