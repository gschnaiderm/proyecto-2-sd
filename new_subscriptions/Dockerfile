FROM python:3.11-slim

WORKDIR /app

# Evita que Python escriba los archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE 1
# Evita que Python guarde en el buffer las salidas de log (ves los prints en tiempo real)
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/

#dependencias
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

#resto del código del servicio
COPY . /app/

# COMPILACIÓN DEL CONTRATO: Genera los archivos _pb2.py y _pb2_grpc.py adentro del contenedor
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. subscriptions.proto

EXPOSE 50051

CMD ["python", "subscribe.py"]