#!/bin/bash
# Script lanzador de CopIA Edge AI

# Ir al directorio raíz del proyecto
cd "$(dirname "$0")/.."

echo "Iniciando CopIA Edge Monitor..."

# Activar entorno virtual
source venv/bin/activate

# Ejecutar aplicación
python raspberry_gui.py

# Al cerrar, dar unos segundos por si hubo un error visible
sleep 2
