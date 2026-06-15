# Contexto del Proyecto

## Estado General
Este es el "Proyecto 2" para la materia Sistemas Distribuidos (2026). El sistema está diseñado en torno a una arquitectura de publicación y suscripción de noticias/novedades clasificadas por áreas/categorías. Actualmente el proyecto cuenta con la estructura inicial de base de datos relacional y configuración de contenedor PostgreSQL listos.

## Arquitectura y Decisiones
- **Base de Datos**: PostgreSQL 16 sobre Alpine Linux (configurado vía Docker).
- **Esquema de Base de Datos**:
  - `users`: Usuarios creadores y suscriptores del sistema.
  - `areas`: Categorías/áreas temáticas gestionadas por un usuario.
  - `subscriptions`: Relación intermedia de suscripciones de usuarios a áreas temáticas.
  - `news`: Noticias publicadas por usuarios en áreas específicas.
- **Estructura de Carpetas**:
  - `database/`: Contenedor y scripts SQL de inicialización.
    - `Dockerfile`: Configuración del contenedor Postgres 16 Alpine con locale en español (`es_AR.utf8`).
    - `scripts/`: Scripts de inicialización de esquema (`01-scheme.sql`) y datos de prueba (`02-test-data.sql`).
  - Documentación de especificación técnica del proyecto (`Modelo.pdf`, `SegundoProyecto-2026 (1).pdf`).

## Tareas Completadas (Recientes)
- [x] Configuración del Dockerfile para el servicio de base de datos PostgreSQL 16.
- [x] Diseño del esquema inicial de base de datos (tablas: `users`, `areas`, `subscriptions`, `news`).
- [x] Configuración de datos ficticios de testeo para verificar llaves foráneas y flujos de inserción.
- [x] Actualización del archivo `.gitignore` para permitir el seguimiento de `AIContext.md`.

## Próximos Pasos (TODO)
- [ ] Implementar la API/servidor backend (ej. Go, Node/TypeScript, o Java) para interactuar con la base de datos distribuidamente.
- [ ] Definir el protocolo de comunicación entre los nodos distribuidos (ej. gRPC, REST, o WebSockets).
- [ ] Implementar la lógica de brokers de mensajería o publicación/suscripción (Pub/Sub).
- [ ] Desarrollar clientes interactivos para probar la publicación y recepción de noticias en tiempo real.

## Problemas Abiertos o Notas
- Asegurarse de levantar el contenedor Postgres exponiendo el puerto estándar `5432` y usar variables de entorno seguras para credenciales de acceso local.
