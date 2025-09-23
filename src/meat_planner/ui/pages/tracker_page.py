"""
Tracker page for the Meat Planner application.
Handles daily meal planning and tracking.
"""

import streamlit as st

from ...core.config import APP_CONFIG, DAY_NAMES
from ...core.models import Day, Diet, MealPlan


def render_tracker_page(data_manager, nutrition_calculator):
    """Render the meal tracker page."""
    st.title("🍽️ Tracker Settimanale")
    
    # Initialize editing state
    if "editing_day" not in st.session_state:
        st.session_state.editing_day = None
    
    if st.session_state.editing_day:
        render_day_editing_interface(data_manager, nutrition_calculator)
    else:
        render_day_grid(data_manager, nutrition_calculator)


def render_day_editing_interface(data_manager, nutrition_calculator):
    """Render the interface for editing a specific day."""
    selected_day = st.session_state.editing_day
    
    # Back button
    if st.button("← Torna alla griglia", type="secondary"):
        st.session_state.editing_day = None
        st.rerun()
    
    # Extract day number for display
    day_number = selected_day.split('_')[1]
    st.title(f"📆 Modifica Giorno {day_number}")
    
    # Get day data
    meal_plan = MealPlan.from_dict(st.session_state.meal_plan)
    day = meal_plan.get_day(selected_day)
    
    if not day:
        st.error(f"Giorno {selected_day} non trovato!")
        return
    
    # Calculate target nutrition from current diet
    diet = Diet.from_dict(st.session_state.dieta_edit)
    target_nutrition = nutrition_calculator.calculate_diet_nutrition(diet)
    
    # Metrics container for real-time updates
    metrics_container = st.container()
    
    st.markdown("---")
    st.subheader("✏️ Modifica pasti")
    
    # Edit each meal
    foods_data = data_manager.get_foods_data_dict()
    food_names = sorted(foods_data.keys())
    
    changes_made = False
    
    for meal_name, meal in day.meals.items():
        with st.expander(f"🍽️ {meal_name}", expanded=True):
            # Edit food items in this meal
            for idx, food_item in enumerate(meal.food_items):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    try:
                        current_index = food_names.index(food_item.alimento)
                    except ValueError:
                        current_index = 0
                    
                    new_food = st.selectbox(
                        f"Alimento {idx + 1}",
                        food_names,
                        index=current_index,
                        key=f"day_food_{meal_name}_{idx}"
                    )
                    
                    if new_food != food_item.alimento:
                        food_item.alimento = new_food
                        changes_made = True
                
                with col2:
                    new_quantity = st.number_input(
                        "Quantità (g)",
                        min_value=0.0,
                        value=float(food_item.quantita),
                        step=1.0,
                        key=f"day_qty_{meal_name}_{idx}"
                    )
                    
                    if new_quantity != food_item.quantita:
                        food_item.quantita = new_quantity
                        changes_made = True
                
                with col3:
                    if st.button("🗑️", key=f"day_del_{meal_name}_{idx}"):
                        if 0 <= idx < len(meal.food_items):
                            removed_item = meal.food_items.pop(idx)
                            
                            # Update meal plan immediately with the modified day
                            meal_plan = MealPlan.from_dict(st.session_state.meal_plan)
                            meal_plan.add_day(day)  # Add the modified day
                            st.session_state.meal_plan = meal_plan.to_dict()
                            
                            # Calculate and save recap
                            recap_data = nutrition_calculator.calculate_weekly_recap(
                                meal_plan,
                                [f"Giorno_{i + 1}" for i in range(APP_CONFIG["total_days"])]
                            )
                            
                            # Save to file
                            data_manager.save_complete_data(meal_plan, recap_data)
                            st.success(f"Rimosso {removed_item.alimento} da {meal_name}")
                            st.rerun()
            
            # Add food item button
            if st.button(f"➕ Aggiungi a {meal_name}", key=f"day_add_{meal_name}"):
                from ...core.models import FoodItem
                new_food_item = FoodItem(alimento=food_names[0], quantita=100.0)
                meal.add_food_item(new_food_item)
                
                # Update meal plan immediately with the modified day
                meal_plan = MealPlan.from_dict(st.session_state.meal_plan)
                meal_plan.add_day(day)  # Add the modified day
                st.session_state.meal_plan = meal_plan.to_dict()
                
                # Calculate and save recap
                recap_data = nutrition_calculator.calculate_weekly_recap(
                    meal_plan,
                    [f"Giorno_{i + 1}" for i in range(APP_CONFIG["total_days"])]
                )
                
                # Save to file
                data_manager.save_complete_data(meal_plan, recap_data)
                st.success(f"Aggiunto {food_names[0]} a {meal_name}")
                st.rerun()
    
    # Update metrics
    current_nutrition = nutrition_calculator.calculate_day_nutrition(day)
    
    with metrics_container:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            diff = current_nutrition.kcal - target_nutrition.kcal
            st.metric("Kcal", f"{current_nutrition.kcal:.0f}", f"{diff:+.0f}")
        
        with col2:
            diff = current_nutrition.protein - target_nutrition.protein
            st.metric("Proteine (g)", f"{current_nutrition.protein:.1f}", f"{diff:+.1f}")
        
        with col3:
            diff = current_nutrition.carbs - target_nutrition.carbs
            st.metric("Carbo (g)", f"{current_nutrition.carbs:.1f}", f"{diff:+.1f}")
        
        with col4:
            diff = current_nutrition.fat - target_nutrition.fat
            st.metric("Grassi (g)", f"{current_nutrition.fat:.1f}", f"{diff:+.1f}")
        
        with col5:
            diff = current_nutrition.fiber - target_nutrition.fiber
            st.metric("Fibre (g)", f"{current_nutrition.fiber:.1f}", f"{diff:+.1f}")
    
    # Save changes if any were made
    if changes_made:
        # Update meal plan
        meal_plan.add_day(day)
        st.session_state.meal_plan = meal_plan.to_dict()
        
        # Calculate and save recap
        recap_data = nutrition_calculator.calculate_weekly_recap(
            meal_plan,
            [f"Giorno_{i + 1}" for i in range(APP_CONFIG["total_days"])]
        )
        
        # Save to file
        data_manager.save_complete_data(meal_plan, recap_data)
        st.success("✅ Modifiche salvate!")


