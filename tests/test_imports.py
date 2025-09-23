#!/usr/bin/env python3
"""
Script di test per verificare che tutti gli import funzionino correttamente.
"""

import sys
from pathlib import Path

# Aggiunge src/ al path per l'importazione del package
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test che tutti gli import funzionino."""
    try:
        print("Testing core imports...")
        from meat_planner.core import config, data_manager, models, nutrition_calculator
        print("✅ Core imports successful")
        
        print("Testing UI imports...")
        from meat_planner.ui import ui_components
        from meat_planner.ui.pages import (
            diet_page,
            foods_page,
            recap_page,
            tracker_page,
        )
        print("✅ UI imports successful")
        
        print("Testing main app import...")
        from meat_planner import MealPlannerApp
        print("✅ Main app import successful")
        
        print("Testing data manager functionality...")
        dm = data_manager.DataManager()
        print(f"✅ DataManager instance created")
        
        print("Testing config paths...")
        print(f"Data directory: {config.DIRECTORIES['data']}")
        print(f"Foods file: {config.FILES['foods']}")
        print("✅ Config paths accessible")
        
        print("\n🎉 All tests passed! The new structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)