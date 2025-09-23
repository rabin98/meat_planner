"""
Core functionality del Meat Planner.
Contiene modelli di dati, logica di business e gestione persistenza.
"""

from .config import *
from .data_manager import DataManager, data_manager
from .models import *
from .nutrition_calculator import NutritionCalculator

__all__ = [
    'DataManager', 'data_manager', 'NutritionCalculator',
    'Food', 'FoodItem', 'Meal', 'Diet', 'Day', 'MealPlan', 'NutritionValues',
    'APP_CONFIG', 'DIRECTORIES', 'FILES', 'PAGES', 'DAY_NAMES'
]