"""
Foods page for the Meat Planner application.
Handles food database management.
"""

import streamlit as st

from ...core.models import Food


def render_foods_page(data_manager):
    """Render the foods management page."""
    st.header("🍎 Alimenti")
    st.write("Gestione degli alimenti disponibili nel sistema")
    
    # Load foods
    foods = data_manager.load_foods()
    
    # Add new food form
    with st.expander("➕ Aggiungi nuovo alimento"):
        with st.form("nuovo_alimento"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome alimento")
                kcal = st.number_input("Kcal per 100g", min_value=0.0, step=1.0)
                carbs = st.number_input("Carboidrati per 100g", min_value=0.0, step=0.1)
            
            with col2:
                protein = st.number_input("Proteine per 100g", min_value=0.0, step=0.1)
                fat = st.number_input("Grassi per 100g", min_value=0.0, step=0.1)
                fiber = st.number_input("Fibre per 100g", min_value=0.0, step=0.1)
            
            tipologia = st.multiselect(
                "Tipologia",
                ["carbs", "protein", "fat", "fiber"],
                help="Seleziona le categorie principali per questo alimento"
            )
            
            if st.form_submit_button("Aggiungi alimento"):
                if nome and nome not in foods:
                    new_food = Food(
                        name=nome,
                        kcal=kcal,
                        carbs=carbs,
                        protein=protein,
                        fat=fat,
                        fiber=fiber,
                        tipologia=tipologia
                    )
                    try:
                        data_manager.add_food(new_food)
                        # Verifica che il salvataggio sia avvenuto ricaricando i dati
                        updated_foods = data_manager.load_foods()
                        if nome in updated_foods:
                            st.success(f"✅ Alimento '{nome}' aggiunto e salvato con successo!")
                            # Pulisce il session state se esiste per forzare il ricaricamento
                            if 'foods_cache' in st.session_state:
                                del st.session_state.foods_cache
                        else:
                            st.error(f"❌ Errore nel salvare l'alimento '{nome}'")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Errore durante il salvataggio: {str(e)}")
                elif nome in foods:
                    st.error("Alimento già esistente!")
                else:
                    st.error("Inserisci il nome dell'alimento!")
    
    # List existing foods
    st.subheader("📋 Elenco alimenti")
    sorted_foods = sorted(foods.items())
    
    for food_name, food in sorted_foods:
        with st.expander(f"🍽️ {food_name}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Kcal:** {food.kcal}")
                st.write(f"**Carboidrati:** {food.carbs}g")
                st.write(f"**Proteine:** {food.protein}g")
            
            with col2:
                st.write(f"**Grassi:** {food.fat}g")
                st.write(f"**Fibre:** {food.fiber}g")
                st.write(f"**Tipologia:** {', '.join(food.tipologia) if food.tipologia else 'N/A'}")
            
            with col3:
                # Usa il metodo del data_manager per verificare se l'alimento può essere rimosso
                if not data_manager.can_remove_food(food_name):
                    st.button("🔒 Protetto", key=f"protected_food_{food_name}", disabled=True, help="Questo alimento non può essere rimosso")
                else:
                    if st.button("🗑️ Elimina", key=f"delete_food_{food_name}"):
                        try:
                            # Usa il metodo del data_manager per rimuovere l'alimento
                            if data_manager.remove_food(food_name):
                                # Pulisce il session state se esiste per forzare il ricaricamento
                                if 'foods_cache' in st.session_state:
                                    del st.session_state.foods_cache
                                st.success(f"✅ Alimento '{food_name}' eliminato con successo!")
                                st.rerun()
                            else:
                                st.error(f"❌ Impossibile rimuovere l'alimento '{food_name}' o alimento non trovato!")
                        except Exception as e:
                            st.error(f"❌ Errore durante l'eliminazione: {str(e)}")
