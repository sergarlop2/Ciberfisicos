FROM python:3.9-slim
RUN pip install --no-cache-dir numpy psycopg2-binary
WORKDIR /src
COPY main.py .
CMD ["python3", "main.py"]
