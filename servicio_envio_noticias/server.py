import grpc
from concurrent import futures
import time
import logging
import queue
import threading
import os
import pika
import psycopg2

import noticias_pb2
# pyrefly: ignore [missing-import]
import noticias_pb2_grpc

class ServicioNoticiasServicer(noticias_pb2_grpc.ServicioNoticiasServicer):
    def __init__(self):
        # Diccionario para mapear: seccion -> lista_de_colas_de_clientes
        # Cada cliente conectado tendrá una cola donde se depositan las noticias a enviar
        self.suscriptores = {}  #acá guardo por ejemplo {1: [cola_juan, cola_pedro], 2: [cola_maria]}
        self.lock = threading.Lock() #por si dos personas intentan suscribirse al mismo ms

    def SuscribirASeccion(self, request, context):
        id_categoria = request.id_categoria
        cliente_id = request.cliente_id
        logging.info(f"Cliente {cliente_id} suscrito a la categoría ID: {id_categoria}")

        # Crear una cola para este cliente
        q = queue.Queue()

        with self.lock:
            if id_categoria not in self.suscriptores:
                self.suscriptores[id_categoria] = []
            self.suscriptores[id_categoria].append(q)

        try:
            # Mantener la conexión abierta y enviar noticias a medida que lleguen
            while context.is_active():
                try:
                    # Esperar por una noticia (timeout para poder chequear si el contexto sigue activo)
                    noticia = q.get(timeout=1)
                    yield noticia
                except queue.Empty:
                    continue
        except Exception as e:
            logging.error(f"Error con el cliente {cliente_id}: {e}")
        finally:
            # Cuando el cliente se desconecta, lo removemos de la lista
            with self.lock:
                if id_categoria in self.suscriptores and q in self.suscriptores[id_categoria]:
                    self.suscriptores[id_categoria].remove(q)
            logging.info(f"Cliente {cliente_id} desconectado de la categoría ID: {id_categoria}")



def rabbitmq_consumer(servicer):
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            channel.exchange_declare(exchange='noticias_exchange', exchange_type='fanout')
            
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            
            channel.queue_bind(exchange='noticias_exchange', queue=queue_name)
            
            def callback(ch, method, properties, body):
                id_noticia = int(body.decode())
                logging.info(f"Recibido ID de noticia desde RabbitMQ: {id_noticia}")
                
                try:
                    conn = psycopg2.connect(
                        host=os.getenv("DB_HOST", "db"),
                        port=os.getenv("DB_PORT", "5432"),
                        user=os.getenv("DB_USER", "admin"),
                        password=os.getenv("DB_PASSWORD", "secreta"),
                        dbname=os.getenv("DB_NAME", "sistema_db")
                    )
                    cursor = conn.cursor()
                    cursor.execute("SELECT title, user_id, category_id, content, created_at FROM news WHERE news_id = %s", (id_noticia,))
                    row = cursor.fetchone()
                    
                    if row:
                        titulo, id_autor, id_categoria, texto, fecha = row
                        with servicer.lock:
                            if id_categoria in servicer.suscriptores:
                                noti = noticias_pb2.Noticia(
                                    id_noticia=id_noticia,
                                    titulo=titulo,
                                    id_autor=id_autor,
                                    id_categoria=id_categoria,
                                    texto=texto,
                                    fecha=str(fecha)
                                )
                                for q in servicer.suscriptores[id_categoria]:
                                    q.put(noti)
                    cursor.close()
                    conn.close()
                except Exception as e:
                    logging.error(f"Error consultando BD o enviando a clientes: {e}")

            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            logging.info("RabbitMQ Consumer esperando mensajes en background...")
            channel.start_consuming()
            
        except Exception as e:
            logging.error(f"Error en RabbitMQ (reintentando en 5s): {e}")
            time.sleep(5)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ServicioNoticiasServicer()
    
    # Iniciar hilo de RabbitMQ
    threading.Thread(target=rabbitmq_consumer, args=(servicer,), daemon=True).start()
    
    noticias_pb2_grpc.add_ServicioNoticiasServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Servicio de Noticias (Suscripciones via gRPC) escuchando en el puerto 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
