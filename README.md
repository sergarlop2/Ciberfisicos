# Trabajo de la asignatura: Sistemas Ciberfísicos y Seguridad Hardware
## Instalación
Para preparar el sistema antes de su despliegue, es necesario ejecutar el
script de inicialización **setup.sh**:

    ./setup.sh

Este script se encargará de descargar y construir las imágenes Docker necesarias,
además de inicializar la base de datos.

## Despliegue
Para desplegar el sistema basta con ejecutar:

    docker-compose up -d

## Interfaz de usuario (Grafana)
Para acceder a la interfaz de usuario hay que navegar a la siguiente url:
    **http://localhost:3000**

Las credenciales de acceso por defecto son: **admin:admin123**

Tras iniciar sesión, hay que navegar a la ruta donde están los dashboards:
    **http://localhost:3000/dashboards**

Y hacemos click en el dashboard llamado **Ciberfisicos**

Dentro de él ya deberíamos ver cuatro gráficas: Temperatura, Humedad, Aceleraciones
y FFT:

![Graficas temperatura humedad](images/graficas_temp_hum.png)

![Graficas aceleraciones](images/graficas_aceleraciones.jpeg)

## Detección de vibraciones

Cuando se detecte una vibración en el modo normal, veremos unas gráficas similares
a estas (64 muestras):

![Detección 64 muestras](images/deteccion_64.jpeg)

Y se pasará al modo continuo, tomando más muestras para realizar las FFTs (1024 muestras):

![Detección 1024 muestras](images/deteccion_1024.jpeg)

## Tests
Sin necesidad de tener la placa STM32, se pueden ejecutar algunos tests con los scripts bash
que se proporcionan para verificar el funcionamiento del sistema. Estos tests generan datos como
lo haría el STM32 y los publican en el broker MQTT. Por ejemplo, podemos simular una 
vibración de tipo seno y comprobar su FFT ejecutando el siguiente test:

    ./test_acel_seno.sh

Tras ejecutarlo, veremos las siguientes gráficas:

![Test aceleraciones seno](images/test_acel_seno.png)

## Configuraciones adicionales
En caso de que se quiera usar un broker MQTT privado (por defecto se usa el de HIVEMQ), hay que modificar
la variable de entorno **MQTT_BROKER** del servicio **servidor** del fichero **docker-compose.yml**

## Parada del sistema
Para parar el sistema hay que ejecutar:

    docker-compose down
