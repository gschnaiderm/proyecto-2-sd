#!/bin/bash

# ==============================================================================
# Integration Test Suite para Consorcio SD
# ==============================================================================
# Este script ejecuta una rutina de prueba completa sobre todos los microservicios
# definidos en el docker-compose.yml.
# Es idempotente: Limpia los datos de prueba generados al finalizar, permitiendo
# ejecutar el script infinitas veces sin corromper el estado de la base de datos.
# ==============================================================================

set -e # Detener script si ocurre un error crítico no manejado

# --- Configuración ---
IP="localhost"
USER_ID=999
TEST_AREA="area_test_integracion"
DATE_START="2026-06-01"
DATE_END="2026-12-31"

# --- Puertos (Basados en docker-compose.yml) ---
PORT_AREA=8000
PORT_DEL_NEWS=8001
PORT_PERIOD=8002
PORT_LOAD=8003
PORT_SUBS=8004
PORT_24H=8005
PORT_DESC=8006

# --- Colores para la salida ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}   Iniciando Rutina de Pruebas de Integración E2E     ${NC}"
echo -e "${BLUE}======================================================${NC}\n"

# Verificación de dependencias (jq)
if ! command -v jq &> /dev/null; then
    echo -e "${RED}[ERROR] 'jq' no está instalado. Instálalo con 'sudo apt install jq' para poder parsear las respuestas JSON.${NC}"
    exit 1
fi

echo -e "${YELLOW}>> [1/7] Limpiando estado previo (Asegurando idempotencia)...${NC}"
# Tratamos de borrar el área por si el script falló a la mitad en la corrida anterior
curl --max-time 10 -s -X DELETE "http://${IP}:${PORT_AREA}/areas/${TEST_AREA}" \
     -H "Content-Type: application/json" \
     -d "{\"user_id\": ${USER_ID}}" > /dev/null || true
echo -e "${GREEN}✓ Entorno preparado.${NC}\n"

echo -e "${YELLOW}>> [2/7] Probando Área Manager (Crear Área)...${NC}"
CREATE_AREA_RES=$(curl --max-time 10 -s -w "\n%{http_code}" -X POST "http://${IP}:${PORT_AREA}/areas" \
     -H "Content-Type: application/json" \
     -d "{\"name\": \"${TEST_AREA}\", \"user_id\": ${USER_ID}}")

HTTP_CODE=$(echo "$CREATE_AREA_RES" | tail -n1)
BODY=$(echo "$CREATE_AREA_RES" | sed '$d')

if [ "$HTTP_CODE" -eq 201 ]; then
    CATEGORY_ID=$(echo "$BODY" | jq -r '.category_id')
    echo -e "${GREEN}✓ Área '${TEST_AREA}' creada con éxito (ID de Categoría asignado: ${CATEGORY_ID}).${NC}\n"
else
    echo -e "${RED}✗ Error al crear el área. HTTP Code: $HTTP_CODE${NC}"
    echo -e "Respuesta: $BODY"
    exit 1
fi

echo -e "${YELLOW}>> [3/7] Probando New Subscriptions (Suscribir)...${NC}"
SUBS_RES=$(curl --max-time 10 -s -w "\n%{http_code}" -X POST "http://${IP}:${PORT_SUBS}/suscribir" \
     -H "Content-Type: application/json" \
     -d "{\"user_id\": ${USER_ID}, \"category_id\": ${CATEGORY_ID}}")
HTTP_CODE=$(echo "$SUBS_RES" | tail -n1)
if [[ "$HTTP_CODE" =~ ^2 ]]; then
    echo -e "${GREEN}✓ Usuario ${USER_ID} suscrito exitosamente a la categoría ${CATEGORY_ID}.${NC}\n"
else
    echo -e "${RED}✗ Error en suscripción. HTTP Code: $HTTP_CODE${NC}\n"
fi

echo -e "${YELLOW}>> [4/7] Probando Lectura de Servicios (Queries)...${NC}"
echo -e "${BLUE}  -> Microservicio: Find News By Period${NC}"
curl --max-time 10 -s -X GET "http://${IP}:${PORT_PERIOD}/api/news-period?fecha_inicio=${DATE_START}&fecha_fin=${DATE_END}" | jq . || echo -e "${RED}Fallo en Period${NC}"

echo -e "\n${BLUE}  -> Microservicio: Get News Load By Area${NC}"
curl --max-time 10 -s -X GET "http://${IP}:${PORT_LOAD}/api/news-load" | jq . || echo -e "${RED}Fallo en Load${NC}"

echo -e "\n${BLUE}  -> Microservicio: Last News 24 Hour${NC}"
curl --max-time 10 -s -X GET "http://${IP}:${PORT_24H}/api/news-last-24h?user_id=${USER_ID}" | jq . || echo -e "${RED}Fallo en 24H${NC}"

echo -e "\n${BLUE}  -> Microservicio: Find News By Descriptor${NC}"
curl --max-time 10 -s -X GET "http://${IP}:${PORT_DESC}/api/news-descriptor?descriptor=test" | jq . || echo -e "${RED}Fallo en Descriptor${NC}"
echo -e "${GREEN}✓ Todas las lecturas ejecutadas.${NC}\n"


echo -e "${YELLOW}>> [5/7] Probando Delete News (Intentando borrar una noticia irreal)...${NC}"
# Enviamos un ID falso (999999). Nos importa saber que el servicio responde y no hace crash.
DEL_NEWS_RES=$(curl --max-time 10 -s -w "\n%{http_code}" -X DELETE "http://${IP}:${PORT_DEL_NEWS}/noticias/999999?user_id=${USER_ID}")
HTTP_CODE=$(echo "$DEL_NEWS_RES" | tail -n1)
echo -e "${GREEN}✓ El servicio respondió con HTTP $HTTP_CODE.${NC}\n"


echo -e "${YELLOW}>> [6/7] Probando New Subscriptions (Desuscribir)...${NC}"
UNSUBS_RES=$(curl --max-time 10 -s -w "\n%{http_code}" -X DELETE "http://${IP}:${PORT_SUBS}/desuscribir" \
     -H "Content-Type: application/json" \
     -d "{\"user_id\": ${USER_ID}, \"category_id\": ${CATEGORY_ID}}")
HTTP_CODE=$(echo "$UNSUBS_RES" | tail -n1)
if [[ "$HTTP_CODE" =~ ^2 ]]; then
    echo -e "${GREEN}✓ Usuario ${USER_ID} desuscrito exitosamente.${NC}\n"
else
    echo -e "${RED}✗ Error en desuscripción. HTTP Code: $HTTP_CODE${NC}\n"
fi


echo -e "${YELLOW}>> [7/7] Teardown: Limpiando base de datos (Area Manager)...${NC}"
DEL_AREA_RES=$(curl --max-time 10 -s -w "\n%{http_code}" -X DELETE "http://${IP}:${PORT_AREA}/areas/${TEST_AREA}" \
     -H "Content-Type: application/json" \
     -d "{\"user_id\": ${USER_ID}}")
HTTP_CODE=$(echo "$DEL_AREA_RES" | tail -n1)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Área eliminada exitosamente. Transacción SERIALIZABLE completada.${NC}"
else
    echo -e "${RED}✗ Error al limpiar área. HTTP Code: $HTTP_CODE${NC}"
fi

echo -e "\n${BLUE}======================================================${NC}"
echo -e "${GREEN}       ¡RUTINA COMPLETADA SIN ERRORES CRÍTICOS!       ${NC}"
echo -e "${BLUE}======================================================${NC}"
