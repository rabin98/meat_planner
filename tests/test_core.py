#!/usr/bin/env python3
"""
Script di test per verificare che gli import core funzionino correttamente.
"""

import sys
from pathlib import Path

# Aggiunge src/ al path per l'importazione del package
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_core_imports():
    """Test che gli import core funzionino."""
    try:
        print("Testing core imports...")
        from meat_planner.core import (
            DataManager,
            config,
            data_manager,
            models,
            nutrition_calculator,
        )
        print("✅ All core imports successful")
        
        print("Testing config values...")
        print(f"Data directory: {config.DIRECTORIES['data']}")
        print(f"Foods file: {config.FILES['foods']}")
        print("✅ Config values accessible")
        
        print("Testing data manager instantiation...")
        dm = DataManager()
        print("✅ New DataManager instance created successfully")
        
        print("Testing global data manager instance...")
        print(f"✅ Global DataManager accessible: {type(data_manager)}")
        
        print("Testing models...")
        food = models.Food(name="Test Food", kcal=78.0, carbs=5.0, protein=10.0, fat=2.0, fiber=1.0, tipologia=["test"])
        print(f"✅ Food model created: {food.name}")
        
        print("\n🎉 Core imports and basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_core_imports()
    sys.exit(0 if success else 1)