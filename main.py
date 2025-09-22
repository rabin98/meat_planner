import json
import os
from datetime import datetime

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
    total = {"kcal": 0, "carbs": 0, "protein": 0, "fat": 0, "fiber": 0}
    for item in lista_alimenti:
        _alimento = FOODS.get(item["alimento"])
        if not _alimento:
            # non interrompiamo: segnaliamo e proseguiamo
            st.warning(f"Alimento non trovato: {item['alimento']}")
            continue
        q = item["quantita"] / 100
        total["kcal"] += _alimento.get("kcal", 0) * q
        total["carbs"] += _alimento.get("carbs", 0) * q
        total["protein"] += _alimento.get("protein", 0) * q
        total["fat"] += _alimento.get("fat", 0) * q
        total["fiber"] += _alimento.get("fiber", 0) * q
    return total


def calcola_totali_dieta(dieta):
    _totals = {"kcal": 0, "carbs": 0, "protein": 0, "fat": 0, "fiber": 0}
    for _alimenti in dieta.values():
        _valori = calcola_nutrienti(_alimenti)
        for _k in _totals:
            _totals[_k] += _valori[_k]
    return _totals


def calcola_totali_giorno(giorno):
    _totals = {"kcal": 0, "carbs": 0, "protein": 0, "fat": 0, "fiber": 0}
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
    """Crea un backup della dieta attuale nella cartella diete_old con timestamp"""
    import shutil
    os.makedirs("diete_old", exist_ok=True)
    
    # Genera timestamp per rendere il nome file univoco
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"dieta_{timestamp}.json"
    backup_path = f"diete_old/{backup_filename}"
    
    # Copia il file attuale
    shutil.copy2("dieta.json", backup_path)
    return backup_filename


def salva_dieta_temp(dieta_data):
    """Salva la dieta modificata in dieta_temp.json"""
    with open("dieta_temp.json", "w", encoding="utf-8") as f:
        json.dump(dieta_data, f, ensure_ascii=False, indent=2)


def carica_dieta_temp():
    """Carica la dieta da dieta_temp.json se esiste, altrimenti da dieta.json"""
    if os.path.exists("dieta_temp.json"):
        with open("dieta_temp.json", "r", encoding="utf-8") as f:
            return json.load(f), True  # True indica che è stata caricata da temp
    else:
        with open("dieta.json", "r", encoding="utf-8") as f:
            return json.load(f), False  # False indica che è stata caricata da originale


def reset_dieta_originale():
    """Reset alla dieta originale e cancella il file temporaneo"""
    # Cancella il file temporaneo se esiste
    if os.path.exists("dieta_temp.json"):
        os.remove("dieta_temp.json")
    
    # Ricarica la dieta originale
    with open("dieta.json", "r", encoding="utf-8") as f:
        return json.load(f)


def conferma_modifiche_dieta():
    """Conferma le modifiche: sposta dieta.json in backup e rinomina dieta_temp.json"""
    import shutil
    
    if not os.path.exists("dieta_temp.json"):
        return False, "Nessuna modifica da confermare"
    
    try:
        # Crea backup della dieta attuale
        backup_filename = backup_dieta_attuale()
        
        # Rinomina dieta_temp.json in dieta.json
        shutil.move("dieta_temp.json", "dieta.json")
        
        return True, backup_filename
    except Exception as e:
        return False, str(e)


def carica_nuova_dieta(uploaded_file):
    """Carica una nuova dieta da file uploadato"""
    try:
        # Leggi il contenuto del file
        content = uploaded_file.read()
        nuova_dieta = json.loads(content.decode('utf-8'))
        
        # Crea backup della dieta attuale con timestamp
        backup_filename = backup_dieta_attuale()
        
        # Sovrascrivi il file dieta.json
        with open("dieta.json", "w", encoding="utf-8") as f:
            json.dump(nuova_dieta, f, ensure_ascii=False, indent=2)
        
        # Rimuovi il file temporaneo se esiste
        if os.path.exists("dieta_temp.json"):
            os.remove("dieta_temp.json")
        
        return True, backup_filename, nuova_dieta
    except Exception as e:
        return False, str(e), None


