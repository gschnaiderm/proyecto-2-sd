import grpc
from concurrent import futures
import noticias_pb2
import noticias_pb2_grpc

class ReceptorNoticiasServicer(noticias_pb2_grpc.ReceptorNoticiasServicer):
    
    
    def EnviarNoticia(self, request, context):
        print(f"\n[+] ¡Llegó una nueva noticia!")
        print(f"ID Noticia: {request.id_noticia}")
        print(f"Título: {request.titulo}")
        print(f"ID Autor: {request.autor_id}")
        print(f"Categoria: {request.id_categoria}")
        print(f"Contenido: {request.texto}")
        print(f"Fecha: {request.fecha}")
        
        # Pendiente: Conectar y guardar en la base de datos centralizada
        print("-> Guardando en la base de datos...")
        
        # Pendiente: Hacer llamado gRPC al segundo servicio (Gonzalo_A)
        print("-> Avisando al servicio de distribución de noticias...")

        # Responder al balanceador o cliente que todo salió perfecto
        return noticias_pb2.Respuesta(
            exito=True, 
            mensaje="La noticia fue recibida y guardada exitosamente."
        )

def serve():
    # Creamos el servidor gRPC con capacidad para 10 hilos concurrentes
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Vinculamos los trabajadores al servidor
    noticias_pb2_grpc.add_ReceptorNoticiasServicer_to_server(ReceptorNoticiasServicer(), servidor)
    
    # Lo ponemos a escuchar en el puerto 50051 (Estandar para gRPC)
    puerto = '50051'
    servidor.add_insecure_port(f'[::]:{puerto}')
    print(f"Servidor de Recepción de Noticias encendido y escuchando en el puerto {puerto}...")
    
    servidor.start()
    servidor.wait_for_termination()

if __name__ == '__main__':
    serve()