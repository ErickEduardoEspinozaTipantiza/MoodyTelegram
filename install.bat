@echo off
echo 🤖 Instalador Bot Moody - Orientacion Psicologica
echo ================================================

echo.
echo 📦 Instalando dependencias de Python...
pip install -r requirements.txt

echo.
echo 📁 Creando directorios necesarios...
if not exist "temp" mkdir temp
if not exist "data" mkdir data

echo.
echo 📋 Copiando archivo de configuracion...
if not exist ".env" (
    copy ".env.example" ".env"
    echo ⚠️  Por favor, edita el archivo .env con tus configuraciones
)

echo.
echo 🔍 Verificando modelos...
python init_models.py

echo.
echo ✅ Instalacion completada!
echo.
echo 🚀 Para iniciar el bot, ejecuta:
echo    python main.py
echo.
echo 📝 No olvides:
echo    1. Editar el archivo .env con tus configuraciones
echo    2. Asegurate de que Ollama este ejecutandose (opcional)
echo    3. Verificar que los modelos esten en la carpeta models/
echo.
pause
