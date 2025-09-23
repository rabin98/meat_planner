"""
Data models for the Meat Planner application.
Contains classes for representing foods, meals, diets, and days.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Food:
    """Represents a food item with nutritional information."""
    name: str
    kcal: float
    carbs: float
    protein: float
    fat: float
    fiber: float
    tipologia: List[str]

    @classmethod
    def from_dict(cls, name: str, data: Dict) -> 'Food':
        """Create a Food instance from dictionary data."""
        return cls(
            name=name,
            kcal=data.get('kcal', 0),
            carbs=data.get('carbs', 0),
            protein=data.get('protein', 0),
            fat=data.get('fat', 0),
            fiber=data.get('fiber', 0),
            tipologia=data.get('tipologia', [])
        )

    def to_dict(self) -> Dict:
        """Convert Food instance to dictionary."""
        return {
            'kcal': self.kcal,
            'carbs': self.carbs,
            'protein': self.protein,
            'fat': self.fat,
            'fiber': self.fiber,
            'tipologia': self.tipologia
        }


@dataclass
class FoodItem:
    """Represents a food item with quantity."""
    alimento: str
    quantita: float

    @classmethod
    def from_dict(cls, data: Dict) -> 'FoodItem':
        """Create a FoodItem instance from dictionary data."""
        return cls(
            alimento=data['alimento'],
            quantita=data['quantita']
        )

    def to_dict(self) -> Dict:
        """Convert FoodItem instance to dictionary."""
        return {
            'alimento': self.alimento,
            'quantita': self.quantita
        }


@dataclass
class NutritionValues:
    """Represents nutritional values."""
    kcal: float = 0
    carbs: float = 0
    protein: float = 0
    fat: float = 0
    fiber: float = 0

    @classmethod
    def from_dict(cls, data: Dict) -> 'NutritionValues':
        """Create NutritionValues from dictionary."""
        return cls(
            kcal=data.get('kcal', 0),
            carbs=data.get('carbs', 0),
            protein=data.get('protein', 0),
            fat=data.get('fat', 0),
            fiber=data.get('fiber', 0)
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'kcal': self.kcal,
            'carbs': self.carbs,
            'protein': self.protein,
            'fat': self.fat,
            'fiber': self.fiber
        }

    def add(self, other: 'NutritionValues') -> 'NutritionValues':
        """Add another NutritionValues to this one."""
        return NutritionValues(
            kcal=self.kcal + other.kcal,
            carbs=self.carbs + other.carbs,
            protein=self.protein + other.protein,
            fat=self.fat + other.fat,
            fiber=self.fiber + other.fiber
        )

    def __add__(self, other: 'NutritionValues') -> 'NutritionValues':
        """Allow using + operator."""
        return self.add(other)


class Meal:
    """Represents a meal with food items."""

    def __init__(self, name: str, food_items: List[FoodItem] = None):
        self.name = name
        self.food_items = food_items or []

    @classmethod
    def from_dict(cls, name: str, data: List[Dict]) -> 'Meal':
        """Create a Meal instance from dictionary data."""
        food_items = [FoodItem.from_dict(item) for item in data]
        return cls(name=name, food_items=food_items)

    def to_dict(self) -> List[Dict]:
        """Convert Meal instance to list of dictionaries."""
        return [item.to_dict() for item in self.food_items]

    def add_food_item(self, food_item: FoodItem):
        """Add a food item to the meal."""
        self.food_items.append(food_item)

    def remove_food_item(self, index: int):
        """Remove a food item by index."""
        if 0 <= index < len(self.food_items):
            del self.food_items[index]

    def update_food_item(self, index: int, food_item: FoodItem):
        """Update a food item at specific index."""
        if 0 <= index < len(self.food_items):
            self.food_items[index] = food_item


class Diet:
    """Represents a complete diet with multiple meals."""

    def __init__(self, meals: Dict[str, Meal] = None):
        self.meals = meals or {}

    @classmethod
    def from_dict(cls, data: Dict) -> 'Diet':
        """Create a Diet instance from dictionary data."""
        meals = {}
        for meal_name, meal_data in data.items():
            meals[meal_name] = Meal.from_dict(meal_name, meal_data)
        return cls(meals=meals)

    def to_dict(self) -> Dict:
        """Convert Diet instance to dictionary."""
        return {meal_name: meal.to_dict() for meal_name, meal in self.meals.items()}

    def get_meal(self, meal_name: str) -> Optional[Meal]:
        """Get a specific meal by name."""
        return self.meals.get(meal_name)

    def add_meal(self, meal: Meal):
        """Add a meal to the diet."""
        self.meals[meal.name] = meal

    def copy(self) -> 'Diet':
        """Create a deep copy of the diet."""
        new_meals = {}
        for meal_name, meal in self.meals.items():
            new_food_items = [
                FoodItem(item.alimento, item.quantita)
                for item in meal.food_items
            ]
            new_meals[meal_name] = Meal(meal_name, new_food_items)
        return Diet(new_meals)


class Day:
    """Represents a single day with meals."""

    def __init__(self, name: str, meals: Dict[str, Meal] = None):
        self.name = name
        self.meals = meals or {}

    @classmethod
    def from_dict(cls, name: str, data: Dict) -> 'Day':
        """Create a Day instance from dictionary data."""
        meals = {}
        for meal_name, meal_data in data.items():
            meals[meal_name] = Meal.from_dict(meal_name, meal_data)
        return cls(name=name, meals=meals)

    def to_dict(self) -> Dict:
        """Convert Day instance to dictionary."""
        return {meal_name: meal.to_dict() for meal_name, meal in self.meals.items()}

    def get_meal(self, meal_name: str) -> Optional[Meal]:
        """Get a specific meal by name."""
        return self.meals.get(meal_name)

    def add_meal(self, meal: Meal):
        """Add a meal to the day."""
        self.meals[meal.name] = meal

    def reset_to_diet(self, diet: Diet):
        """Reset this day to match the reference diet."""
        self.meals = diet.copy().meals


class MealPlan:
    """Represents a complete meal plan with multiple days."""

    def __init__(self, days: Dict[str, Day] = None):
        self.days = days or {}

    @classmethod
    def from_dict(cls, data: Dict) -> 'MealPlan':
        """Create a MealPlan instance from dictionary data."""
        days = {}
        for day_name, day_data in data.items():
            days[day_name] = Day.from_dict(day_name, day_data)
        return cls(days=days)

    def to_dict(self) -> Dict:
        """Convert MealPlan instance to dictionary."""
        return {day_name: day.to_dict() for day_name, day in self.days.items()}

    def get_day(self, day_name: str) -> Optional[Day]:
        """Get a specific day by name."""
        return self.days.get(day_name)

    def add_day(self, day: Day):
        """Add a day to the meal plan."""
        self.days[day.name] = day

    def reset_all_to_diet(self, diet: Diet, day_names: List[str]):
        """Reset all days to match the reference diet."""
        for day_name in day_names:
            if day_name not in self.days:
                self.days[day_name] = Day(day_name)
            self.days[day_name].reset_to_diet(diet)