def render_day_grid(data_manager, nutrition_calculator):
    """Render the 5x7 grid of days for selection."""
    st.subheader("🗓️ Seleziona un giorno da modificare")
    
    # Calculate target nutrition
    diet = Diet.from_dict(st.session_state.dieta_edit)
    target_nutrition = nutrition_calculator.calculate_diet_nutrition(diet)
    
    # Get meal plan
    meal_plan = MealPlan.from_dict(st.session_state.meal_plan)
    
    # Inject custom CSS
    from ..ui_components import inject_custom_css
    inject_custom_css()
    
    # Render 5 weeks
    for week in range(1, 6):
        st.markdown(f"### Settimana {week}")
        cols = st.columns(7)
        
        for day_idx in range(7):
            day_number = (week - 1) * 7 + day_idx + 1
            day_id = f"Giorno_{day_number}"
            
            with cols[day_idx]:
                # Calculate day nutrition
                day = meal_plan.get_day(day_id)
                if day:
                    day_nutrition = nutrition_calculator.calculate_day_nutrition(day)
                    
                    # Calculate variation
                    kcal_variation = nutrition_calculator.calculate_variation_percentage(
                        day_nutrition.kcal, target_nutrition.kcal
                    )
                    
                    # Get color indicator
                    color_indicator = nutrition_calculator.get_variation_color_class(kcal_variation)
                    
                    # Create button
                    button_label = f"{DAY_NAMES[day_idx]}\nG.{day_number}\n{day_nutrition.kcal:.0f} kcal"
                    
                    if st.button(
                        button_label,
                        key=f"grid_day_{day_id}",
                        help=f"Variazione: {kcal_variation:.1f}%"
                    ):
                        st.session_state.editing_day = day_id
                        st.rerun()
                else:
                    st.button(
                        f"{DAY_NAMES[day_idx]}\nG.{day_number}\nNon configurato",
                        key=f"grid_day_{day_id}",
                        disabled=True
                    )
        
        st.markdown("---")