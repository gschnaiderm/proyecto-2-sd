-- ==============================================================================
-- 1. POBLAR USUARIOS (10 Usuarios con distintos perfiles)
-- ==============================================================================
INSERT INTO users (user_id, name) VALUES 
(1, 'Carlos Alberto Solari'), (2, 'Admin Deportes'), (3, 'Lector Frecuente'), 
(4, 'Usuario Inactivo'), (5, 'Periodista Tech'), (6, 'Analista Económico'),
(7, 'Estudiante Ing'), (8, 'Profesor Sistemas'), (9, 'Admin Cultura'),
(10, 'Lector Fantasma');

-- ==============================================================================
-- 2. POBLAR ÁREAS/CATEGORÍAS (8 Áreas)
-- ==============================================================================
INSERT INTO areas (category_id, name, user_id) VALUES 
(1, 'Tecnología y UNS', 1), (2, 'Deportes Universitarios', 2),
(3, 'Cultura y Recitales', 9), (4, 'Economía Nacional', 6),
(5, 'Investigación IA', 5), (6, 'Sistemas Distribuidos', 8),
(7, 'Centro de Estudiantes', 7), (8, 'Área Vacía (Pruebas)', 1);

-- ==============================================================================
-- 3. POBLAR SUSCRIPCIONES (20 Suscripciones cruzadas)
-- ==============================================================================
INSERT INTO subscriptions (user_id, category_id) VALUES 
(1, 1), (1, 2), (1, 3), (1, 5), (1, 6), -- Carlos lee mucho
(2, 2), (2, 7),                         -- Admin deportes
(3, 1), (3, 3), (3, 4), (3, 6),         -- Lector intensivo
(5, 1), (5, 5), (5, 6),                 -- Interesados en Tech
(6, 4), (7, 1), (7, 2), (7, 7), (8, 6), (9, 3);

-- ==============================================================================
-- 4. POBLAR NOTICIAS (Inyección masiva)
-- ==============================================================================

-- BLOQUE A: NOTICIAS ULTRA FRESCAS (Últimas 5 horas) - Para probar filtros de 24hs
INSERT INTO news (news_id, title, user_id, category_id, content, created_at) VALUES 
(1, 'Nuevas integraciones para Home Assistant', 1, 1, 'Se publicaron actualizaciones para ESPHome.', NOW() - INTERVAL '1 hour'),
(2, 'Resultados de los 31° Juegos', 2, 2, 'Resumen de las competencias realizadas esta tarde.', NOW() - INTERVAL '2 hours'),
(3, 'Caída de los mercados asiáticos', 6, 4, 'El índice Nikkei cerró con una baja histórica.', NOW() - INTERVAL '4 hours'),
(4, 'Lanzamiento del nuevo modelo de LLM', 5, 5, 'OpenAI anuncia un modelo con ventana de contexto infinita.', NOW() - INTERVAL '3 hours'),
(5, 'Reunión del Centro de Estudiantes', 7, 7, 'Hoy a las 18hs se debate el nuevo plan de estudios.', NOW() - INTERVAL '30 minutes');

-- BLOQUE B: NOTICIAS DEL DÍA ANTERIOR (Entre 12 y 24 horas)
INSERT INTO news (news_id, title, user_id, category_id, content, created_at) VALUES 
(6, 'Confirmaciones para el Lollapalooza', 9, 3, 'Nuevos cabezas de cartel para el festival.', NOW() - INTERVAL '18 hours'),
(7, 'Docker Swarm vs Kubernetes en 2026', 8, 6, 'Análisis de orquestación para proyectos universitarios.', NOW() - INTERVAL '20 hours'),
(8, 'Torneo de básquet suspendido', 2, 2, 'Por goteras en el estadio de la UNS.', NOW() - INTERVAL '23 hours');

-- BLOQUE C: NOTICIAS ANTIGUAS (Para probar búsquedas históricas)
INSERT INTO news (news_id, title, user_id, category_id, content, created_at) VALUES 
(9, 'Resumen del CLEI 2024', 1, 1, 'Un repaso por las conferencias realizadas en Bahía Blanca.', NOW() - INTERVAL '45 days'),
(10, 'Inflación del mes pasado', 6, 4, 'Los índices superaron las expectativas.', NOW() - INTERVAL '30 days'),
(11, 'Avances en Shaders 3D', 1, 1, 'Implementación de Blinn-Phong en Unity.', NOW() - INTERVAL '15 days'),
(12, 'Concierto de rock local', 9, 3, 'Gran convocatoria en el centro de la ciudad.', NOW() - INTERVAL '40 days'),
(13, 'Clase especial de gRPC', 8, 6, 'Patrones de comunicación remota y directa.', NOW() - INTERVAL '10 days'),
(14, 'Nuevas becas de comedor', 7, 7, 'Se abre la inscripción para el segundo cuatrimestre.', NOW() - INTERVAL '60 days');

-- BLOQUE D: NOTICIAS PARA PRUEBAS DE DESCRIPTORES Y BORRADO (Edge cases)
INSERT INTO news (news_id, title, user_id, category_id, content, created_at) VALUES 
(15, 'Noticia con palabra clave secreta: XQZ99', 3, 4, 'Solo para testear el buscador exacto.', NOW() - INTERVAL '5 days'),
(16, 'Noticia de prueba para ser borrada', 2, 2, 'El admin de deportes debería poder borrar esto, pero German no.', NOW() - INTERVAL '2 days');

-- ==============================================================================
-- 5. REINICIO DE SECUENCIAS (EL TRUCO DE LA INDUSTRIA)
-- ==============================================================================
-- Como forzamos los IDs (1, 2, 3...) a mano, las secuencias automáticas de Postgres 
-- se quedaron trabadas en 1. Las adelantamos a 100 para que tus futuros INSERTs 
-- desde la aplicación funcionen perfecto.

ALTER SEQUENCE users_user_id_seq RESTART WITH 100;
ALTER SEQUENCE areas_category_id_seq RESTART WITH 100;
ALTER SEQUENCE news_news_id_seq RESTART WITH 100;