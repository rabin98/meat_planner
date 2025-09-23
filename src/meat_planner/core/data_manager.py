"""
Data persistence manager for the Meat Planner application.
Handles all file I/O operations, backups, and data loading/saving.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .config import DIRECTORIES, FILES
from .models import Diet, Food, MealPlan


class DataManager:
    """Manages all data persistence operations."""

    def __init__(self):
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all required directories exist."""
        for directory in DIRECTORIES.values():
            os.makedirs(directory, exist_ok=True)

    # ==================== Basic File Operations ====================

    def load_json_file(self, filepath: str) -> Dict:
        """Load data from a JSON file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {filepath}: {e}")

    def save_json_file(self, filepath: str, data: Dict):
        """Save data to a JSON file."""
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ==================== Foods Management ====================

    def load_foods(self) -> Dict[str, Food]:
        """Load all foods from the foods.json file."""
        foods_data = self.load_json_file(FILES["foods"])
        foods = {}
        for name, data in foods_data.items():
            foods[name] = Food.from_dict(name, data)
        return foods

    def save_foods(self, foods: Dict[str, Food]):
        """Save foods to the foods.json file in alphabetical order."""
        # Sort foods alphabetically by name
        sorted_food_names = sorted(foods.keys())
        foods_data = {}
        for name in sorted_food_names:
            foods_data[name] = foods[name].to_dict()
        self.save_json_file(FILES["foods"], foods_data)

    def add_food(self, food: Food):
        """Add a new food to the foods database."""
        foods = self.load_foods()
        foods[food.name] = food
        self.save_foods(foods)

    def can_remove_food(self, food_name: str) -> bool:
        """Check if a food can be removed (protect special foods)."""
        protected_foods = ["-----"]
        return food_name not in protected_foods

    def remove_food(self, food_name: str) -> bool:
        """Remove a food from the database if allowed."""
        if not self.can_remove_food(food_name):
            return False
        
        foods = self.load_foods()
        if food_name in foods:
            del foods[food_name]
            self.save_foods(foods)
            return True
        return False

    # ==================== Basic Data Loading ====================

    def load_meals_list(self) -> List[str]:
        """Load the list of meal names."""
        return self.load_json_file(FILES["meals"])

    def load_days_list(self) -> List[str]:
        """Load the list of day names."""
        return self.load_json_file(FILES["days"])

    # ==================== Diet Management ====================

    def load_diet(self) -> Diet:
        """Load the current diet from diet.json."""
        diet_data = self.load_json_file(FILES["diet"])
        return Diet.from_dict(diet_data)

    def save_diet(self, diet: Diet):
        """Save diet to diet.json."""
        self.save_json_file(FILES["diet"], diet.to_dict())

    def load_diet_temp(self) -> Tuple[Diet, bool]:
        """Load diet from temp file if exists, otherwise from main file."""
        if os.path.exists(FILES["diet_temp"]):
            diet_data = self.load_json_file(FILES["diet_temp"])
            return Diet.from_dict(diet_data), True
        else:
            return self.load_diet(), False

    def save_diet_temp(self, diet: Diet):
        """Save diet to temporary file."""
        self.save_json_file(FILES["diet_temp"], diet.to_dict())

    def reset_diet_to_original(self) -> Diet:
        """Reset to original diet and remove temp file."""
        if os.path.exists(FILES["diet_temp"]):
            os.remove(FILES["diet_temp"])
        return self.load_diet()

    def backup_current_diet(self) -> str:
        """Create a backup of the current diet with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"dieta_{timestamp}.json"
        backup_path = os.path.join(DIRECTORIES["backup"], backup_filename)
        
        shutil.copy2(FILES["diet"], backup_path)
        return backup_filename

    def confirm_diet_changes(self) -> Tuple[bool, str]:
        """Confirm diet changes: backup current and replace with temp."""
        if not os.path.exists(FILES["diet_temp"]):
            return False, "Nessuna modifica da confermare"
        
        try:
            backup_filename = self.backup_current_diet()
            shutil.move(FILES["diet_temp"], FILES["diet"])
            return True, backup_filename
        except Exception as e:
            return False, str(e)

    def load_new_diet_from_file(self, uploaded_file) -> Tuple[bool, str, Optional[Diet]]:
        """Load a new diet from an uploaded file."""
        try:
            content = uploaded_file.read()
            diet_data = json.loads(content.decode('utf-8'))
            new_diet = Diet.from_dict(diet_data)
            
            # Create backup of current diet
            backup_filename = self.backup_current_diet()
            
            # Save new diet
            self.save_diet(new_diet)
            
            # Remove temp file if exists
            if os.path.exists(FILES["diet_temp"]):
                os.remove(FILES["diet_temp"])
            
            return True, backup_filename, new_diet
        except Exception as e:
            return False, str(e), None

    # ==================== Meal Plan Management ====================

    def load_complete_data(self) -> Optional[Dict]:
        """Load all data from the unified recap.json file."""
        if os.path.exists(FILES["recap"]):
            return self.load_json_file(FILES["recap"])
        return None

    def save_complete_data(self, meal_plan: MealPlan, recap_data: Dict):
        """Save complete data (meal plan + recap) to unified file."""
        complete_data = {
            "meal_plan": meal_plan.to_dict(),
            "recap": recap_data
        }
        self.save_json_file(FILES["recap"], complete_data)

    def load_meal_plan(self) -> Optional[MealPlan]:
        """Load meal plan from complete data file."""
        complete_data = self.load_complete_data()
        if complete_data and "meal_plan" in complete_data:
            return MealPlan.from_dict(complete_data["meal_plan"])
        return None

    def save_meal_plan(self, meal_plan: MealPlan, recap_data: Dict):
        """Save meal plan with recap data."""
        self.save_complete_data(meal_plan, recap_data)

    def load_day_data(self, day_name: str) -> Optional[Dict]:
        """Load data for a specific day."""
        complete_data = self.load_complete_data()
        if complete_data and "meal_plan" in complete_data:
            return complete_data["meal_plan"].get(day_name)
        return None

    def save_day_data(self, day_name: str, day_data: Dict, meal_plan: MealPlan, recap_data: Dict):
        """Save data for a specific day by updating the complete meal plan."""
        # Update meal plan with new day data
        from .models import Day
        day = Day.from_dict(day_name, day_data)
        meal_plan.add_day(day)
        
        # Save everything
        self.save_complete_data(meal_plan, recap_data)

    def load_recap_data(self) -> Optional[Dict]:
        """Load recap data from complete data file."""
        complete_data = self.load_complete_data()
        if complete_data and "recap" in complete_data:
            return complete_data["recap"]
        return None

    # ==================== Utility Methods ====================

    def get_foods_data_dict(self) -> Dict:
        """Get foods data as dictionary for legacy compatibility."""
        foods = self.load_foods()
        foods_dict = {}
        for name, food in foods.items():
            foods_dict[name] = food.to_dict()
        return foods_dict

    def initialize_meal_plan_from_diet(self, diet: Diet, day_names: List[str]) -> MealPlan:
        """Initialize a new meal plan based on a diet."""
        meal_plan = MealPlan()
        meal_plan.reset_all_to_diet(diet, day_names)
        return meal_plan


