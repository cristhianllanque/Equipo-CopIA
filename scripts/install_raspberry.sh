#!/bin/bash
# Instalador amigable de CopIA para Raspberry Pi

echo "================================================="
echo "   Bienvenido al Instalador de CopIA Edge AI     "
echo "================================================="
echo ""
echo "Este script configurará tu Raspberry Pi para ejecutar el asistente de conducción."
echo ""

# Pedir la URL del servidor
read -p "1. Ingresa la URL de Ngrok que te dio el administrador (ej. https://xyz.ngrok.app): " SERVER_URL
if [ -z "$SERVER_URL" ]; then
    echo "No ingresaste una URL. Se usará localhost por defecto."
    SERVER_URL="http://localhost:8000"
fi

echo ""
echo "2. Instalando dependencias del sistema..."
echo "Te pediremos tu contraseña (sudo) si es necesario."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-tk python3-opencv libgl1-mesa-glx xterm

echo ""
echo "3. Creando entorno virtual de Python..."
cd "$(dirname "$0")/.." # Ir a la raíz del proyecto
PROJECT_ROOT=$(pwd)

python3 -m venv venv
source venv/bin/activate

echo "4. Instalando librerías de Python (esto puede tardar unos minutos)..."
pip install -r requirements.txt

echo ""
echo "5. Configurando la conexión (.env)..."
echo "SERVER_URL=$SERVER_URL" > .env
echo "Configuración guardada en .env"

echo ""
echo "6. Creando acceso directo en el Escritorio..."

DESKTOP_DIR="$HOME/Desktop"
if [ ! -d "$DESKTOP_DIR" ]; then
    DESKTOP_DIR="$HOME/Escritorio"
fi

SHORTCUT="$DESKTOP_DIR/CopIA_Edge.desktop"
cat <<EOF > "$SHORTCUT"
[Desktop Entry]
Version=1.0
Name=CopIA Edge Monitor
Comment=Asistente de Conducción AI
Exec=/bin/bash "$PROJECT_ROOT/scripts/start_copia.sh"
Icon=$PROJECT_ROOT/Frontend/public/logoCopAI.png
Terminal=true
Type=Application
Categories=Utility;
EOF

chmod +x "$SHORTCUT"

echo ""
echo "================================================="
echo " ¡Instalación Completada con Éxito!              "
echo "================================================="
echo "Ahora puedes encontrar el ícono 'CopIA Edge' en tu escritorio."
echo "Solo dale doble clic para iniciar la aplicación."
echo ""
read -p "Presiona Enter para salir..."
