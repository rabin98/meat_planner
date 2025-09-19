import json

"""
MEAT PLANNER APP
----------------
Applicazione Streamlit per la pianificazione dei pasti settimanali.
Permette di:
- Definire una dieta di riferimento (alimenti e grammature per pasto)
- Personalizzare i pasti di ogni giorno partendo dalla dieta
- Calcolare e confrontare i valori nutrizionali
"""

import streamlit as st

# ==========================
# Caricamento dati JSON
# ==========================
with open("foods.json", "r", encoding="utf-8") as f:
    FOODS = json.load(f)

with open("meals.json", "r", encoding="utf-8") as f:
    MEALS = json.load(f)

with open("days.json", "r", encoding="utf-8") as f:
    DAYS = json.load(f)

with open("dieta.json", "r", encoding="utf-8") as f:
    DIETA = json.load(f)

# ==========================
# Funzioni di utilità
# ==========================


def calcola_nutrienti(lista_alimenti):
    """
    Calcola i valori nutrizionali totali per una lista di alimenti.
    Restituisce un dizionario con kcal, carboidrati, proteine, grassi, fibre.
    """
    total = {"kcal": 0, "carbo": 0, "proteine": 0, "grassi": 0, "fibre": 0}
    mapping = {
        "carbo": "carbs",
        "proteine": "protein",
        "grassi": "fat",
        "fibre": "fiber"
    }
    for item in lista_alimenti:
        _alimento = FOODS.get(item["alimento"])
        if not _alimento:
            # non interrompiamo: segnaliamo e proseguiamo
            st.warning(f"Alimento non trovato: {item['alimento']}")
            continue
        q = item["quantita"] / 100
        total["kcal"] += _alimento.get("kcal", 0) * q
        for _k, kfood in mapping.items():
            total[_k] += _alimento.get(kfood, 0) * q
    return total


def calcola_totali_dieta(dieta):
    _totals = {"kcal": 0, "carbo": 0, "proteine": 0, "grassi": 0, "fibre": 0}
    for _alimenti in dieta.values():
        _valori = calcola_nutrienti(_alimenti)
        for _k in _totals:
            _totals[_k] += _valori[_k]
    return _totals


def calcola_totali_giorno(giorno):
    _totals = {"kcal": 0, "carbo": 0, "proteine": 0, "grassi": 0, "fibre": 0}
    for _alimenti in giorno.values():
        _valori = calcola_nutrienti(_alimenti)
        for _k in _totals:
            _totals[_k] += _valori[_k]
    return _totals


# ==========================
# Streamlit UI
# ==========================

st.set_page_config(page_title="Meal Tracker", layout="wide")
st.sidebar.title("Navigazione")
page = st.sidebar.radio("Vai a:", ["Giorni", "Dieta"], index=0)

# ==========================
# Inizializzazione sessione
# ==========================
if "dieta_edit" not in st.session_state:
    st.session_state.dieta_edit = {k: [dict(a) for a in v] for k, v in DIETA.items()}

if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = {}
    for day in DAYS:
        st.session_state.meal_plan[day] = {}
        for meal in MEALS:
            # copiamo la lista di alimenti per pasto dalla dieta di riferimento (se presente)
            st.session_state.meal_plan[day][meal] = [dict(a) for a in DIETA.get(meal, [])]

# ==========================
# Pagina Dieta
# ==========================
if page == "Dieta":
    st.title("📋 Dieta di riferimento")
    if "dieta_edit" not in st.session_state:
        st.session_state.dieta_edit = {k: [dict(a) for a in v] for k, v in DIETA.items()}

    dieta_totals = {"kcal": 0, "carbo": 0, "proteine": 0, "grassi": 0, "fibre": 0}

    for nome_pasto, alimenti in st.session_state.dieta_edit.items():
        st.subheader(nome_pasto)
        for idx, alimento in enumerate(alimenti):
            col1, col2 = st.columns([3, 1])
            with col1:
                alimento["alimento"] = st.selectbox(
                    f"Alimento {idx + 1} - {nome_pasto}",
                    list(FOODS.keys()),
                    key=f"dieta_{nome_pasto}_food_{idx}",
                    index=list(FOODS.keys()).index(alimento["alimento"]) if alimento["alimento"] in FOODS else 0
                )
            with col2:
                alimento["quantita"] = st.number_input(
                    "Quantità (g)",
                    min_value=0,
                    value=int(alimento["quantita"]),
                    key=f"dieta_{nome_pasto}_qty_{idx}"
                )
        valori = calcola_nutrienti(alimenti)
        st.markdown(
            f"**Kcal:** {valori['kcal']:.0f} | "
            f"**Proteine:** {valori['proteine']:.1f} g | "
            f"**Carbo:** {valori['carbo']:.1f} g | "
            f"**Grassi:** {valori['grassi']:.1f} g | "
            f"**Fibre:** {valori['fibre']:.1f} g"
        )
        for k in dieta_totals:
            dieta_totals[k] += valori[k]

    st.markdown("---")
    st.success(
        f"**Totali giornalieri target:** {dieta_totals['kcal']:.0f} kcal | "
        f"{dieta_totals['proteine']:.1f} g proteine | "
        f"{dieta_totals['carbo']:.1f} g carbo | "
        f"{dieta_totals['grassi']:.1f} g grassi | "
        f"{dieta_totals['fibre']:.1f} g fibre"
    )

