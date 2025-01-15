import numpy as np
import time
import logging

# Configurar el logger para imprimir en consola
logging.basicConfig(
    level=logging.DEBUG,  # Establece el nivel mínimo de logging
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato del log
)

def main():
   A = np.array([1, 2, 3])
   B = np.array([4, 5, 6])
   i = 0

   while True:

      logging.info(f"Hola: {i}")
      logging.info(B-A)
      i = i + 1
      time.sleep(3)

if __name__ == "__main__":
   main()