def reset_a_dieta():
    """Reset tutti i giorni alla dieta di riferimento"""
    # Usa la dieta attualmente caricata nel session state invece della variabile globale
    dieta_corrente = st.session_state.dieta_edit
    for day in DAYS:
        giorno_reset = {}
        for meal in MEALS:
            giorno_reset[meal] = [dict(a) for a in dieta_corrente.get(meal, [])]
        st.session_state.meal_plan[day] = giorno_reset
    
    # Salva tutto in un unico file
    salva_tutti_dati()


def calcola_recap_settimanale():
    """Calcola il recap di tutti i 35 giorni suddivisi per settimane"""
    recap = {}
    
    # Calcola i totali per ogni singolo giorno
    for day in DAYS:
        giorno_data = st.session_state.meal_plan[day]
        totali_giorno = calcola_totali_giorno(giorno_data)
        recap[day] = totali_giorno
    
    # Calcola i totali per ogni settimana (7 giorni per settimana)
    recap["settimane"] = {}
    for settimana in range(1, 6):  # 5 settimane
        totali_settimana = {"kcal": 0, "carbs": 0, "protein": 0, "fat": 0, "fiber": 0}
        giorni_settimana = []
        
        for giorno_idx in range(7):  # 7 giorni per settimana
            numero_giorno = (settimana - 1) * 7 + giorno_idx + 1
            giorno_id = f"Giorno_{numero_giorno}"
            giorni_settimana.append(giorno_id)
            
            totali_giorno = recap[giorno_id]
            for k in totali_settimana:
                totali_settimana[k] += totali_giorno[k]
        
        recap["settimane"][f"settimana_{settimana}"] = {
            "totali": totali_settimana,
            "giorni": giorni_settimana
        }
    
    return recap


# ==========================
# Streamlit UI
# ==========================

st.set_page_config(page_title="Meal Tracker", layout="wide")
st.sidebar.title("Navigazione")
page = st.sidebar.radio("Vai a:", ["Tracker", "Dieta", "Alimenti", "Recap"], index=0)

