# Consorcio de Noticias - Sistemas Distribuidos (2026)

Este repositorio contiene el proyecto práctico para la materia **Sistemas Distribuidos (2do Cuatrimestre 2026)**. La arquitectura del sistema consiste en un conjunto de microservicios independientes y desacoplados que cooperan para formar un consorcio de noticias distribuido.

---

## 🏛️ Microservicios del Proyecto

A continuación, se detalla la funcionalidad, estructura y cómo desplegar cada uno de los microservicios implementados:

### 1. Base de Datos (`database`)

- **Funcionalidad:** Base de datos PostgreSQL centralizada. Provee los esquemas iniciales y datos de prueba para los microservicios.
- **Estructura:** Contiene los scripts SQL de inicialización en la carpeta `scripts/` y su propio `docker-compose.yml` para levantar la instancia en el puerto `5432`.
- **Despliegue:**
  ```bash
  docker compose -f database/docker-compose.yml up -d
  ```

### 2. Buscar Noticias por Descriptor (`news_search`)

- **Funcionalidad:** Servicio gRPC (Python) que busca noticias a partir de un descriptor (mínimo 3 caracteres), utilizando _PostgreSQL Full-Text Search_ para optimizar coincidencias ignorando conectores o plurales.
- **Estructura:** Código plano sin subcarpetas innecesarias. Archivos ubicados en la raíz de `news_search/` (cliente interactivo, servidor gRPC y scripts de DB).
- **Despliegue:** (Requiere la base de datos central iniciada primero)
  ```bash
  docker compose -f news_search/docker-compose.yml up -d --build
  ```
  _Para probar el cliente interactivo localmente, se puede utilizar el shortcut `.\find-news-by-descriptor\run_client.bat`._

### 3. Gestión de Áreas (`area-manager`)

- **Funcionalidad:** API REST (Go) encargada de la gestión (creación y eliminación) de áreas o categorías temáticas.
- **Estructura:** Código fuente unificado en `main.go`. Incluye un `test.bash` para probar los endpoints interactuando con la API.
- **Despliegue:** (Requiere la base de datos central iniciada primero)
  ```bash
  docker compose -f area-manager/docker-compose.yml up -d --build
  ```

### 4. Búsqueda de Noticias por Período (`find_news_period`)

- **Funcionalidad:** Servicio (Python) para obtener noticias publicadas dentro de un rango de tiempo específico.
- **Estructura:** API desarrollada en Python, con los archivos fuente directamente en la raíz de la carpeta.
- **Despliegue:** Cuenta con su propio archivo Compose que levanta una instancia local de la base de datos junto con el servicio (expone el puerto `8000`):
  ```bash
  docker compose -f find_news_period/docker-compose.yml up -d --build
  ```

### 5. Carga de Noticias por Área (`get-news-load-by-area`)

- **Funcionalidad:** Servicio (Python) que proporciona estadísticas sobre la cantidad de noticias publicadas por cada área temática.
- **Estructura:** API en Python con sus scripts ubicados de forma plana en la raíz de su respectiva carpeta.
- **Despliegue:** Utiliza su propio archivo Compose que, de igual manera, levanta la base de datos y el servicio (expone el puerto `8000`):
  ```bash
  docker compose -f get-news-load-by-area/docker-compose.yml up -d --build
  ```

---

## 🛑 Detener los Servicios

Para apagar los entornos que utilizan Docker Compose:

```bash
docker compose -f <carpeta>/docker-compose.yml down
```
