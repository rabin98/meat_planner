# Configuration constants for the Meat Planner application

# File paths
FILES = {
    "foods": "data/foods.json",
    "meals": "data/meals.json",
    "days": "data/days.json",
    "diet": "data/dieta.json",
    "diet_temp": "data/dieta_temp.json",
    "recap": "data/recap.json"
}

# Directories
DIRECTORIES = {
    "data": "data",
    "backup": "diete_old"
}

# Application settings
APP_CONFIG = {
    "total_days": 35,  # 5 weeks x 7 days
    "weeks": 5,
    "days_per_week": 7,
    "page_title": "Meal Tracker",
    "layout": "wide"
}

# Nutrition keys
NUTRITION_KEYS = ["kcal", "carbs", "protein", "fat", "fiber"]

# Color thresholds for day variations (percentage)
COLOR_THRESHOLDS = {
    "green": 10,    # <= 10% variation
    "yellow": 25,   # 10-25% variation
    "red": 25       # > 25% variation
}

# Day names in Italian
DAY_NAMES = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

# Default nutrition values
DEFAULT_NUTRITION = {
    "kcal": 0,
    "carbs": 0,
    "protein": 0,
    "fat": 0,
    "fiber": 0
}

# Page names
PAGES = ["Tracker", "Dieta", "Alimenti", "Recap"]
