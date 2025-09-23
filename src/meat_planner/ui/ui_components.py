"""
UI components for the Meat Planner application.
Contains the main UI logic and page routing.
"""

import streamlit as st

from ..core.config import APP_CONFIG, PAGES
from ..core.data_manager import data_manager
from ..core.models import Diet
from ..core.nutrition_calculator import NutritionCalculator
from .pages.diet_page import render_diet_page
from .pages.foods_page import render_foods_page
from .pages.recap_page import render_recap_page
from .pages.tracker_page import render_tracker_page


class MealPlannerApp:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        self.data_manager = data_manager
        self.setup_page_config()
        self.initialize_session_state()
        self.nutrition_calculator = NutritionCalculator(
            self.data_manager.get_foods_data_dict()
        )
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=APP_CONFIG["page_title"],
            layout=APP_CONFIG["layout"]
        )
    
    def initialize_session_state(self):
        """Initialize session state variables."""
        # Initialize diet editing state
        if "dieta_edit" not in st.session_state:
            diet, is_temp = self.data_manager.load_diet_temp()
            st.session_state.dieta_edit = diet.to_dict()
            st.session_state.dieta_da_temp = is_temp
        
        # Initialize meal plan state
        if "meal_plan" not in st.session_state:
            complete_data = self.data_manager.load_complete_data()
            if complete_data and "meal_plan" in complete_data:
                st.session_state.meal_plan = complete_data["meal_plan"]
            else:
                # Initialize with diet reference
                diet = Diet.from_dict(st.session_state.dieta_edit)
                day_names = [f"Giorno_{i + 1}" for i in range(APP_CONFIG["total_days"])]
                meal_plan = self.data_manager.initialize_meal_plan_from_diet(diet, day_names)
                st.session_state.meal_plan = meal_plan.to_dict()
        
        # Initialize editing state
        if "editing_day" not in st.session_state:
            st.session_state.editing_day = None
    
    def render_sidebar(self):
        """Render the navigation sidebar."""
        st.sidebar.title("Navigazione")
        return st.sidebar.radio("Vai a:", PAGES, index=0)
    
    def run(self):
        """Main application entry point."""
        # Render sidebar and get current page
        current_page = self.render_sidebar()
        
        # Route to appropriate page
        if current_page == "Tracker":
            render_tracker_page(
                self.data_manager,
                self.nutrition_calculator
            )
        elif current_page == "Dieta":
            render_diet_page(
                self.data_manager,
                self.nutrition_calculator
            )
        elif current_page == "Alimenti":
            render_foods_page(
                self.data_manager
            )
        elif current_page == "Recap":
            render_recap_page(
                self.data_manager,
                self.nutrition_calculator
            )


# CSS styles for the application
def inject_custom_css():
    """Inject custom CSS styles for the application."""
    st.markdown("""
    <style>
    /* Bottoni verdi per variazioni <= 10% */
    .stButton > button[aria-label*="✅"] {
        background-color: #28a745 !important;
        color: white !important;
        border: 1px solid #28a745 !important;
    }
    .stButton > button[aria-label*="✅"]:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    
    /* Bottoni gialli per variazioni 10-25% */
    .stButton > button[aria-label*="⚠️"] {
        background-color: #ffc107 !important;
        color: #212529 !important;
        border: 1px solid #ffc107 !important;
    }
    .stButton > button[aria-label*="⚠️"]:hover {
        background-color: #e0a800 !important;
        border-color: #d39e00 !important;
    }
    
    /* Bottoni rossi per variazioni > 25% */
    .stButton > button[aria-label*="❌"] {
        background-color: #dc3545 !important;
        color: white !important;
        border: 1px solid #dc3545 !important;
    }
    .stButton > button[aria-label*="❌"]:hover {
        background-color: #c82333 !important;
        border-color: #bd2130 !important;
    }
    </style>
    """, unsafe_allow_html=True)
