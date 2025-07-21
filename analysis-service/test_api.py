#!/usr/bin/env python3
"""
Script de prueba para el Analysis Service
"""

import asyncio
import aiohttp
import json
import sys

# Configuración
AUTH_SERVICE_URL = "http://localhost:8080"
ANALYSIS_SERVICE_URL = "http://localhost:8002"

async def test_auth_service():
    """Prueba el servicio de autenticación"""
    print("🔐 Probando servicio de autenticación...")
    
    async with aiohttp.ClientSession() as session:
        # Datos de login
        login_data = {
            "username": "admin",
            "password": "password123"
        }
        
        try:
            # Realizar login
            async with session.post(f"{AUTH_SERVICE_URL}/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get('token')
                    user = data.get('user')
                    print(f"✅ Login exitoso para usuario: {user}")
                    print(f"🔑 Token obtenido: {token[:50]}...")
                    return token
                else:
                    print(f"❌ Error en login: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Error de conexión con auth-service: {e}")
            return None

async def test_analysis_service(token):
    """Prueba el servicio de análisis"""
    print("\n📊 Probando servicio de análisis...")
    
    if not token:
        print("❌ No se puede probar sin token válido")
        return
    
    async with aiohttp.ClientSession() as session:
        # Headers con token
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Archivos de prueba
        test_files = [
            "document.txt",
            "image.jpg",
            "data.json",
            "video.mp4"
        ]
        
        for filename in test_files:
            print(f"\n📁 Analizando archivo: {filename}")
            
            try:
                # Realizar análisis
                url = f"{ANALYSIS_SERVICE_URL}/api/v1/analyze?filename={filename}"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Análisis exitoso:")
                        print(f"   - Archivo original: {data['filename']}")
                        print(f"   - Archivo encriptado: {data['encrypted_filename'][:50]}...")
                        print(f"   - Tipo de archivo: {data['data']['file_type']}")
                        print(f"   - Tamaño simulado: {data['data']['file_size']} bytes")
                        print(f"   - Algoritmo: {data['data']['encryption_algorithm']}")
                    else:
                        error_data = await response.text()
                        print(f"❌ Error en análisis: {response.status}")
                        print(f"   Detalles: {error_data}")
            except Exception as e:
                print(f"❌ Error de conexión: {e}")

async def test_health_endpoints():
    """Prueba los endpoints de salud"""
    print("\n🏥 Probando endpoints de salud...")
    
    async with aiohttp.ClientSession() as session:
        # Probar auth-service health
        try:
            async with session.get(f"{AUTH_SERVICE_URL}/health") as response:
                if response.status == 200:
                    print("✅ Auth-service está saludable")
                else:
                    print(f"❌ Auth-service no está saludable: {response.status}")
        except Exception as e:
            print(f"❌ Error conectando a auth-service: {e}")
        
        # Probar analysis-service health
        try:
            async with session.get(f"{ANALYSIS_SERVICE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Analysis-service está saludable: {data}")
                else:
                    print(f"❌ Analysis-service no está saludable: {response.status}")
        except Exception as e:
            print(f"❌ Error conectando a analysis-service: {e}")

async def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del Analysis Service")
    print("=" * 50)
    
    # Probar endpoints de salud
    await test_health_endpoints()
    
    # Probar autenticación
    token = await test_auth_service()
    
    # Probar análisis
    await test_analysis_service(token)
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")
    
    # Mostrar URLs de documentación
    print("\n📚 Documentación disponible en:")
    print(f"   - Swagger UI: {ANALYSIS_SERVICE_URL}/docs")
    print(f"   - ReDoc: {ANALYSIS_SERVICE_URL}/redoc")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1) 