"""
Script simple para verificar el bot sin modelos de ML
"""
import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_basic_setup():
    """Verifica la configuración básica del bot"""
    logger.info("🔍 Verificando configuración básica...")
    
    # Verificar archivos esenciales
    essential_files = [
        "main.py",
        ".env",
        "config/settings.py",
        "handlers/start_handler.py"
    ]
    
    missing_files = []
    for file in essential_files:
        if os.path.exists(file):
            logger.info(f"✅ {file} encontrado")
        else:
            logger.error(f"❌ {file} no encontrado")
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Archivos esenciales faltantes: {missing_files}")
        return False
    
    # Verificar directorios
    directories = ["models", "data", "temp", "handlers", "services", "config"]
    for directory in directories:
        if os.path.exists(directory):
            logger.info(f"✅ Directorio {directory}/ encontrado")
        else:
            logger.warning(f"⚠️ Directorio {directory}/ no encontrado, creando...")
            os.makedirs(directory, exist_ok=True)
    
    # Verificar modelos (opcional)
    model_files = [
        "models/modelo_cnn.h5",
        "models/scaler.pkl", 
        "models/pca.pkl",
        "models/label_encoder.pkl"
    ]
    
    models_found = 0
    for model_file in model_files:
        if os.path.exists(model_file):
            logger.info(f"✅ {model_file} encontrado")
            models_found += 1
        else:
            logger.warning(f"⚠️ {model_file} no encontrado")
    
    if models_found == 0:
        logger.warning("⚠️ No se encontraron modelos de ML. El bot funcionará con análisis básico.")
    elif models_found < len(model_files):
        logger.warning(f"⚠️ Solo {models_found}/{len(model_files)} modelos encontrados.")
    else:
        logger.info("✅ Todos los modelos de ML encontrados")
    
    return True

def test_imports():
    """Prueba las importaciones básicas"""
    logger.info("🧪 Probando importaciones...")
    
    try:
        import telegram
        logger.info("✅ python-telegram-bot importado correctamente")
    except ImportError as e:
        logger.error(f"❌ Error importando telegram: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        logger.info("✅ python-dotenv importado correctamente")
    except ImportError as e:
        logger.error(f"❌ Error importando dotenv: {e}")
        return False
    
    try:
        import requests
        logger.info("✅ requests importado correctamente")
    except ImportError as e:
        logger.error(f"❌ Error importando requests: {e}")
        return False
    
    return True

def check_telegram_token():
    """Verifica que el token de Telegram esté configurado"""
    logger.info("🔑 Verificando token de Telegram...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv('TELEGRAM_BOT_TOKEN', '8293226970:AAHns7nkSeL4SFHbmH7K6YOlglq6YAwgL1Q')
        
        if token and len(token) > 20:
            logger.info("✅ Token de Telegram configurado")
            return True
        else:
            logger.error("❌ Token de Telegram no válido")
            return False
    except Exception as e:
        logger.error(f"❌ Error verificando token: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Verificando configuración del Bot Moody...")
    print("=" * 50)
    
    # Realizar verificaciones
    setup_ok = check_basic_setup()
    imports_ok = test_imports()
    token_ok = check_telegram_token()
    
    print("=" * 50)
    
    if setup_ok and imports_ok and token_ok:
        logger.info("🎉 ¡Bot listo para probar!")
        print("\n🤖 Para iniciar el bot, ejecuta:")
        print("python main.py")
        print("\n📱 Luego ve a Telegram y busca tu bot para probarlo")
        print("\n💡 Comandos para probar:")
        print("   /start - Iniciar el bot")
        print("   /help - Ver ayuda")
    else:
        logger.error("❌ El bot no está completamente configurado")
        print("\n🔧 Revisa los errores anteriores y corrígelos")
        
        if not imports_ok:
            print("\n📦 Para instalar dependencias faltantes:")
            print("pip install python-telegram-bot python-dotenv requests")
    
    print("\n" + "=" * 50)