# ==========================
# Inizializzazione sessione
# ==========================
if "dieta_edit" not in st.session_state:
    # Carica la dieta dal file temporaneo se esiste, altrimenti dal file originale
    dieta_caricata, da_temp = carica_dieta_temp()
    st.session_state.dieta_edit = {k: [dict(a) for a in v] for k, v in dieta_caricata.items()}
    st.session_state.dieta_da_temp = da_temp

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
    
    # Mostra se la dieta è stata caricata dal file temporaneo
    if st.session_state.get('dieta_da_temp', False):
        st.info("ℹ️ Stai visualizzando una dieta modificata (salvata automaticamente)")
    
    # Pulsanti per gestione dieta
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Reset Dieta", type="secondary"):
            # Cancella il file temporaneo
            if os.path.exists("dieta_temp.json"):
                os.remove("dieta_temp.json")
            
            # Ricarica la dieta originale direttamente da dieta.json
            with open("dieta.json", "r", encoding="utf-8") as f:
                dieta_originale = json.load(f)
            
            # Aggiorna il session state con la dieta originale
            st.session_state.dieta_edit = {k: [dict(a) for a in v] for k, v in dieta_originale.items()}
            st.session_state.dieta_da_temp = False
            st.success("✅ Dieta ripristinata all'originale!")
            st.rerun()
    
    with col2:
        # Mostra il pulsante solo se esistono modifiche da confermare
        if st.session_state.get('dieta_da_temp', False):
            if st.button("💾 Conferma Modifiche", type="primary"):
                success, risultato = conferma_modifiche_dieta()
                if success:
                    st.session_state.dieta_da_temp = False
                    st.success(f"✅ Modifiche confermate! Backup salvato come: {risultato}")
                    st.rerun()
                else:
                    st.error(f"❌ Errore nel confermare le modifiche: {risultato}")
    
    if "dieta_edit" not in st.session_state:
        dieta_caricata, da_temp = carica_dieta_temp()
        st.session_state.dieta_edit = {k: [dict(a) for a in v] for k, v in dieta_caricata.items()}
        st.session_state.dieta_da_temp = da_temp

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
                st.session_state.dieta_da_temp = False  # Reset flag temporaneo
                st.info("🔄 Ricarica la pagina per applicare completamente i cambiamenti alla dieta di riferimento.")
                st.rerun()
            else:
                st.error(f"❌ Errore nel caricamento della dieta: {risultato}")
    
    st.markdown("---")

    dieta_totals = {"kcal": 0, "carbs": 0, "protein": 0, "fat": 0, "fiber": 0}
    
    # Flag per tracciare se ci sono state modifiche
    modifiche_effettuate = False

    for nome_pasto, alimenti in st.session_state.dieta_edit.items():
        st.subheader(nome_pasto)
        for idx, alimento in enumerate(alimenti):
            col1, col2 = st.columns([3, 1])
            with col1:
                # Lista alimenti ordinata alfabeticamente
                alimenti_ordinati = sorted(FOODS.keys())
                nuovo_alimento = st.selectbox(
                    f"Alimento {idx + 1} - {nome_pasto}",
                    alimenti_ordinati,
                    key=f"dieta_{nome_pasto}_food_{idx}",
                    index=alimenti_ordinati.index(alimento["alimento"]) if alimento["alimento"] in alimenti_ordinati else 0
                )
                if nuovo_alimento != alimento["alimento"]:
                    alimento["alimento"] = nuovo_alimento
                    modifiche_effettuate = True
            with col2:
                nuova_quantita = st.number_input(
                    "Quantità (g)",
                    min_value=0,
                    value=int(alimento["quantita"]),
                    key=f"dieta_{nome_pasto}_qty_{idx}"
                )
                if nuova_quantita != alimento["quantita"]:
                    alimento["quantita"] = nuova_quantita
                    modifiche_effettuate = True
        valori = calcola_nutrienti(alimenti)
        st.markdown(
            f"**Kcal:** {valori['kcal']:.0f} | "
            f"**Proteine:** {valori['protein']:.1f} g | "
            f"**Carbo:** {valori['carbs']:.1f} g | "
            f"**Grassi:** {valori['fat']:.1f} g | "
            f"**Fibre:** {valori['fiber']:.1f} g"
        )
        for k in dieta_totals:
            dieta_totals[k] += valori[k]
    
    # Salva automaticamente se ci sono state modifiche
    if modifiche_effettuate:
        salva_dieta_temp(st.session_state.dieta_edit)
        st.session_state.dieta_da_temp = True
        # Forza il rerun per mostrare immediatamente il pulsante "Conferma Modifiche"
        st.rerun()

    st.markdown("---")
    st.success(
        f"**Totali giornalieri target:** {dieta_totals['kcal']:.0f} kcal | "
        f"{dieta_totals['protein']:.1f} g proteine | "
        f"{dieta_totals['carbs']:.1f} g carbo | "
        f"{dieta_totals['fat']:.1f} g grassi | "
        f"{dieta_totals['fiber']:.1f} g fibre"
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
                    # Lista alimenti ordinata alfabeticamente
                    alimenti_ordinati = sorted(FOODS.keys())
                    nuovo_alimento = st.selectbox(
                        f"Nuovo alimento per {nome_pasto}",
                        [""] + alimenti_ordinati,
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
                    # Lista alimenti ordinata alfabeticamente
                    alimenti_ordinati = sorted(FOODS.keys())
                    nuovo_alimento = st.selectbox(
                        f"Alimento {idx + 1}",
                        alimenti_ordinati,
                        key=f"{selected_day}_{nome_pasto}_food_{idx}",
                        index=alimenti_ordinati.index(alimento["alimento"]) if alimento["alimento"] in alimenti_ordinati else 0
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
                f"Proteine: {valori_pasto['protein']:.1f} g | "
                f"Carbo: {valori_pasto['carbs']:.1f} g | "
                f"Grassi: {valori_pasto['fat']:.1f} g | "
                f"Fibre: {valori_pasto['fiber']:.1f} g"
            )

        # Calcola i totali aggiornati dopo tutte le modifiche
        totals = {k: 0 for k in ["kcal", "carbs", "protein", "fat", "fiber"]}
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
                st.metric("Carboidrati", f"{totals['carbs']:.1f}/{dieta_ref['carbs']:.1f} g", delta=f"{totals['carbs'] - dieta_ref['carbs']:.1f}")
            with col3:
                st.metric("Proteine", f"{totals['protein']:.1f}/{dieta_ref['protein']:.1f} g", delta=f"{totals['protein'] - dieta_ref['protein']:.1f}")
            with col4:
                st.metric("Grassi", f"{totals['fat']:.1f}/{dieta_ref['fat']:.1f} g", delta=f"{totals['fat'] - dieta_ref['fat']:.1f}")
            with col5:
                st.metric("Fibre", f"{totals['fiber']:.1f}/{dieta_ref['fiber']:.1f} g", delta=f"{totals['fiber'] - dieta_ref['fiber']:.1f}")

            st.caption(
                f"Differenza rispetto ai target: "
                f"Kcal: {totals['kcal'] - dieta_ref['kcal']:.0f}, "
                f"Carbo: {totals['carbs'] - dieta_ref['carbs']:.1f} g, "
                f"Proteine: {totals['protein'] - dieta_ref['protein']:.1f} g, "
                f"Grassi: {totals['fat'] - dieta_ref['fat']:.1f} g, "
                f"Fibre: {totals['fiber'] - dieta_ref['fiber']:.1f} g."
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
elif page == "Alimenti":
    st.header("🍎 Alimenti")
    st.write("Gestione degli alimenti disponibili nel sistema")
    
    # Carica gli alimenti
    with open('foods.json', 'r', encoding='utf-8') as f:
        foods = json.load(f)
    
    # Form per aggiungere nuovo alimento
    with st.expander("➕ Aggiungi nuovo alimento"):
        with st.form("nuovo_alimento"):
            nome = st.text_input("Nome alimento")
            kcal = st.number_input("Kcal (per 100g)", min_value=0.0, step=0.1)
            carbs = st.number_input("Carboidrati (g per 100g)", min_value=0.0, step=0.1)
            protein = st.number_input("Proteine (g per 100g)", min_value=0.0, step=0.1)
            fat = st.number_input("Grassi (g per 100g)", min_value=0.0, step=0.1)
            fiber = st.number_input("Fibre (g per 100g)", min_value=0.0, step=0.1)
            tipologia = st.multiselect("Tipologia", ["carbs", "protein", "fat", "fiber"])
            
            if st.form_submit_button("Aggiungi alimento"):
                if nome:
                    foods[nome] = {
                        "kcal": kcal,
                        "carbs": carbs,
                        "protein": protein,
                        "fat": fat,
                        "fiber": fiber,
                        "tipologia": tipologia
                    }
                    
                    # Riordina alfabeticamente prima di salvare
                    from collections import OrderedDict
                    foods_ordinati = OrderedDict(sorted(foods.items()))
                    
                    # Salva il file aggiornato e ordinato
                    with open('foods.json', 'w', encoding='utf-8') as f:
                        json.dump(foods_ordinati, f, indent=2, ensure_ascii=False)
                    
                    st.success(f"Alimento '{nome}' aggiunto con successo!")
                    st.rerun()
                else:
                    st.error("Il nome dell'alimento è obbligatorio")
    
    # Elenco alimenti in ordine alfabetico
    st.subheader("📋 Elenco alimenti")
    alimenti_ordinati = sorted(foods.keys())
    
    for alimento in alimenti_ordinati:
        with st.expander(f"🍽️ {alimento}"):
            dati = foods[alimento]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Kcal (per 100g)", f"{dati['kcal']}")
                st.metric("Carboidrati (g)", f"{dati['carbs']}")
                st.metric("Proteine (g)", f"{dati['protein']}")
            
            with col2:
                st.metric("Grassi (g)", f"{dati['fat']}")
                st.metric("Fibre (g)", f"{dati['fiber']}")
                if dati.get('tipologia'):
                    st.write(f"**Tipologia:** {', '.join(dati['tipologia'])}")
            
            # Pulsante per eliminare l'alimento
            if st.button(f"🗑️ Elimina {alimento}", key=f"del_{alimento}"):
                del foods[alimento]
                
                # Riordina alfabeticamente prima di salvare
                from collections import OrderedDict
                foods_ordinati = OrderedDict(sorted(foods.items()))
                
                with open('foods.json', 'w', encoding='utf-8') as f:
                    json.dump(foods_ordinati, f, indent=2, ensure_ascii=False)
                st.success(f"Alimento '{alimento}' eliminato!")
                st.rerun()

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
    
    st.markdown("---")
    
    # Visualizzazione per settimane
    st.subheader("📊 Analisi per Settimane")
    
    for settimana_num in range(1, 6):  # 5 settimane
        settimana_key = f"settimana_{settimana_num}"
        settimana_data = recap_attuale["settimane"][settimana_key]
        totali_settimana = settimana_data["totali"]
        giorni_settimana = settimana_data["giorni"]
        
        with st.expander(f"📅 Settimana {settimana_num}", expanded=False):
            # Metriche totali della settimana
            st.markdown("**Totali Settimana**")
            target_settimana = {k: v * 7 for k, v in dieta_ref.items()}
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                delta = totali_settimana["kcal"] - target_settimana["kcal"]
                st.metric("Kcal", f"{totali_settimana['kcal']:.1f}", f"{delta:+.1f}")
            
            with col2:
                delta = totali_settimana["carbs"] - target_settimana["carbs"]
                st.metric("Carboidrati (g)", f"{totali_settimana['carbs']:.1f}", f"{delta:+.1f}")
            
            with col3:
                delta = totali_settimana["protein"] - target_settimana["protein"]
                st.metric("Proteine (g)", f"{totali_settimana['protein']:.1f}", f"{delta:+.1f}")
            
            with col4:
                delta = totali_settimana["fat"] - target_settimana["fat"]
                st.metric("Grassi (g)", f"{totali_settimana['fat']:.1f}", f"{delta:+.1f}")
            
            with col5:
                delta = totali_settimana["fiber"] - target_settimana["fiber"]
                st.metric("Fibre (g)", f"{totali_settimana['fiber']:.1f}", f"{delta:+.1f}")
    
    st.markdown("---")
    
    # Dettagli per ogni giorno (raggruppati per settimana)
    st.subheader("🔍 Dettagli Completi per Giorno")
    
    for settimana_num in range(1, 6):  # 5 settimane
        st.markdown(f"### Settimana {settimana_num}")
        settimana_key = f"settimana_{settimana_num}"
        giorni_settimana = recap_attuale["settimane"][settimana_key]["giorni"]
        
        for giorno_id in giorni_settimana:
            # Estrai il numero del giorno per la visualizzazione
            numero_giorno = giorno_id.split('_')[1]
            with st.expander(f"Giorno {numero_giorno} - Dettagli"):
                giorno_data = st.session_state.meal_plan[giorno_id]
                totali_giorno = recap_attuale[giorno_id]
                
                # Mostra differenza rispetto ai target
                st.info(
                    f"**Target vs Reale:** "
                    f"Kcal: {totali_giorno['kcal']:.0f}/{dieta_ref['kcal']:.0f} "
                    f"({totali_giorno['kcal'] - dieta_ref['kcal']:+.0f}) | "
                    f"Proteine: {totali_giorno['protein']:.1f}/{dieta_ref['protein']:.1f} g "
                    f"({totali_giorno['protein'] - dieta_ref['protein']:+.1f}) | "
                    f"Carbo: {totali_giorno['carbs']:.1f}/{dieta_ref['carbs']:.1f} g "
                    f"({totali_giorno['carbs'] - dieta_ref['carbs']:+.1f})"
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
                        f"P: {valori_pasto['protein']:.1f}g | "
                        f"C: {valori_pasto['carbs']:.1f}g | "
                        f"G: {valori_pasto['fat']:.1f}g | "
                        f"F: {valori_pasto['fiber']:.1f}g"
                    )
