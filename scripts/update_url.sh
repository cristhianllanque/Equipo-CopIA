#!/bin/bash
cd "$(dirname "$0")/.."
echo "================================================="
echo "   Actualizador de Enlace Ngrok para CopIA       "
echo "================================================="
read -p "Ingresa el NUEVO enlace de Ngrok de hoy: " NEW_URL
if [ -z "$NEW_URL" ]; then
    echo "No ingresaste nada. Saliendo..."
    exit 1
fi
echo "SERVER_URL=$NEW_URL" > .env
echo ""
echo "¡Éxito! El enlace ha sido actualizado a: $NEW_URL"
echo "Ya puedes abrir el programa desde tu escritorio."
