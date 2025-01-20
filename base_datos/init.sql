CREATE TABLE temperatura (
    id SERIAL PRIMARY KEY,
    temperatura FLOAT,
    timestamp TIMESTAMP
);

CREATE TABLE humedad (
    id SERIAL PRIMARY KEY,
    humedad FLOAT, 
    timestamp TIMESTAMP 
);

CREATE TABLE aceleraciones (
    id SERIAL PRIMARY KEY,
    x FLOAT,
    y FLOAT,
    z FLOAT,      
    timestamp TIMESTAMP  
);

CREATE TABLE fft (
    id SERIAL PRIMARY KEY,
    x FLOAT,
    y FLOAT,
    z FLOAT,      
    frec FLOAT  
);

