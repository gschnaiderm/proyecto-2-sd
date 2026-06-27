import sys
import os
import requests

def run():
    # Nos conectamos al puerto local del servidor HTTP
    server_address = os.environ.get("SERVER_ADDRESS", "http://localhost:8030")
    print(f"Estableciendo comunicación con {server_address}...")
    
    print("Escribe 'salir' para terminar el cliente.")
    
    while True:
        # Le pedimos al usuario que escriba un término a buscar en la consola
        descriptor = input("\nIngrese la palabra clave o descriptor a buscar (mínimo 3 caracteres): ")
        
        if descriptor.strip().lower() in ['salir', 'exit', 'quit']:
            print("Cerrando cliente de prueba...")
            break
            
        if len(descriptor.strip()) < 3:
            print("⚠️ Error: Por favor, ingresa al menos 3 caracteres para que la búsqueda sea efectiva.")
            print('\n\n\n')
            continue
            
        try:
            # Hacemos la llamada HTTP GET
            print("Enviando petición de búsqueda...")
            response = requests.get(f"{server_address}/api/news-descriptor", params={"descriptor": descriptor})
            
            if response.status_code != 200:
                print(f"\n❌ Error del servidor ({response.status_code}): {response.text}")
                continue

            news_results = response.json()
            
            # Mostramos los resultados devueltos por el servidor
            print("\n==============================================")
            print(f"  RESULTADOS ENCONTRADOS ({len(news_results)})")
            print("==============================================")
            
            if not news_results:
                print("No se encontraron noticias que coincidan con ese descriptor.")
                print('\n\n\n')
            else:
                for idx, item in enumerate(news_results, 1):
                    print(f"\n[{idx}] Título: {item['title']}")
                    print(f"    Noticia ID: {item['news_id']} | Categoría ID: {item['category_id']} | Creador ID: {item['user_id']}")
                    print(f"    Fecha de creación: {item['created_at']}")
                    print(f"    Contenido: {item['content']}")
                    print("-" * 46)

                print('\n==================================================================================\n\n\n')
            
        except requests.exceptions.RequestException as e:
            # Captura excepciones específicas de la petición HTTP
            print(f"\n❌ Error de conexión HTTP: {e}")

if __name__ == '__main__':
    run()