# Global instance for easy access
data_manager = DataManager()


# ==================== Legacy Functions ====================
# These functions provide backward compatibility with the original code

# def salva_tutti_dati(meal_plan_dict: Dict, recap_data: Dict):
#     """Legacy wrapper for saving all data."""
#     meal_plan = MealPlan.from_dict(meal_plan_dict)
#     data_manager.save_complete_data(meal_plan, recap_data)


# def carica_tutti_dati() -> Optional[Dict]:
#     """Legacy wrapper for loading all data."""
#     return data_manager.load_complete_data()


# def salva_giorno(day_name: str, giorno_data: Dict, meal_plan_dict: Dict, recap_data: Dict):
#     """Legacy wrapper for saving day data."""
#     meal_plan = MealPlan.from_dict(meal_plan_dict)
#     data_manager.save_day_data(day_name, giorno_data, meal_plan, recap_data)


# def carica_giorno(day_name: str) -> Optional[Dict]:
#     """Legacy wrapper for loading day data."""
#     return data_manager.load_day_data(day_name)


# def salva_recap(recap_data: Dict):
#     """Legacy wrapper for saving recap (uses complete data save)."""
#     # This function would need the meal plan data as well
#     # For now, just pass an empty meal plan
#     empty_meal_plan = MealPlan()
#     data_manager.save_complete_data(empty_meal_plan, recap_data)


# def carica_recap() -> Optional[Dict]:
#     """Legacy wrapper for loading recap data."""
#     return data_manager.load_recap_data()


# def backup_dieta_attuale() -> str:
#     """Legacy wrapper for backing up current diet."""
#     return data_manager.backup_current_diet()


# def salva_dieta_temp(dieta_data: Dict):
#     """Legacy wrapper for saving temporary diet."""
#     diet = Diet.from_dict(dieta_data)
#     data_manager.save_diet_temp(diet)


# def carica_dieta_temp() -> Tuple[Dict, bool]:
#     """Legacy wrapper for loading temporary diet."""
#     diet, is_temp = data_manager.load_diet_temp()
#     return diet.to_dict(), is_temp


# def reset_dieta_originale() -> Dict:
#     """Legacy wrapper for resetting to original diet."""
#     diet = data_manager.reset_diet_to_original()
#     return diet.to_dict()


# def conferma_modifiche_dieta() -> Tuple[bool, str]:
#     """Legacy wrapper for confirming diet changes."""
#     return data_manager.confirm_diet_changes()


# def carica_nuova_dieta(uploaded_file) -> Tuple[bool, str, Optional[Dict]]:
#     """Legacy wrapper for loading new diet from file."""
#     success, result, diet = data_manager.load_new_diet_from_file(uploaded_file)
#     diet_dict = diet.to_dict() if diet else None
#     return success, result, diet_dict
