"""
Diet page for the Meat Planner application.
Handles the diet reference configuration and management.
"""

import os

import streamlit as st

from ...core.models import Diet, FoodItem


def render_diet_page(data_manager, nutrition_calculator):
    """Render the diet configuration page."""
    st.title("📋 Dieta di riferimento")
    
    # Show if diet is loaded from temp file
    if st.session_state.get('dieta_da_temp', False):
        st.info("ℹ️ Stai visualizzando una dieta modificata (salvata automaticamente)")
    
    # Diet management buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Reset Dieta", type="secondary"):
            reset_diet_to_original(data_manager)
    
    with col2:
        # Show confirm button only if there are changes to confirm
        if st.session_state.get('dieta_da_temp', False):
            if st.button("💾 Conferma Modifiche", type="primary"):
                confirm_diet_changes(data_manager)
    
    # Diet upload section
    st.subheader("📂 Gestione Dieta")
    uploaded_file = st.file_uploader(
        "Carica una nuova dieta (file JSON)",
        type=['json'],
        help="Seleziona un file JSON con la struttura della dieta per sostituire quella attuale"
    )
    
    if uploaded_file is not None:
        if st.button("🔄 Carica Dieta", type="primary"):
            load_new_diet(data_manager, uploaded_file)
    
    st.markdown("---")
    
    # Diet editing interface
    render_diet_editing_interface(data_manager, nutrition_calculator)


def reset_diet_to_original(data_manager):
    """Reset diet to original version."""
    # Remove temp file if exists
    if os.path.exists("dieta_temp.json"):
        os.remove("dieta_temp.json")
    
    # Load original diet
    original_diet = data_manager.load_diet()
    
    # Update session state
    st.session_state.dieta_edit = original_diet.to_dict()
    st.session_state.dieta_da_temp = False
    st.success("✅ Dieta ripristinata all'originale!")
    st.rerun()


def confirm_diet_changes(data_manager):
    """Confirm and save diet changes."""
    success, backup_filename = data_manager.confirm_diet_changes()
    if success:
        st.session_state.dieta_da_temp = False
        st.success(f"✅ Modifiche confermate! Backup salvato come: {backup_filename}")
        st.rerun()
    else:
        st.error(f"❌ Errore nel confermare le modifiche: {backup_filename}")


def load_new_diet(data_manager, uploaded_file):
    """Load a new diet from uploaded file."""
    success, result, new_diet_dict = data_manager.load_new_diet_from_file(uploaded_file)
    if success:
        st.session_state.dieta_edit = new_diet_dict
        st.session_state.dieta_da_temp = False
        st.success(f"✅ Nuova dieta caricata! Backup salvato come: {result}")
        st.rerun()
    else:
        st.error(f"❌ Errore nel caricare la dieta: {result}")


def render_diet_editing_interface(data_manager, nutrition_calculator):
    """Render the diet editing interface."""
    # Load current diet
    diet = Diet.from_dict(st.session_state.dieta_edit)
    
    # Track changes
    changes_made = False
    
    # Load foods data for dropdown
    foods_data = data_manager.get_foods_data_dict()
    food_names = sorted(foods_data.keys())
    
    # Edit each meal
    for meal_name, meal in diet.meals.items():
        st.subheader(meal_name)
        
        # Edit existing food items
        for idx, food_item in enumerate(meal.food_items):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Food selection
                try:
                    current_index = food_names.index(food_item.alimento)
                except ValueError:
                    current_index = 0
                
                new_food = st.selectbox(
                    f"Alimento {idx + 1}",
                    food_names,
                    index=current_index,
                    key=f"food_{meal_name}_{idx}"
                )
                
                if new_food != food_item.alimento:
                    food_item.alimento = new_food
                    changes_made = True
            
            with col2:
                # Quantity input
                new_quantity = st.number_input(
                    "Quantità (g)",
                    min_value=0.0,
                    value=float(food_item.quantita),
                    step=1.0,
                    key=f"qty_{meal_name}_{idx}"
                )
                
                if new_quantity != food_item.quantita:
                    food_item.quantita = new_quantity
                    changes_made = True
            
            with col3:
                # Delete button
                if st.button("🗑️", key=f"del_{meal_name}_{idx}"):
                    if 0 <= idx < len(meal.food_items):
                        removed_item = meal.food_items.pop(idx)
                        
                        # Update session state immediately
                        st.session_state.dieta_edit = diet.to_dict()
                        
                        # Save to temp file immediately
                        data_manager.save_diet_temp(diet)
                        st.session_state.dieta_da_temp = True
                        st.success(f"Rimosso {removed_item.alimento} da {meal_name}")
                        st.rerun()
        
        # Add new food item button
        if st.button(f"➕ Aggiungi alimento a {meal_name}", key=f"add_{meal_name}"):
            new_food_item = FoodItem(alimento=food_names[0], quantita=100.0)
            meal.add_food_item(new_food_item)
            
            # Update session state immediately
            st.session_state.dieta_edit = diet.to_dict()
            
            # Save to temp file immediately
            data_manager.save_diet_temp(diet)
            st.session_state.dieta_da_temp = True
            st.success(f"Aggiunto {food_names[0]} a {meal_name}")
            st.rerun()
        
        # Show meal nutrition
        meal_nutrition = nutrition_calculator.calculate_meal_nutrition(meal)
        st.markdown(nutrition_calculator.format_nutrition_values(meal_nutrition))
    
    # Save changes if any were made
    if changes_made:
        # Update session state
        st.session_state.dieta_edit = diet.to_dict()
        
        # Save to temp file
        data_manager.save_diet_temp(diet)
        st.session_state.dieta_da_temp = True
        st.success("✅ Modifiche salvate temporaneamente!")
        st.rerun()
    
    # Show total nutrition
    st.markdown("---")
    total_nutrition = nutrition_calculator.calculate_diet_nutrition(diet)
    st.success(f"**Totali giornalieri target:** {nutrition_calculator.format_nutrition_values(total_nutrition)}")