#!/usr/bin/env python3
"""
Entry point per l'applicazione Meat Planner.

Utilizzo:
    streamlit run main.py
"""

import sys
from pathlib import Path

# Aggiunge src/ al path per l'importazione del package
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from meat_planner import MealPlannerApp


def main():
    """Entry point principale dell'applicazione."""
    app = MealPlannerApp()
    app.run()


if __name__ == "__main__":
    main()
