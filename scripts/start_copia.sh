#!/bin/bash
# Script lanzador de CopIA Edge AI

# Ir al directorio raíz del proyecto
cd "$(dirname "$0")/.."

echo "Iniciando CopIA Edge Monitor..."
echo "Comprobando actualizaciones OTA..."

# El entorno virtual debe estar activo para Python y customtkinter
if [ -d "$HOME/miniforge3/envs/copia_env" ]; then
    source $HOME/miniforge3/bin/activate copia_env
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

python scripts/updater_gui.py

# Ejecutar aplicación
python raspberry_gui.py

# Al cerrar, dar unos segundos por si hubo un error visible
sleep 2
