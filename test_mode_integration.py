#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba de integración para la funcionalidad de modos
Verifica que todos los componentes estén bien integrados
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Probar que todos los imports funcionen correctamente"""
    print("🔍 Probando imports...")
    
    try:
        from src.core.mode_manager import ModeManager, InspectionMode
        print("✅ ModeManager importado correctamente")
        
        from src.ui.mode_selector import ModeSelector
        print("✅ ModeSelector importado correctamente")
        
        from src.ui.controls.control_panel import ControlPanel
        print("✅ ControlPanel importado correctamente")
        
        from src.ui.core.main_window import MainWindow
        print("✅ MainWindow importado correctamente")
        
        from src.ui.core.window_manager import WindowManager
        print("✅ WindowManager importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_mode_manager():
    """Probar funcionalidad del ModeManager"""
    print("\n🔍 Probando ModeManager...")
    
    try:
        from src.core.mode_manager import ModeManager, InspectionMode
        
        # Crear instancia
        manager = ModeManager()
        print("✅ ModeManager creado")
        
        # Configurar modo PRO
        manager.set_mode(InspectionMode.PRO)
        print(f"✅ Modo PRO configurado: {manager.get_mode_name()}")
        
        # Verificar configuración PRO
        buttons = manager.get_control_buttons()
        overlays = manager.get_configurable_overlays()
        print(f"✅ Botones PRO: {buttons}")
        print(f"✅ Overlays PRO: {overlays}")
        
        # Configurar modo RÁPIDO
        manager.set_mode(InspectionMode.RAPIDO)
        print(f"✅ Modo RÁPIDO configurado: {manager.get_mode_name()}")
        
        # Verificar configuración RÁPIDO
        buttons = manager.get_control_buttons()
        overlays = manager.get_configurable_overlays()
        print(f"✅ Botones RÁPIDO: {buttons}")
        print(f"✅ Overlays RÁPIDO: {overlays}")
        
        # Configurar modo BÁSICO
        manager.set_mode(InspectionMode.BASICO)
        print(f"✅ Modo BÁSICO configurado: {manager.get_mode_name()}")
        
        # Verificar configuración BÁSICO
        buttons = manager.get_control_buttons()
        overlays = manager.get_configurable_overlays()
        print(f"✅ Botones BÁSICO: {buttons}")
        print(f"✅ Overlays BÁSICO: {overlays}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en ModeManager: {e}")
        return False

def test_mode_differences():
    """Probar que los modos tienen diferencias correctas"""
    print("\n🔍 Probando diferencias entre modos...")
    
    try:
        from src.core.mode_manager import ModeManager, InspectionMode
        
        manager = ModeManager()
        
        # Obtener configuraciones
        manager.set_mode(InspectionMode.PRO)
        pro_buttons = set(manager.get_control_buttons())
        pro_overlays = set(manager.get_configurable_overlays())
        
        manager.set_mode(InspectionMode.RAPIDO)
        rapido_buttons = set(manager.get_control_buttons())
        rapido_overlays = set(manager.get_configurable_overlays())
        
        manager.set_mode(InspectionMode.BASICO)
        basico_buttons = set(manager.get_control_buttons())
        basico_overlays = set(manager.get_configurable_overlays())
        
        # Verificar que PRO y RÁPIDO tienen los mismos botones ahora (sin +)
        if pro_buttons == rapido_buttons:
            print("✅ PRO y RÁPIDO tienen los mismos botones disponibles (sin botón +)")
        else:
            print("❌ PRO y RÁPIDO no tienen los mismos botones")
            print(f"PRO: {pro_buttons}")
            print(f"RÁPIDO: {rapido_buttons}")
            return False
        
        if len(pro_overlays) > len(rapido_overlays):
            print("✅ PRO tiene más overlays que RÁPIDO")
        else:
            print("❌ PRO no tiene más overlays que RÁPIDO")
            return False
        
        # Verificar que RÁPIDO tiene todos los botones (sin +)
        expected_rapido = {"record", "stop", "capture", "annotate", "reset", "clear", "settings"}
        if rapido_buttons == expected_rapido:
            print("✅ RÁPIDO tiene todos los botones disponibles (sin botón +)")
        else:
            print(f"❌ RÁPIDO no tiene los botones esperados. Tiene: {rapido_buttons}")
            return False
        
        print("✅ Diferencias entre modos correctas")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando diferencias: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBA DE INTEGRACIÓN DE MODOS")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("ModeManager", test_mode_manager),
        ("Diferencias entre modos", test_mode_differences)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 PRUEBA: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 RESULTADO: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La funcionalidad de modos está lista para usar")
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Ejecutar: python main.py")
        print("2. Hacer login con credenciales")
        print("3. Seleccionar modo de inspección")
        print("4. Verificar que el panel se adapte según el modo")
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores antes de usar la funcionalidad")

if __name__ == "__main__":
    main() 