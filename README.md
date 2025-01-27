# Trabajo de la asignatura: Sistemas Ciberfísicos y Seguridad Hardware
## Instalación
Para preparar el sistema antes de su despliegue, es necesario ejecutar el
script de inicialización **setup.sh**:

    ```bash
    ./setup.sh

Este script se encargará de descargar y construir las imágenes Docker necesarias,
además de inicializar la base de datos.

## Despliegue
Para desplegar el sistema, basta con ejecutar:

    ```bash
    docker-compose up -d

## Interfaz de usuario (Grafana)
Para acceder a la interfaz de usuario hay que navegar a la siguiente url:
    **http://localhost:3000**

Las credenciales de acceso por defecto son: **admin:admin123**

Tras iniciar sesión, hay que navegar a la ruta donde están los dashboards:
    **http://http://localhost:3000/dashboards

Y hacemos click en el dashboard llamado **Ciberfisicos**

Dentro de él ya deberíamos ver cuatro gráficas: Temperatura, Humedad, Aceleraciones,
y FFT

## Parada del sistema
Para parar el sistema hay que ejecutar:

    ```bash
    docker-compose down