# ==========================
# Pagina Giorni
# ==========================
elif page == "Giorni":
    st.title("📆 Giorni della settimana")
    selected_day = st.selectbox("Seleziona un giorno:", DAYS)

    giorno = st.session_state.meal_plan[selected_day]
    pasti = list(giorno.keys())

    # Calcola i target giornalieri dalla dieta modificata in session_state
    dieta_ref = calcola_totali_dieta(st.session_state.dieta_edit)

    # Calcola i totali dei nutrienti del giorno
    totals = {k: 0 for k in ["kcal", "carbo", "proteine", "grassi", "fibre"]}
    for meal_items in giorno.values():
        valori = calcola_nutrienti(meal_items)
        for k in totals:
            totals[k] += valori[k]

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Kcal", f"{totals['kcal']:.0f}/{dieta_ref['kcal']:.0f}", delta=f"{totals['kcal'] - dieta_ref['kcal']:.0f}")
    with col2:
        st.metric("Carboidrati", f"{totals['carbo']:.1f}/{dieta_ref['carbo']:.1f} g", delta=f"{totals['carbo'] - dieta_ref['carbo']:.1f}")
    with col3:
        st.metric("Proteine", f"{totals['proteine']:.1f}/{dieta_ref['proteine']:.1f} g", delta=f"{totals['proteine'] - dieta_ref['proteine']:.1f}")
    with col4:
        st.metric("Grassi", f"{totals['grassi']:.1f}/{dieta_ref['grassi']:.1f} g", delta=f"{totals['grassi'] - dieta_ref['grassi']:.1f}")
    with col5:
        st.metric("Fibre", f"{totals['fibre']:.1f}/{dieta_ref['fibre']:.1f} g", delta=f"{totals['fibre'] - dieta_ref['fibre']:.1f}")

    st.caption(
        f"Differenza rispetto ai target: "
        f"Kcal: {totals['kcal'] - dieta_ref['kcal']:.0f}, "
        f"Carbo: {totals['carbo'] - dieta_ref['carbo']:.1f} g, "
        f"Proteine: {totals['proteine'] - dieta_ref['proteine']:.1f} g, "
        f"Grassi: {totals['grassi'] - dieta_ref['grassi']:.1f} g, "
        f"Fibre: {totals['fibre'] - dieta_ref['fibre']:.1f} g."
    )

    st.markdown("---")
    st.subheader("✏️ Modifica pasti")
    
    # Interfaccia per modificare manualmente i pasti
    for nome_pasto, alimenti in giorno.items():
        st.subheader(nome_pasto)
        
        # Aggiungi un nuovo alimento al pasto
        with st.expander(f"Aggiungi alimento a {nome_pasto}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                nuovo_alimento = st.selectbox(
                    f"Nuovo alimento per {nome_pasto}",
                    [""] + list(FOODS.keys()),
                    key=f"nuovo_{selected_day}_{nome_pasto}"
                )
            with col2:
                nuova_quantita = st.number_input(
                    "Quantità (g)",
                    min_value=0,
                    value=100,
                    key=f"qty_nuovo_{selected_day}_{nome_pasto}"
                )
            with col3:
                if st.button("Aggiungi", key=f"add_{selected_day}_{nome_pasto}"):
                    if nuovo_alimento:
                        alimenti.append({"alimento": nuovo_alimento, "quantita": nuova_quantita})
                        st.rerun()
        
        # Modifica alimenti esistenti
        for idx, alimento in enumerate(alimenti):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                alimento["alimento"] = st.selectbox(
                    f"Alimento {idx + 1}",
                    list(FOODS.keys()),
                    key=f"{selected_day}_{nome_pasto}_food_{idx}",
                    index=list(FOODS.keys()).index(alimento["alimento"]) if alimento["alimento"] in FOODS else 0
                )
            with col2:
                alimento["quantita"] = st.number_input(
                    "Quantità (g)",
                    min_value=0,
                    value=int(alimento["quantita"]),
                    key=f"{selected_day}_{nome_pasto}_qty_{idx}"
                )
            with col3:
                if st.button("Rimuovi", key=f"remove_{selected_day}_{nome_pasto}_{idx}"):
                    alimenti.pop(idx)
                    st.rerun()
        
        # Mostra i valori nutrizionali del pasto
        valori_pasto = calcola_nutrienti(alimenti)
        st.markdown(
            f"**{nome_pasto}:** {valori_pasto['kcal']:.0f} kcal | "
            f"Proteine: {valori_pasto['proteine']:.1f} g | "
            f"Carbo: {valori_pasto['carbo']:.1f} g | "
            f"Grassi: {valori_pasto['grassi']:.1f} g | "
            f"Fibre: {valori_pasto['fibre']:.1f} g"
        )
