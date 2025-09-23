"""
Recap page for the Meat Planner application.
Handles weekly and period analysis.
"""

import streamlit as st

from ...core.config import APP_CONFIG
from ...core.models import Diet, MealPlan


def render_recap_page(data_manager, nutrition_calculator):
    """Render the recap analysis page."""
    st.title("📊 Recap Periodo (35 giorni)")
    
    # Load current data
    meal_plan = MealPlan.from_dict(st.session_state.meal_plan)
    diet = Diet.from_dict(st.session_state.dieta_edit)
    target_nutrition = nutrition_calculator.calculate_diet_nutrition(diet)
    
    # Reset button
    if st.button("🔄 RESET (Ripristina da Dieta)", type="primary"):
        reset_all_to_diet(data_manager, nutrition_calculator)
    
    st.markdown("---")
    
    # Calculate recap
    day_names = [f"Giorno_{i + 1}" for i in range(APP_CONFIG["total_days"])]
    recap_data = nutrition_calculator.calculate_weekly_recap(meal_plan, day_names)
    
    # Weekly analysis
    st.subheader("📊 Analisi per Settimane")
    
    for week in range(1, 6):
        week_key = f"settimana_{week}"
        week_data = recap_data["settimane"][week_key]
        week_totals = week_data["totali"]
        week_days = week_data["giorni"]
        
        with st.expander(f"📅 Settimana {week}", expanded=False):
            # Weekly totals
            st.subheader("Totali Settimana")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Calculate weekly targets (7 days * daily target)
            weekly_target_kcal = target_nutrition.kcal * 7
            weekly_target_protein = target_nutrition.protein * 7
            weekly_target_carbs = target_nutrition.carbs * 7
            weekly_target_fat = target_nutrition.fat * 7
            weekly_target_fiber = target_nutrition.fiber * 7
            
            with col1:
                diff = week_totals["kcal"] - weekly_target_kcal
                st.metric("Kcal", f"{week_totals['kcal']:.0f}", f"{diff:+.0f}")
            
            with col2:
                diff = week_totals["protein"] - weekly_target_protein
                st.metric("Proteine (g)", f"{week_totals['protein']:.1f}", f"{diff:+.1f}")
            
            with col3:
                diff = week_totals["carbs"] - weekly_target_carbs
                st.metric("Carbo (g)", f"{week_totals['carbs']:.1f}", f"{diff:+.1f}")
            
            with col4:
                diff = week_totals["fat"] - weekly_target_fat
                st.metric("Grassi (g)", f"{week_totals['fat']:.1f}", f"{diff:+.1f}")
            
            with col5:
                diff = week_totals["fiber"] - weekly_target_fiber
                st.metric("Fibre (g)", f"{week_totals['fiber']:.1f}", f"{diff:+.1f}")
    
    st.markdown("---")
    
    # Daily details
    st.subheader("🔍 Dettagli Completi per Giorno")
    
    for week in range(1, 6):
        st.markdown(f"### Settimana {week}")
        week_key = f"settimana_{week}"
        week_days = recap_data["settimane"][week_key]["giorni"]
        
        for day_id in week_days:
            day_number = day_id.split('_')[1]
            
            with st.expander(f"Giorno {day_number} - Dettagli"):
                day = meal_plan.get_day(day_id)
                
                if day:
                    day_nutrition = nutrition_calculator.calculate_day_nutrition(day)
                    
                    # Show comparison with target
                    st.info(nutrition_calculator.format_nutrition_comparison(day_nutrition, target_nutrition))
                    
                    # Show meals for the day
                    for meal_name, meal in day.meals.items():
                        st.write(f"**{meal_name}:**")
                        if meal.food_items:
                            for food_item in meal.food_items:
                                st.write(f"  • {food_item.alimento}: {food_item.quantita}g")
                        else:
                            st.write("  • Nessun alimento")
                        
                        meal_nutrition = nutrition_calculator.calculate_meal_nutrition(meal)
                        st.caption(f"  {nutrition_calculator.format_nutrition_caption(meal_nutrition)}")
                else:
                    st.write("Giorno non configurato")


def reset_all_to_diet(data_manager, nutrition_calculator):
    """Reset all days to the reference diet."""
    # Load current diet
    diet = Diet.from_dict(st.session_state.dieta_edit)
    
    # Generate day names
    day_names = [f"Giorno_{i + 1}" for i in range(APP_CONFIG["total_days"])]
    
    # Reset meal plan
    meal_plan = data_manager.initialize_meal_plan_from_diet(diet, day_names)
    st.session_state.meal_plan = meal_plan.to_dict()
    
    # Calculate and save recap
    recap_data = nutrition_calculator.calculate_weekly_recap(meal_plan, day_names)
    data_manager.save_complete_data(meal_plan, recap_data)
    
    st.success("Tutti i giorni sono stati ripristinati alla dieta di riferimento!")
    st.rerun()