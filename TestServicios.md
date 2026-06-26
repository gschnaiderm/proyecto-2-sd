# Smoke Tests de Microservicios

Esta guia sirve para probar rapidamente que cada servicio del compose raiz responde.

## Requisitos previos

- Levantar el stack con `docker compose up --build`
- Tener `curl` instalado para los servicios HTTP
- Tener `grpcurl` instalado para los servicios gRPC

## 1. `database`

Como conextarse a la base:
```bash 
docker compose exec database psql -U postgres -d database 
```
No tiene request directa porque es la base compartida. Se valida indirectamente con cualquier servicio que consulte datos.

## 2. `area-manager`

### Crear area

```bash
curl -X POST http://localhost:8080/areas \
  -H "Content-Type: application/json" \
  -d '{"name":"Sistemas Embebidos","user_id":1}'
```

### Eliminar area

```bash
curl -X DELETE http://localhost:8080/areas/Sistemas%20Embebidos \
  -H "Content-Type: application/json" \
  -d '{"user_id":1}'
```

### Health

```bash
curl http://localhost:8080/health
```

## 3. `find-news-period`

### Noticias entre dos fechas

```bash
curl "http://localhost:8010/api/news-period?fecha_inicio=2026-06-20&fecha_fin=2026-06-24"
```

### Health

```bash
curl http://localhost:8010/health
```

## 4. `last-news-24-hour`

### Noticias de las ultimas 24 horas

```bash
curl http://localhost:8012/api/news-last-24h
```

### Health

```bash
curl http://localhost:8012/health
```

## 5. `get-news-load-by-area`

### Carga de noticias por area

```bash
curl http://localhost:8011/api/news-load
```

### Health

```bash
curl http://localhost:8011/health
```

## 6. `delete-news`

### Eliminar noticia

```bash
curl -X DELETE "http://localhost:8013/noticias/1?user_id=1"
```

## 7. `find-news-by-descriptor` gRPC

### Buscar por descriptor

```bash
grpcurl -plaintext \
  -proto find-news-by-descriptor/protos/news_search.proto \
  -d '{"descriptor":"Docker"}' \
  localhost:50051 news_search.NewsSearchService/SearchByDescriptor
```

### Verificacion rapida del server

Si la busqueda no devuelve datos, probalo con un descriptor que exista en la base de prueba, por ejemplo:

```bash
grpcurl -plaintext \
  -proto find-news-by-descriptor/protos/news_search.proto \
  -d '{"descriptor":"IA"}' \
  localhost:50051 news_search.NewsSearchService/SearchByDescriptor
```

## 8. `servicio_envio_noticias` gRPC

Este servicio tiene streaming. Para probarlo hacen falta dos terminales.

### Terminal 1: suscribirse a una categoria

```bash
grpcurl -plaintext \
  -proto servicio_envio_noticias/noticias.proto \
  -d '{"cliente_id":"cliente-1","id_categoria":1}' \
  localhost:50052 noticias.ServicioNoticias/SuscribirASeccion
```

### Terminal 2: publicar una noticia

```bash
grpcurl -plaintext \
  -proto servicio_envio_noticias/noticias.proto \
  -d '{"id_noticia":100,"titulo":"Prueba","id_autor":1,"id_categoria":1,"texto":"Mensaje de prueba","fecha":"2026-06-24T12:00:00Z"}' \
  localhost:50052 noticias.ServicioNoticias/PublicarNoticia
```

## Orden recomendado de prueba

1. `database`
2. `area-manager`
3. `find-news-period`
4. `last-news-24-hour`
5. `get-news-load-by-area`
6. `delete-news`
7. `find-news-by-descriptor`
8. `servicio_envio_noticias`
