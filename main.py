import json
import os

"""
MEAT PLANNER APP
----------------
Applicazione Streamlit per la pianificazione dei pasti settimanali.
Permette di:
- Definire una dieta di riferimento (alimenti e grammature per pasto)
- Personalizzare i pasti di ogni giorno partendo dalla dieta
- Calcolare e confrontare i valori nutrizionali
- Vedere un recap settimanale dei valori nutrizionali
- Salvare e ripristinare i dati in modo persistente
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
    DAYS_ORIGINAL = json.load(f)

with open("dieta.json", "r", encoding="utf-8") as f:
    DIETA = json.load(f)

# Genera 35 giorni indipendenti (5 settimane x 7 giorni)
DAYS = [f"Giorno_{i + 1}" for i in range(35)]

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
# Funzioni di persistenza
# ==========================

def salva_tutti_dati():
    """Salva tutti i dati (meal_plan + recap) in un unico file recap.json"""
    os.makedirs("persistenza", exist_ok=True)
    
    # Prepara i dati da salvare
    data_completi = {
        "meal_plan": st.session_state.meal_plan,
        "recap": calcola_recap_settimanale()
    }
    
    with open("persistenza/recap.json", "w", encoding="utf-8") as f:
        json.dump(data_completi, f, ensure_ascii=False, indent=2)


def carica_tutti_dati():
    """Carica tutti i dati dal file recap.json"""
    if os.path.exists("persistenza/recap.json"):
        with open("persistenza/recap.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def salva_giorno(day_name, giorno_data):
    """Salva i dati di un giorno aggiornando il file recap.json"""
    # Aggiorna il meal_plan in session_state
    st.session_state.meal_plan[day_name] = giorno_data
    # Salva tutto
    salva_tutti_dati()


def carica_giorno(day_name):
    """Carica i dati di un giorno dal file recap.json"""
    data_completi = carica_tutti_dati()
    if data_completi and "meal_plan" in data_completi:
        return data_completi["meal_plan"].get(day_name)
    return None


def salva_recap(recap_data):
    """Salva i dati del recap (mantenuto per compatibilità, ma usa salva_tutti_dati)"""
    salva_tutti_dati()


def carica_recap():
    """Carica i dati del recap dal file recap.json"""
    data_completi = carica_tutti_dati()
    if data_completi and "recap" in data_completi:
        return data_completi["recap"]
    return None


def backup_dieta_attuale():
    """Crea un backup della dieta attuale nella cartella diete_old"""
    import shutil
    os.makedirs("diete_old", exist_ok=True)
    
    # Trova il prossimo numero progressivo
    progressivo = 1
    while os.path.exists(f"diete_old/dieta_{progressivo:03d}.json"):
        progressivo += 1
    
    # Copia il file attuale
    shutil.copy2("dieta.json", f"diete_old/dieta_{progressivo:03d}.json")
    return f"dieta_{progressivo:03d}.json"


def carica_nuova_dieta(uploaded_file):
    """Carica una nuova dieta da file uploadato"""
    try:
        # Leggi il contenuto del file
        content = uploaded_file.read()
        nuova_dieta = json.loads(content.decode('utf-8'))
        
        # Crea backup della dieta attuale
        backup_filename = backup_dieta_attuale()
        
        # Sovrascrivi il file dieta.json
        with open("dieta.json", "w", encoding="utf-8") as f:
            json.dump(nuova_dieta, f, ensure_ascii=False, indent=2)
        
        return True, backup_filename, nuova_dieta
    except Exception as e:
        return False, str(e), None


def reset_a_dieta():
    """Reset tutti i giorni alla dieta di riferimento"""
    for day in DAYS:
        giorno_reset = {}
        for meal in MEALS:
            giorno_reset[meal] = [dict(a) for a in DIETA.get(meal, [])]
        st.session_state.meal_plan[day] = giorno_reset
    
    # Salva tutto in un unico file
    salva_tutti_dati()


def calcola_recap_settimanale():
    """Calcola il recap di tutti i 35 giorni"""
    recap = {}
    totali_periodo = {"kcal": 0, "carbo": 0, "proteine": 0, "grassi": 0, "fibre": 0}
    
    for day in DAYS:
        giorno_data = st.session_state.meal_plan[day]
        totali_giorno = calcola_totali_giorno(giorno_data)
        recap[day] = totali_giorno
        
        for k in totali_periodo:
            totali_periodo[k] += totali_giorno[k]
    
    recap["totali_periodo"] = totali_periodo
    recap["media_giornaliera"] = {k: v / 35 for k, v in totali_periodo.items()}
    
    return recap


# ==========================
# Streamlit UI
# ==========================

st.set_page_config(page_title="Meal Tracker", layout="wide")
st.sidebar.title("Navigazione")
page = st.sidebar.radio("Vai a:", ["Tracker", "Dieta", "Recap"], index=0)

# ==========================
# Inizializzazione sessione
# ==========================
if "dieta_edit" not in st.session_state:
    st.session_state.dieta_edit = {k: [dict(a) for a in v] for k, v in DIETA.items()}

if "meal_plan" not in st.session_state:
    # Prova a caricare tutti i dati dal file unificato
    data_completi = carica_tutti_dati()
    if data_completi and "meal_plan" in data_completi:
        st.session_state.meal_plan = data_completi["meal_plan"]
    else:
        # Se non ci sono dati salvati, inizializza con la dieta di riferimento
        st.session_state.meal_plan = {}
        for day in DAYS:
            st.session_state.meal_plan[day] = {}
            for meal in MEALS:
                st.session_state.meal_plan[day][meal] = [dict(a) for a in DIETA.get(meal, [])]

# ==========================
# Pagina Dieta
# ==========================
if page == "Dieta":
    st.title("📋 Dieta di riferimento")
    if "dieta_edit" not in st.session_state:
        st.session_state.dieta_edit = {k: [dict(a) for a in v] for k, v in DIETA.items()}

    # Bottone per caricare una nuova dieta
    st.subheader("📂 Gestione Dieta")
    uploaded_file = st.file_uploader(
        "Carica una nuova dieta (file JSON)",
        type=['json'],
        help="Seleziona un file JSON con la struttura della dieta per sostituire quella attuale"
    )
    
    if uploaded_file is not None:
        if st.button("🔄 Carica Dieta", type="primary"):
            success, risultato, nuova_dieta = carica_nuova_dieta(uploaded_file)
            if success:
                st.success(f"✅ Dieta caricata con successo! Backup salvato come: {risultato}")
                # Aggiorna solo il session state, la variabile globale verrà ricaricata al prossimo refresh
                st.session_state.dieta_edit = {k: [dict(a) for a in v] for k, v in nuova_dieta.items()}
                st.info("🔄 Ricarica la pagina per applicare completamente i cambiamenti alla dieta di riferimento.")
                st.rerun()
            else:
                st.error(f"❌ Errore nel caricamento della dieta: {risultato}")
    
    st.markdown("---")

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
elif page == "Tracker":
    st.title("� Tracker Settimanale")
    
    # Inizializza il session state per la modalità di editing
    if "editing_day" not in st.session_state:
        st.session_state.editing_day = None
    
    # Se stiamo modificando un giorno specifico
    if st.session_state.editing_day:
        selected_day = st.session_state.editing_day
        
        # Bottone per tornare alla vista griglia
        if st.button("← Torna alla griglia", type="secondary"):
            st.session_state.editing_day = None
            st.rerun()
        
        # Estrai il numero del giorno per la visualizzazione
        numero_giorno = selected_day.split('_')[1]
        st.title(f"📆 Modifica Giorno {numero_giorno}")
        
        giorno = st.session_state.meal_plan[selected_day]
        pasti = list(giorno.keys())

        # Calcola i target giornalieri dalla dieta modificata in session_state
        dieta_ref = calcola_totali_dieta(st.session_state.dieta_edit)

        # Container per i valori nutrizionali che si aggiorna dinamicamente
        metrics_container = st.container()
        
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
                            salva_giorno(selected_day, giorno)
                            st.rerun()
            
            # Modifica alimenti esistenti
            alimenti_modificati = False
            for idx, alimento in enumerate(alimenti):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    nuovo_alimento = st.selectbox(
                        f"Alimento {idx + 1}",
                        list(FOODS.keys()),
                        key=f"{selected_day}_{nome_pasto}_food_{idx}",
                        index=list(FOODS.keys()).index(alimento["alimento"]) if alimento["alimento"] in FOODS else 0
                    )
                    if nuovo_alimento != alimento["alimento"]:
                        alimento["alimento"] = nuovo_alimento
                        alimenti_modificati = True
                with col2:
                    nuova_quantita = st.number_input(
                        "Quantità (g)",
                        min_value=0,
                        value=int(alimento["quantita"]),
                        key=f"{selected_day}_{nome_pasto}_qty_{idx}"
                    )
                    if nuova_quantita != alimento["quantita"]:
                        alimento["quantita"] = nuova_quantita
                        alimenti_modificati = True
                with col3:
                    if st.button("Rimuovi", key=f"remove_{selected_day}_{nome_pasto}_{idx}"):
                        alimenti.pop(idx)
                        salva_giorno(selected_day, giorno)
                        st.rerun()
            
            # Salva e ricarica se ci sono state modifiche
            if alimenti_modificati:
                salva_giorno(selected_day, giorno)
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

        # Calcola i totali aggiornati dopo tutte le modifiche
        totals = {k: 0 for k in ["kcal", "carbo", "proteine", "grassi", "fibre"]}
        for meal_items in giorno.values():
            valori = calcola_nutrienti(meal_items)
            for k in totals:
                totals[k] += valori[k]

        # Aggiorna il container dei metrics con i valori aggiornati
        with metrics_container:
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

        # Salva automaticamente i cambiamenti ogni volta che si modifica qualcosa
        salva_giorno(selected_day, giorno)
    
    else:
        # Vista griglia 5x7 (5 settimane x 7 giorni)
        st.subheader("🗓️ Seleziona un giorno da modificare")
        
        # Calcola i target giornalieri dalla dieta
        dieta_ref = calcola_totali_dieta(st.session_state.dieta_edit)
        
        # Genera 5 settimane di giorni (35 giorni totali)
        giorni_settimana = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
        
        for settimana in range(1, 6):
            st.markdown(f"**Settimana {settimana}**")
            cols = st.columns(7)
            
            for giorno_idx in range(7):
                with cols[giorno_idx]:
                    # Calcola il numero del giorno (da 1 a 35)
                    numero_giorno = (settimana - 1) * 7 + giorno_idx + 1
                    giorno_id = f"Giorno_{numero_giorno}"
                    giorno_nome_breve = giorni_settimana[giorno_idx]
                    
                    # Calcola i totali del giorno
                    giorno_data = st.session_state.meal_plan[giorno_id]
                    totali_giorno = calcola_totali_giorno(giorno_data)
                    
                    # Calcola la percentuale rispetto al target
                    perc_kcal = (totali_giorno['kcal'] / dieta_ref['kcal']) * 100 if dieta_ref['kcal'] > 0 else 0
                    
                    # Colore in base alla percentuale (verde se vicino al target)
                    if 90 <= perc_kcal <= 110:
                        tipo_bottone = "primary"
                        emoji = "✅"
                    elif 80 <= perc_kcal <= 120:
                        tipo_bottone = "secondary"
                        emoji = "⚠️"
                    else:
                        tipo_bottone = "secondary"
                        emoji = "❌"
                    
                    # Bottone per ogni giorno
                    if st.button(
                        f"{emoji} {giorno_nome_breve}\n{numero_giorno}\n{totali_giorno['kcal']:.0f} kcal\n({perc_kcal:.0f}%)",
                        key=f"btn_{numero_giorno}",
                        type=tipo_bottone,
                        use_container_width=True
                    ):
                        st.session_state.editing_day = giorno_id
                        st.rerun()
            
            st.markdown("")  # Spazio tra le settimane

# ==========================
# Pagina Recap
# ==========================
elif page == "Recap":
    st.title("📊 Recap Periodo (35 giorni)")
    
    # Calcola il recap attuale
    recap_attuale = calcola_recap_settimanale()
    dieta_ref = calcola_totali_dieta(st.session_state.dieta_edit)
    
    # Bottone per azioni
    if st.button("🔄 RESET (Ripristina da Dieta)", type="primary"):
        reset_a_dieta()
        st.success("Tutti i giorni sono stati ripristinati alla dieta di riferimento!")
        st.rerun()
    
    st.markdown("---")
    
    # Tabella riassuntiva dei giorni
    st.subheader("📅 Valori per Giorno")
    
    data_giorni = []
    for day in DAYS:
        totali_giorno = recap_attuale[day]
        # Estrai il numero del giorno dal nome (es. "Giorno_1" -> "1")
        numero_giorno = day.split('_')[1]
        data_giorni.append({
            "Giorno": numero_giorno,
            "Kcal": f"{totali_giorno['kcal']:.0f}",
            "Carboidrati (g)": f"{totali_giorno['carbo']:.1f}",
            "Proteine (g)": f"{totali_giorno['proteine']:.1f}",
            "Grassi (g)": f"{totali_giorno['grassi']:.1f}",
            "Fibre (g)": f"{totali_giorno['fibre']:.1f}"
        })
    
    st.table(data_giorni)
    
    st.markdown("---")
    
    # Totali e medie del periodo (35 giorni)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Totali del Periodo (35 giorni)")
        totali_periodo = recap_attuale["totali_periodo"]
        target_periodo = {k: v * 35 for k, v in dieta_ref.items()}
        
        for nutriente in ["kcal", "carbo", "proteine", "grassi", "fibre"]:
            delta = totali_periodo[nutriente] - target_periodo[nutriente]
            unita = "kcal" if nutriente == "kcal" else "g"
            st.metric(
                f"{nutriente.title()}",
                f"{totali_periodo[nutriente]:.1f} {unita}",
                f"{delta:+.1f} {unita}"
            )
    
    with col2:
        st.subheader("📊 Medie Giornaliere")
        medie = recap_attuale["media_giornaliera"]
        
        for nutriente in ["kcal", "carbo", "proteine", "grassi", "fibre"]:
            delta = medie[nutriente] - dieta_ref[nutriente]
            unita = "kcal" if nutriente == "kcal" else "g"
            st.metric(
                f"{nutriente.title()} (media)",
                f"{medie[nutriente]:.1f} {unita}",
                f"{delta:+.1f} {unita}"
            )
    
    st.markdown("---")
    
    # Dettagli per ogni giorno
    st.subheader("🔍 Dettagli per Giorno")
    
    for day in DAYS:
        # Estrai il numero del giorno per la visualizzazione
        numero_giorno = day.split('_')[1]
        with st.expander(f"Giorno {numero_giorno} - Dettagli"):
            giorno_data = st.session_state.meal_plan[day]
            totali_giorno = recap_attuale[day]
            
            # Mostra differenza rispetto ai target
            st.info(
                f"**Target vs Reale:** "
                f"Kcal: {totali_giorno['kcal']:.0f}/{dieta_ref['kcal']:.0f} "
                f"({totali_giorno['kcal'] - dieta_ref['kcal']:+.0f}) | "
                f"Proteine: {totali_giorno['proteine']:.1f}/{dieta_ref['proteine']:.1f} g "
                f"({totali_giorno['proteine'] - dieta_ref['proteine']:+.1f}) | "
                f"Carbo: {totali_giorno['carbo']:.1f}/{dieta_ref['carbo']:.1f} g "
                f"({totali_giorno['carbo'] - dieta_ref['carbo']:+.1f})"
            )
            
            # Mostra i pasti del giorno
            for nome_pasto, alimenti in giorno_data.items():
                st.write(f"**{nome_pasto}:**")
                if alimenti:
                    for alimento in alimenti:
                        st.write(f"  • {alimento['alimento']}: {alimento['quantita']}g")
                else:
                    st.write("  • Nessun alimento")
                
                valori_pasto = calcola_nutrienti(alimenti)
                st.caption(
                    f"  {valori_pasto['kcal']:.0f} kcal | "
                    f"P: {valori_pasto['proteine']:.1f}g | "
                    f"C: {valori_pasto['carbo']:.1f}g | "
                    f"G: {valori_pasto['grassi']:.1f}g | "
                    f"F: {valori_pasto['fibre']:.1f}g"
                )
