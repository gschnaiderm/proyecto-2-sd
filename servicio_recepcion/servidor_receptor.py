import grpc
from concurrent import futures
import psycopg2
import noticias_pb2
import noticias_pb2_grpc

class ReceptorNoticiasServicer(noticias_pb2_grpc.ReceptorNoticiasServicer):
    
    def EnviarNoticia(self, request, context):
        print(f"\n[+] ¡Llegó una nueva noticia!")
        print(f"ID Noticia: {request.id_noticia}")
        print(f"Título: {request.titulo}")
        print(f"ID Autor: {request.id_autor}")
        print(f"Categoria: {request.id_categoria}")
        print(f"Contenido: {request.texto}")
        print(f"Fecha: {request.fecha}")
        
        print("Guardando en la base de datos...")
        try:
            conexion = psycopg2.connect(
                host="host.docker.internal",      
                database="noticias_db", 
                user="postgres",       
                password="admin"       
            )
            cursor = conexion.cursor()
            
            insert_query = """
                INSERT INTO news (title, user_id, category_id, content)
                VALUES (%s, %s, %s, %s)
                RETURNING news_id;
            """
            datos_a_insertar = (request.titulo, request.id_autor, request.id_categoria, request.texto)
            
            cursor.execute(insert_query, datos_a_insertar)
            nuevo_id = cursor.fetchone()[0]
            
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"[ÉXITO] Noticia guardada correctamente con ID: {nuevo_id}")

        except Exception as e:
            print(f"[ERROR] No se pudo guardar en la base de datos. Detalle: {e}")
            # Cortamos el flujo acá y devolvemos el error real al cliente
            return noticias_pb2.Respuesta(
                exito=False, 
                mensaje=f"Error interno: No se pudo persistir la noticia en la base de datos centralizada."
            )
        
        # Hacer llamado gRPC al segundo servicio (Gonzalo_A)
        print("Avisando al servicio de distribución de noticias...")
        try:
            # Nos conectamos al puerto de Gonzalo (50051)
            # Nota: En Docker Compose, 'localhost' cambiará al nombre de su contenedor (ej: 'servicio_noticias')
            with grpc.insecure_channel('localhost:50051') as canal_gonza:
                # Instanciamos el Stub (control remoto) del servicio de Gonzalo
                stub_gonza = noticias_pb2_grpc.ServicioNoticiasStub(canal_gonza)
                
                # Armamos el paquete usando la data original, pero inyectando el ID real de Postgres
                noticia_a_repartir = noticias_pb2.Noticia(
                    id_noticia=nuevo_id,
                    titulo=request.titulo,
                    id_autor=request.id_autor,
                    id_categoria=request.id_categoria,
                    texto=request.texto,
                    fecha="" # La fecha se autogeneró en la DB, Gonza no la filtra, así que viaja vacía
                )
                
                # Disparamos la función PublicarNoticia de Gonzalo
                respuesta_gonza = stub_gonza.PublicarNoticia(noticia_a_repartir)
                print(f"[ÉXITO DISTRIBUCIÓN] Gonzalo respondió: {respuesta_gonza.mensaje}")
                
        except Exception as error_distribucion:
            # Si el servicio de Gonza está apagado, lo atrapamos acá para que nuestro servidor no muera.
            # OJO: La noticia YA se guardó en la base de datos, así que no frenamos el proceso general.
            print(f"[AVISO] La noticia se guardó, pero falló el aviso a distribución. Detalle: {error_distribucion}")

        # Responder al cliente que todo salio bien
        return noticias_pb2.Respuesta(
            exito=True, 
            mensaje=f"La noticia '{request.titulo}' fue recibida y guardada exitosamente con ID {nuevo_id}."
        )

def serve():
    # Creamos el servidor gRPC con capacidad para 10 hilos concurrentes
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Vinculamos los trabajadores al servidor
    noticias_pb2_grpc.add_ReceptorNoticiasServicer_to_server(ReceptorNoticiasServicer(), servidor)
    
    # Lo ponemos a escuchar en el puerto 50050 (Estandar para gRPC)
    puerto = '50050'
    servidor.add_insecure_port(f'[::]:{puerto}')
    print(f"Servidor de Recepción de Noticias encendido y escuchando en el puerto {puerto}...")
    
    servidor.start()
    servidor.wait_for_termination()

if __name__ == '__main__':
    serve()