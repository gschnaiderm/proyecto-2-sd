import os
import grpc
from concurrent import futures
import psycopg2
from psycopg2.extras import RealDictCursor

# los .proto
import subscriptions_pb2
import subscriptions_pb2_grpc

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "noticias_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgrespassword")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"Error de conexión a la base de datos: {str(e)}")
        raise e

# CLASE QUE IMPLEMENTA TODOS LOS MÉTODOS DEL SERVICIO DE SUSCRIPCIÓN
class SubscriptionServicer(subscriptions_pb2_grpc.SubscriptionServiceServicer):

    # Suscribe un cliente a un área
    def Subscribe(self, request, context):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # 1. Verificar si el área existe en la base de datos
            cur.execute("SELECT name FROM areas WHERE category_id = %s;", (request.category_id,))
            area = cur.fetchone()

            if not area:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    f"El área {request.category_id} no existe."
                )

            # 2. Verificar si existe el usuario en la base de datos
            cur.execute("SELECT user_id FROM users WHERE user_id = %s;", (request.user_id,))
            user_exists = cur.fetchone()

            if not user_exists:  # si no existe lo creamos (ESTO DEBERÍA SER UN SERVICIO APARTE)
                cur.execute(
                    "INSERT INTO users (user_id, name) VALUES (%s, %s);",
                    (request.user_id, f"Usuario generado automáticamente {request.user_id}")
                )

            # 3. Suscribir al cliente
            cur.execute(
                "INSERT INTO subscriptions (user_id, category_id) VALUES (%s, %s);",
                (request.user_id, request.category_id),
            )

            conn.commit()
            return subscriptions_pb2.SubscriptionResponse(
                message=f"El usuario {request.user_id} se suscribió a '{area['name']}'.",
                success=True
            )

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "El usuario ya está suscrito a esta categoría.")
        except psycopg2.errors.ForeignKeyViolation as e:
            conn.rollback()
            context.abort(grpc.StatusCode.NOT_FOUND, f"Error de clave foránea: {str(e)}")
        except Exception as e:
            conn.rollback()
            context.abort(grpc.StatusCode.INTERNAL, f"Error interno del servidor: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def Unsubscribe(self, request, context):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "DELETE FROM subscriptions WHERE user_id = %s AND category_id = %s;",
                (request.user_id, request.category_id),
            )
            affected_rows = cur.rowcount
            conn.commit()

            if affected_rows == 0:
                context.abort(grpc.StatusCode.NOT_FOUND, "La suscripción no existe.")

            return subscriptions_pb2.SubscriptionResponse(
                message=f"El usuario {request.user_id} se desuscribió de la categoría {request.category_id}.",
                success=True
            )
        except Exception as e:
            conn.rollback()
            context.abort(grpc.StatusCode.INTERNAL, f"Error interno del servidor: {str(e)}")
        finally:
            cur.close()
            conn.close()

    #obtener todas las suscripciones de un cliente
    def GetSubscriptions(self, request, context):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                SELECT s.category_id, a.name
                FROM subscriptions s
                LEFT JOIN areas a ON s.category_id = a.category_id
                WHERE s.user_id = %s;
                """,
                (request.user_id,)
            )
            rows = cur.fetchall()

            result_list = [
                subscriptions_pb2.CategoryInfo(
                    category_id=row["category_id"],
                    name=row["name"] or "Área externa o sin mapear"
                )
                for row in rows
            ]

            return subscriptions_pb2.SubscriptionList(
                user_id=request.user_id,
                subscriptions=result_list
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error interno del servidor: {str(e)}")
        finally:
            cur.close()
            conn.close()

# INICIO DEL SERVIDOR gRPC
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    subscriptions_pb2_grpc.add_SubscriptionServiceServicer_to_server(SubscriptionServicer(), server)

    server.add_insecure_port('[::]:50051')
    print("Servicio iniciado y escuchando en el puerto 50051...")

    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
