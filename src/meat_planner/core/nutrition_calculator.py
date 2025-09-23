"""
Nutrition calculation utilities for the Meat Planner application.
Handles all nutrition-related calculations and comparisons.
"""

from typing import Dict, List

import streamlit as st

from .models import Day, Diet, FoodItem, Meal, MealPlan, NutritionValues


class NutritionCalculator:
    """Handles all nutrition calculations."""

    def __init__(self, foods_data: Dict):
        self.foods_data = foods_data

    def calculate_food_item_nutrition(self, food_item: FoodItem) -> NutritionValues:
        """Calculate nutrition values for a single food item with quantity."""
        food_data = self.foods_data.get(food_item.alimento)
        if not food_data:
            st.warning(f"Alimento non trovato: {food_item.alimento}")
            return NutritionValues()

        quantity_factor = food_item.quantita / 100
        return NutritionValues(
            kcal=food_data.get("kcal", 0) * quantity_factor,
            carbs=food_data.get("carbs", 0) * quantity_factor,
            protein=food_data.get("protein", 0) * quantity_factor,
            fat=food_data.get("fat", 0) * quantity_factor,
            fiber=food_data.get("fiber", 0) * quantity_factor
        )

    def calculate_food_items_nutrition(self, food_items: List[FoodItem]) -> NutritionValues:
        """Calculate total nutrition values for a list of food items."""
        total = NutritionValues()
        for food_item in food_items:
            item_nutrition = self.calculate_food_item_nutrition(food_item)
            total = total + item_nutrition
        return total

    def calculate_meal_nutrition(self, meal: Meal) -> NutritionValues:
        """Calculate nutrition values for a meal."""
        return self.calculate_food_items_nutrition(meal.food_items)

    def calculate_diet_nutrition(self, diet: Diet) -> NutritionValues:
        """Calculate total nutrition values for a complete diet."""
        total = NutritionValues()
        for meal in diet.meals.values():
            meal_nutrition = self.calculate_meal_nutrition(meal)
            total = total + meal_nutrition
        return total

    def calculate_day_nutrition(self, day: Day) -> NutritionValues:
        """Calculate total nutrition values for a day."""
        total = NutritionValues()
        for meal in day.meals.values():
            meal_nutrition = self.calculate_meal_nutrition(meal)
            total = total + meal_nutrition
        return total

    def calculate_meal_plan_nutrition(self, meal_plan: MealPlan) -> Dict[str, NutritionValues]:
        """Calculate nutrition values for each day in a meal plan."""
        daily_nutrition = {}
        for day_name, day in meal_plan.days.items():
            daily_nutrition[day_name] = self.calculate_day_nutrition(day)
        return daily_nutrition

    def calculate_weekly_recap(self, meal_plan: MealPlan, day_names: List[str]) -> Dict:
        """Calculate weekly recap with totals for individual days and weeks."""
        recap = {}
        
        # Calculate totals for each individual day
        daily_nutrition = self.calculate_meal_plan_nutrition(meal_plan)
        for day_name in day_names:
            if day_name in daily_nutrition:
                recap[day_name] = daily_nutrition[day_name].to_dict()
            else:
                recap[day_name] = NutritionValues().to_dict()
        
        # Calculate totals for each week (5 weeks x 7 days)
        recap["settimane"] = {}
        weeks = 5
        days_per_week = 7
        
        for week in range(1, weeks + 1):
            week_total = NutritionValues()
            week_days = []
            
            for day_idx in range(days_per_week):
                day_number = (week - 1) * days_per_week + day_idx + 1
                day_id = f"Giorno_{day_number}"
                week_days.append(day_id)
                
                if day_id in recap:
                    day_nutrition = NutritionValues.from_dict(recap[day_id])
                    week_total = week_total + day_nutrition
            
            recap["settimane"][f"settimana_{week}"] = {
                "totali": week_total.to_dict(),
                "giorni": week_days
            }
        
        return recap

    def calculate_variation_percentage(self, actual: float, target: float) -> float:
        """Calculate percentage variation between actual and target values."""
        if target == 0:
            return 0 if actual == 0 else 100
        return abs((actual - target) / target) * 100

    def get_variation_color_class(self, variation_percentage: float) -> str:
        """Get CSS color class based on variation percentage."""
        if variation_percentage <= 10:
            return "✅"  # Green
        elif variation_percentage <= 25:
            return "⚠️"  # Yellow
        else:
            return "❌"  # Red

    def format_nutrition_comparison(self, actual: NutritionValues, target: NutritionValues) -> str:
        """Format nutrition comparison string for display."""
        return (
            f"**Kcal:** {actual.kcal:.0f}/{target.kcal:.0f} "
            f"({actual.kcal - target.kcal:+.0f}) | "
            f"**Proteine:** {actual.protein:.1f}/{target.protein:.1f} g "
            f"({actual.protein - target.protein:+.1f}) | "
            f"**Carbo:** {actual.carbs:.1f}/{target.carbs:.1f} g "
            f"({actual.carbs - target.carbs:+.1f}) | "
            f"**Grassi:** {actual.fat:.1f}/{target.fat:.1f} g "
            f"({actual.fat - target.fat:+.1f}) | "
            f"**Fibre:** {actual.fiber:.1f}/{target.fiber:.1f} g "
            f"({actual.fiber - target.fiber:+.1f})"
        )

    def format_nutrition_values(self, nutrition: NutritionValues) -> str:
        """Format nutrition values for display."""
        return (
            f"**Kcal:** {nutrition.kcal:.0f} | "
            f"**Proteine:** {nutrition.protein:.1f} g | "
            f"**Carbo:** {nutrition.carbs:.1f} g | "
            f"**Grassi:** {nutrition.fat:.1f} g | "
            f"**Fibre:** {nutrition.fiber:.1f} g"
        )

    def format_nutrition_caption(self, nutrition: NutritionValues) -> str:
        """Format nutrition values for caption display."""
        return (
            f"{nutrition.kcal:.0f} kcal | "
            f"P: {nutrition.protein:.1f}g | "
            f"C: {nutrition.carbs:.1f}g | "
            f"G: {nutrition.fat:.1f}g | "
            f"F: {nutrition.fiber:.1f}g"
        )


# # Legacy function wrappers for backward compatibility
# def calcola_nutrienti(lista_alimenti: List[Dict], foods_data: Dict) -> Dict:
#     """Legacy wrapper for backward compatibility."""
#     calculator = NutritionCalculator(foods_data)
#     food_items = [FoodItem.from_dict(item) for item in lista_alimenti]
#     nutrition = calculator.calculate_food_items_nutrition(food_items)
#     return nutrition.to_dict()


# def calcola_totali_dieta(dieta_dict: Dict, foods_data: Dict) -> Dict:
#     """Legacy wrapper for backward compatibility."""
#     calculator = NutritionCalculator(foods_data)
#     diet = Diet.from_dict(dieta_dict)
#     nutrition = calculator.calculate_diet_nutrition(diet)
#     return nutrition.to_dict()


# def calcola_totali_giorno(giorno_dict: Dict, foods_data: Dict) -> Dict:
#     """Legacy wrapper for backward compatibility."""
#     calculator = NutritionCalculator(foods_data)
#     day = Day.from_dict("temp", giorno_dict)
#     nutrition = calculator.calculate_day_nutrition(day)
#     return nutrition.to_dict()
