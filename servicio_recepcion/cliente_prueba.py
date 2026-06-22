import grpc
import noticias_pb2
import noticias_pb2_grpc

def enviar_noticia_cliente():
    print("--- Simulador de Cliente ---")
    
    # Usamos IDs que REALMENTE existen en la base de datos centralizada
    id_cliente_actual = 7  # 7 = 'Estudiante Ing'
    categoria_destino = 6  # 6 = 'Sistemas Distribuidos'
    
    print(f"[*] Usuario ID {id_cliente_actual} preparando noticia para la categoría {categoria_destino}...")
    
    # El bloque 'with' abre el canal y garantiza que se cierre automáticamente
    # al terminar de usarse, liberando los recursos de red de la computadora.
    with grpc.insecure_channel('localhost:50050') as canal:
        cliente = noticias_pb2_grpc.ReceptorNoticiasStub(canal)
        
        # Empaquetamos la noticia.
        # Nota: Ya no mandamos id_noticia ni fecha. Si no los ponemos, gRPC los manda vacíos, 
        # y nuestro servidor directamente los ignora porque confía en PostgreSQL para generarlos.
        noticia_request = noticias_pb2.Noticia(
            titulo="Nuevas fechas para las entregas de gRPC",
            id_autor=id_cliente_actual,
            id_categoria=categoria_destino,
            texto="Se habilitó el entorno de pruebas para validar los microservicios antes de subirlos a los contenedores."
        )
        
        print("[*] Enviando paquete por la red...")
        
        try:
            respuesta = cliente.EnviarNoticia(noticia_request)
            print("\n[+] --- RESPUESTA DEL SERVIDOR ---")
            print(f"    Éxito: {respuesta.exito}")
            print(f"    Mensaje: {respuesta.mensaje}")
            print("----------------------------------")
        except grpc.RpcError as e:
            print("\n[-] Error de conexión. ¿Está encendido el servidor?")
            print(f"    Detalle técnico: {e.details()}")

if __name__ == '__main__':
    enviar_noticia_cliente()