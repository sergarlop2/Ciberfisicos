import json
import time
import logging
import paho.mqtt.client as mqtt
import os
import psycopg2
import psycopg2.extras
import pytz
from datetime import datetime, timedelta
import numpy as np

# Numero de datos a recibir segun el modo
NUM_NORMAL = 64
NUM_CONTINUO = 1024

# Frecuencia de muestreo (Hz)
FREC_MUESTREO = 53

# Umbrales con histeresis
TEMP_THRESHOLD_HIGH = 30.0  # Umbral superior para temperatura
TEMP_THRESHOLD_LOW = 28.0   # Umbral inferior para temperatura
HUM_THRESHOLD_HIGH = 70.0   # Umbral superior para humedad
HUM_THRESHOLD_LOW = 65.0    # Umbral inferior para humedad

# Umbral FFT
FFT_THRESHOLD_DB = 20 # Consideramos pico como X dBs por encima del valor medio de la FFT

# Leer las variables de entorno
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")  # Valor por defecto si no está definido
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))  # Convertimos a entero
TOPIC_CONTROL_1 = "SCF/sejuja/moni/1" # Topico de control del nodo 1
TOPIC_CONTROL_2 = "SCF/sejuja/moni/2" # Topico de control del nodo 2
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
def store_acel_in_db(acel_x, acel_y, acel_z, timestamps):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Construimos una lista de tuplas con los datos
        data_to_insert = list(zip(acel_x, acel_y, acel_z, timestamps))

        # Realizamos un INSERT masivo
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO aceleraciones (x, y, z, timestamp) VALUES %s",
            data_to_insert
        )

        conn.commit()
        cur.close()
        conn.close()
        logging.info(f"Se almacenaron {len(acel_x)} muestras de aceleración en la base de datos.")
    except Exception as e:
        logging.error(f"Error al almacenar datos de aceleración en la base de datos: {e}")

# Función para almacenar los resultados de las FFTs en la base de datos
def store_fft_in_db(fft_x, fft_y, fft_z, frecs):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Eliminamos los datos existentes
        cur.execute("DELETE FROM fft")
        conn.commit()

        # Construimos una lista de tuplas con los datos
        data_to_insert = list(zip(fft_x, fft_y, fft_z, frecs))

        # Realizamos un INSERT masivo
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO fft (x, y, z, frec) VALUES %s",
            data_to_insert
        )

        conn.commit()
        cur.close()
        conn.close()
        logging.info(f"Se almacenaron {len(fft_x)} valores de FFT en la base de datos.")
    except Exception as e:
        logging.error(f"Error al almacenar valores de FFTs en la base de datos: {e}")

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
        client.publish(TOPIC_CONTROL_2, "1")

    # Modo continuo -> normal si se bajan los umbrales inferiores
    elif MODO_FUNC == 1 and (temperatura < TEMP_THRESHOLD_LOW and humedad < HUM_THRESHOLD_LOW):
        MODO_FUNC = 0
        logging.info(f"Volviendo al modo normal: Temperatura={temperatura}, Humedad={humedad}.")

        # Publicamos mensaje en modo normal
        client.publish(TOPIC_CONTROL_2, "0")
    else:
        logging.info(f"Modo actual ({'continuo' if MODO_FUNC == 1 else 'normal'}): Temperatura={temperatura}, Humedad={humedad}.")

# Función para detectar picos en la FFT y cambiar de modo
def detect_peak_and_switch_mode(fft_data, client):
    global MODO_FUNC
    detected = False

    # Calculamos el valor medio y el valor máximo de la FFT
    fft_mean = np.mean(fft_data) 
    fft_max = np.max(fft_data)
    logging.info(f"FFT_MEAN: {fft_mean} dB | FFT_MAX: {fft_max} dB | THRESHOLD: {FFT_THRESHOLD_DB} dB")

    # Si el valor máximo se aleja mucho del valor medio, consideramos que hay un pico
    if fft_max > fft_mean + FFT_THRESHOLD_DB: 
        if MODO_FUNC == 0:
            MODO_FUNC = 1
            detected = True
            # Publicamos mensaje en modo continuo
            client.publish(TOPIC_CONTROL_1, "1")
            logging.info("Detectado pico en la FFT, cambiando al modo continuo.")
    else:
        if MODO_FUNC == 1:
            MODO_FUNC = 0
            # Publicamos mensaje en modo normal
            client.publish(TOPIC_CONTROL_1, "0")
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

        aceleraciones_x = []
        aceleraciones_y = []
        aceleraciones_z = []
        timestamps_acel = []

        for sample in samples:
            timestamp_str = sample.get("t")
            aceleraciones = sample.get("a", [])

            if len(aceleraciones) != 3 or not timestamp_str:
                logging.warning(f"Muestra incompleta: {sample}")
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

        # Comprobamos si se alcanza el número minimo de datos para la FFT
        if len(aceleraciones_x) == NUM_NORMAL or len(aceleraciones_x) == NUM_CONTINUO:  
            logging.info("Calculando FFTs...")

            # Calculamos la FFT para cada componente de aceleración
            fft_x = [float(20*np.log10(np.abs(val))) for val in np.fft.fft(aceleraciones_x)]
            fft_y = [float(20*np.log10(np.abs(val))) for val in np.fft.fft(aceleraciones_y)]
            fft_z = [float(20*np.log10(np.abs(val))) for val in np.fft.fft(aceleraciones_z)]

            n = len(fft_x)

            # Obtenemos los valores de frecuencia
            frecs = np.linspace(-FREC_MUESTREO/2, FREC_MUESTREO/2, n).tolist()

            # Detectamos picos y cambiamos de modo si es necesario (solo frecuencias positivas)
            if not detect_peak_and_switch_mode(fft_x[1: n//2 + 1], client): 
                if not detect_peak_and_switch_mode(fft_y[1: n//2 + 1], client):
                    detect_peak_and_switch_mode(fft_z[1: n//2 + 1], client)

            # Hacemos el fftshift
            fft_x = np.fft.fftshift(fft_x).tolist()
            fft_y = np.fft.fftshift(fft_y).tolist()
            fft_z = np.fft.fftshift(fft_z).tolist()

            # Almacenamos los datos en la base de datos
            store_acel_in_db(aceleraciones_x, aceleraciones_y, aceleraciones_z, timestamps_acel)
            store_fft_in_db(fft_x, fft_y, fft_z, frecs)


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
    client.publish(TOPIC_CONTROL_1, "0")
    client.publish(TOPIC_CONTROL_2, "0")

    # Bucle infinito del cliente MQTT
    client.loop_forever()

if __name__ == "__main__":
    main()
