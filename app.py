"""
🃏 Jack di Cuori — Streamlit Multiplayer Game
app.py

Avvio: streamlit run app.py
"""

import streamlit as st
import json
import os
import time
import random
import string
from pathlib import Path

# ─────────────────────────────────────────────────────
# PAGE CONFIG  (deve essere la prima chiamata Streamlit)
# ─────────────────────────────────────────────────────

st.set_page_config(
    page_title="🃏 Jack di Cuori",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Nascondi chrome Streamlit ── */
#MainMenu, footer, header,
[data-testid="stStatusWidget"],
.stDeployButton { visibility: hidden !important; display: none !important; }

/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&display=swap');

/* ── Sfondo ── */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 30%, #1a0a0a 0%, #0d0d0d 60%, #0a1020 100%);
    min-height: 100vh;
}
[data-testid="stMain"] { background: transparent; }

/* ── Tipografia globale ── */
html, body, [data-testid="stMarkdownContainer"] {
    font-family: 'Crimson Pro', Georgia, serif;
    color: #e8d5b0;
}

/* ── Titolo principale ── */
.hero-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: clamp(2rem, 6vw, 3.5rem);
    text-align: center;
    background: linear-gradient(135deg, #c9a227, #e8d5b0, #c9a227);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0.5rem 0 0.25rem;
    letter-spacing: 0.05em;
    text-shadow: none;
}
.hero-sub {
    text-align: center;
    font-style: italic;
    color: #888;
    font-size: 1.1rem;
    margin: 0 0 1.5rem;
}

/* ── Card semi ── */
.suit-row {
    display: flex; align-items: center; gap: 12px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(201,162,39,0.2);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.suit-name { font-weight: 600; font-size: 1rem; color: #e8d5b0; min-width: 80px; }
.suit-value { font-size: 1.1rem; }

/* ── Codice torneo ── */
.code-box {
    background: rgba(201,162,39,0.12);
    border: 2px solid rgba(201,162,39,0.5);
    border-radius: 12px;
    padding: 16px 24px;
    text-align: center;
    font-family: 'Cinzel Decorative', serif;
    font-size: 2rem;
    letter-spacing: 0.3em;
    color: #c9a227;
    margin: 12px 0;
}

/* ── Badge Jack ── */
.jack-badge {
    background: linear-gradient(135deg, #8b0000, #c0392b);
    border: 1px solid #e74c3c;
    border-radius: 8px;
    padding: 10px 16px;
    margin: 10px 0;
    text-align: center;
    font-weight: 600;
    color: #fff;
}
.player-badge {
    background: linear-gradient(135deg, #0a3d0a, #1a6b1a);
    border: 1px solid #27ae60;
    border-radius: 8px;
    padding: 10px 16px;
    margin: 10px 0;
    text-align: center;
    font-weight: 600;
    color: #fff;
}

/* ── Timer ── */
.timer-green { color: #2ecc71; font-size: 2rem; font-family: monospace; font-weight: bold; }
.timer-yellow { color: #f39c12; font-size: 2rem; font-family: monospace; font-weight: bold; }
.timer-red { color: #e74c3c; font-size: 2rem; font-family: monospace; font-weight: bold; animation: pulse 0.5s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* ── Player list ── */
.player-item {
    padding: 8px 14px;
    border-left: 3px solid rgba(201,162,39,0.4);
    margin-bottom: 6px;
    font-size: 1.05rem;
}
.player-item.me { border-left-color: #c9a227; color: #c9a227; font-weight: 600; }

/* ── Result rows ── */
.result-saved {
    background: rgba(39, 174, 96, 0.12);
    border: 1px solid rgba(39,174,96,0.4);
    border-radius: 8px; padding: 10px 14px; margin: 5px 0;
}
.result-elim {
    background: rgba(231, 76, 60, 0.12);
    border: 1px solid rgba(231,76,60,0.4);
    border-radius: 8px; padding: 10px 14px; margin: 5px 0;
    text-decoration: line-through; color: #888;
}

/* ── Pulsanti personalizzati ── */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #8b6914, #c9a227) !important;
    border: none !important;
    color: #0d0d0d !important;
    font-family: 'Crimson Pro', serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    border-radius: 8px !important;
}
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: 1px solid rgba(201,162,39,0.5) !important;
    color: #c9a227 !important;
    font-family: 'Crimson Pro', serif !important;
}

/* ── Divider ── */
hr { border-color: rgba(201,162,39,0.2) !important; }

/* ── Metriche ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(201,162,39,0.2);
    border-radius: 10px; padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# COSTANTI
# ─────────────────────────────────────────────────────

SUITS = ["❤️ Cuori", "♦️ Quadri", "♣️ Fiori", "♠️ Picche"]
DATA_FILE = "tournaments.json"
POLL_INTERVAL = 2   # secondi tra un rerun e l'altro

# ─────────────────────────────────────────────────────
# DATA LAYER — JSON file come "database" condiviso
# ─────────────────────────────────────────────────────

def _load() -> dict:
    if not Path(DATA_FILE).exists():
        return {"t": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"t": {}}


def _save(data: dict) -> None:
    """Scrittura atomica: scrive su .tmp poi rinomina."""
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def _rand_code(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


# ─────────────────────────────────────────────────────
# GAME LOGIC
# ─────────────────────────────────────────────────────

def create_game(creator: str, max_rounds: int, duration) -> str:
    data = _load()
    code = _rand_code()
    while code in data["t"]:
        code = _rand_code()
    data["t"][code] = {
        "creator":     creator,
        "players":     [creator],
        "jack":        None,
        "max_rounds":  max_rounds,
        "duration":    duration,       # None = aspetta tutti
        "status":      "lobby",        # lobby | round | results | finished
        "round":       0,
        "suits":       {},             # nome → seme (round corrente)
        "guesses":     {},             # nome → guess (round corrente)
        "rd_results":  {},             # nome → "salvato" | "eliminato"
        "eliminated":  [],
        "outcome":     None,           # "players_win" | "jack_wins"
        "history":     [],             # lista round completati
        "timer_start": None,
    }
    _save(data)
    return code


def join_game(code: str, name: str) -> tuple[bool, str, dict | None]:
    data = _load()
    if code not in data["t"]:
        return False, "Codice non trovato.", None
    t = data["t"][code]
    if name in t["players"]:
        return True, "Riconnesso.", t
    if t["status"] != "lobby":
        return False, "La partita è già iniziata.", None
    t["players"].append(name)
    _save(data)
    return True, "Entrato!", t


def start_game(code: str) -> None:
    data = _load()
    t = data["t"][code]
    t["jack"] = random.choice(t["players"])
    _begin_round(t)
    t["status"] = "round"
    _save(data)


def _begin_round(t: dict) -> None:
    t["round"] += 1
    t["guesses"] = {}
    t["rd_results"] = {}
    alive = _alive(t)
    t["suits"] = {p: random.choice(SUITS) for p in alive}
    t["timer_start"] = time.time() if t["duration"] else None


def submit_guess(code: str, name: str, guess: str) -> None:
    data = _load()
    t = data["t"][code]
    if name in t["guesses"]:
        _save(data)
        return
    t["guesses"][name] = guess
    alive = _alive(t)
    if all(p in t["guesses"] for p in alive):
        _evaluate(t)
    _save(data)


def tick_timer(code: str) -> None:
    """Chiamato ad ogni rerun: valuta il round se il timer è scaduto."""
    data = _load()
    t = data["t"].get(code)
    if not t or t["status"] != "round":
        return
    if not t["duration"] or not t["timer_start"]:
        return
    elapsed = time.time() - t["timer_start"]
    if elapsed < t["duration"]:
        return
    alive = _alive(t)
    for p in alive:
        if p not in t["guesses"]:
            # Guess automatico sbagliato per chi non ha risposto in tempo
            suit = t["suits"].get(p, "")
            wrong = [s for s in SUITS if s != suit]
            t["guesses"][p] = random.choice(wrong) if wrong else SUITS[0]
    _evaluate(t)
    _save(data)


def _evaluate(t: dict) -> None:
    alive = _alive(t)
    results = {}
    newly_elim = []
    for p in alive:
        g = t["guesses"].get(p, "")
        r = t["suits"].get(p, "")
        # Il Jack sopravvive sempre (conosce il suo seme)
        if p == t["jack"] or g == r:
            results[p] = "salvato"
        else:
            results[p] = "eliminato"
            newly_elim.append(p)
    t["rd_results"] = results
    t["eliminated"].extend(newly_elim)
    t["history"].append({
        "round":   t["round"],
        "suits":   dict(t["suits"]),
        "guesses": dict(t["guesses"]),
        "results": results,
        "elim":    newly_elim,
    })
    survivors = _alive(t)
    jack = t["jack"]
    non_jack = [s for s in survivors if s != jack]
    if jack not in survivors:
        t["outcome"] = "players_win"
        t["status"] = "finished"
    elif not non_jack:
        t["outcome"] = "jack_wins"
        t["status"] = "finished"
    elif t["round"] >= t["max_rounds"]:
        t["outcome"] = "jack_wins"
        t["status"] = "finished"
    else:
        t["status"] = "results"


def accuse_jack(code: str, accuser: str, suspect: str) -> dict:
    data = _load()
    t = data["t"][code]
    if suspect == t["jack"]:
        t["eliminated"].append(suspect)
        result = {"correct": True, "eliminated": suspect}
    else:
        t["eliminated"].append(accuser)
        result = {"correct": False, "eliminated": accuser}
    survivors = _alive(t)
    jack = t["jack"]
    non_jack = [s for s in survivors if s != jack]
    if jack not in survivors:
        t["outcome"] = "players_win"
        t["status"] = "finished"
    elif not non_jack:
        t["outcome"] = "jack_wins"
        t["status"] = "finished"
    _save(data)
    return result


def next_round(code: str) -> None:
    data = _load()
    t = data["t"][code]
    _begin_round(t)
    t["status"] = "round"
    _save(data)


def get_tournament(code: str) -> dict | None:
    return _load()["t"].get(code)


def _alive(t: dict) -> list[str]:
    return [p for p in t["players"] if p not in t["eliminated"]]


# ─────────────────────────────────────────────────────
# HELPERS SESSION STATE
# ─────────────────────────────────────────────────────

def ss(key, default=None):
    return st.session_state.get(key, default)


def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()


# ─────────────────────────────────────────────────────
# PAGINA: HOME
# ─────────────────────────────────────────────────────

def pg_home():
    st.markdown('<p class="hero-title">🃏 Jack di Cuori</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Scopri il tuo seme. Trova il Jack. Sopravvivi.</p>', unsafe_allow_html=True)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕  Crea Partita", use_container_width=True, type="primary"):
            go("create")
    with col2:
        if st.button("🚪  Unisciti", use_container_width=True):
            go("join")
    st.divider()
    st.markdown("""
<small style="color:#555; text-align:center; display:block;">
Basato su <em>Alice in Borderland</em> — Jack di Cuori
</small>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# PAGINA: CREA PARTITA
# ─────────────────────────────────────────────────────

def pg_create():
    st.markdown('<p class="hero-title" style="font-size:1.8rem">🆕 Crea Partita</p>', unsafe_allow_html=True)
    st.divider()

    name = st.text_input("Il tuo nome", max_chars=20, placeholder="es. Andrea")
    max_rounds = st.slider("Numero di round", 2, 10, 5)
    timed = st.toggle("⏱️ Round a tempo")
    duration = None
    if timed:
        duration = st.slider("Secondi per round", 30, 300, 90, step=15)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Indietro", use_container_width=True):
            go("home")
    with col2:
        if st.button("✅  Crea", type="primary", use_container_width=True):
            if name.strip():
                code = create_game(name.strip(), max_rounds, duration)
                st.session_state.update({
                    "name": name.strip(),
                    "code": code,
                    "is_creator": True,
                    "page": "lobby",
                })
                st.rerun()
            else:
                st.error("Inserisci il tuo nome!")


# ─────────────────────────────────────────────────────
# PAGINA: UNISCITI
# ─────────────────────────────────────────────────────

def pg_join():
    st.markdown('<p class="hero-title" style="font-size:1.8rem">🚪 Unisciti</p>', unsafe_allow_html=True)
    st.divider()

    code = st.text_input("Codice partita", max_chars=10, placeholder="es. AB1234").upper().strip()
    name = st.text_input("Il tuo nome", max_chars=20, placeholder="es. Bruno")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Indietro", use_container_width=True):
            go("home")
    with col2:
        if st.button("✅  Entra", type="primary", use_container_width=True):
            if code and name.strip():
                ok, msg, t = join_game(code, name.strip())
                if ok:
                    st.session_state.update({
                        "name": name.strip(),
                        "code": code,
                        "is_creator": False,
                        "page": "game" if t and t["status"] != "lobby" else "lobby",
                    })
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Compila tutti i campi.")


# ─────────────────────────────────────────────────────
# PAGINA: LOBBY
# ─────────────────────────────────────────────────────

def pg_lobby():
    code = ss("code")
    name = ss("name")
    is_creator = ss("is_creator", False)

    t = get_tournament(code)
    if not t:
        st.error("Partita non trovata.")
        return
    if t["status"] != "lobby":
        go("game")

    st.markdown('<p class="hero-title" style="font-size:1.8rem">🎮 Sala d\'Attesa</p>', unsafe_allow_html=True)
    st.markdown("Condividi il codice con gli altri giocatori:", unsafe_allow_html=True)
    st.markdown(f'<div class="code-box">{code}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Round totali", t["max_rounds"])
    with col2:
        st.metric("Timer", f"{t['duration']}s" if t["duration"] else "Aspetta tutti")

    st.divider()
    st.markdown(f"**👥 Giocatori ({len(t['players'])})**")
    for p in t["players"]:
        css_class = "player-item me" if p == name else "player-item"
        badge = " ← tu" if p == name else ""
        st.markdown(f'<div class="{css_class}">{p}{badge}</div>', unsafe_allow_html=True)

    st.divider()
    if is_creator:
        if len(t["players"]) >= 2:
            if st.button("🚀  Inizia il Gioco!", type="primary", use_container_width=True):
                start_game(code)
                go("game")
        else:
            st.warning("Servono almeno 2 giocatori per iniziare.")
    else:
        st.info("⏳ In attesa che il creatore avvii la partita...")

    time.sleep(POLL_INTERVAL)
    st.rerun()


# ─────────────────────────────────────────────────────
# ROUTER DI GIOCO (smista tra round / risultati / fine)
# ─────────────────────────────────────────────────────

def pg_game():
    code = ss("code")
    name = ss("name")
    is_creator = ss("is_creator", False)

    tick_timer(code)

    t = get_tournament(code)
    if not t:
        st.error("Partita non trovata.")
        return

    status = t["status"]
    if status == "finished":
        pg_finished(t)
    elif status == "results":
        pg_results(t, code, name, is_creator)
    elif status == "round":
        pg_round(t, code, name)
    else:
        st.info(f"Stato: {status}")
        time.sleep(POLL_INTERVAL)
        st.rerun()


# ─────────────────────────────────────────────────────
# PAGINA: ROUND IN CORSO
# ─────────────────────────────────────────────────────

def pg_round(t: dict, code: str, name: str):
    alive = _alive(t)
    is_jack = name == t["jack"]
    is_eliminated = name in t["eliminated"]
    already_guessed = name in t["guesses"]
    my_suit = t["suits"].get(name, "")

    # ── Intestazione ──────────────────────────────
    st.markdown(
        f'<p class="hero-title" style="font-size:1.6rem">'
        f'Round {t["round"]} / {t["max_rounds"]}</p>',
        unsafe_allow_html=True,
    )

    # ── Timer ─────────────────────────────────────
    if t["duration"] and t["timer_start"]:
        elapsed = time.time() - t["timer_start"]
        remaining = max(0.0, t["duration"] - elapsed)
        m, s = int(remaining // 60), int(remaining % 60)
        if remaining < 15:
            css = "timer-red"
        elif remaining < 30:
            css = "timer-yellow"
        else:
            css = "timer-green"
        st.markdown(
            f'<div style="text-align:center">'
            f'<span class="{css}">⏱ {m:02d}:{s:02d}</span></div>',
            unsafe_allow_html=True,
        )

    # ── Badge stato giocatore ─────────────────────
    if is_jack:
        st.markdown(
            '<div class="jack-badge">👑 Sei il <b>Jack di Cuori</b> — '
            'il tuo obiettivo: elimina tutti gli altri!</div>',
            unsafe_allow_html=True,
        )
    elif is_eliminated:
        st.warning("💀 Sei stato eliminato. Puoi guardare ma non giocare.")
    else:
        st.markdown(
            '<div class="player-badge">💚 Sei in gioco — sopravvivi!</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Il proprio seme ───────────────────────────
    if is_jack:
        st.info(f"🃏 Il **tuo** seme (solo tu lo vedi): **{my_suit}**")
    else:
        st.info("🃏 Il **tuo** seme: **❓** — chiedilo agli altri giocatori!")

    # ── Semi degli altri (modificabili localmente) ─
    st.markdown("**👥 Semi degli altri giocatori**")
    st.caption("Puoi modificare le note qui sotto — sono private e non influenzano il gioco.")

    for p in alive:
        if p == name:
            continue
        real_suit = t["suits"].get(p, "")
        lk = f"ls_{code}_{p}"
        if lk not in st.session_state:
            st.session_state[lk] = real_suit

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{p}**")
        with col2:
            idx = SUITS.index(st.session_state[lk]) if st.session_state[lk] in SUITS else 0
            st.selectbox(
                "", SUITS, index=idx, key=lk,
                label_visibility="collapsed",
            )

    # ── Eliminati ─────────────────────────────────
    if t["eliminated"]:
        with st.expander(f"💀 Eliminati ({len(t['eliminated'])})"):
            for e in t["eliminated"]:
                st.write(f"~~{e}~~")

    st.divider()

    # ── Progresso guess ───────────────────────────
    guessed_n = len(t["guesses"])
    alive_n = len(alive)
    st.progress(
        guessed_n / alive_n if alive_n > 0 else 0,
        text=f"Risposte inviate: {guessed_n}/{alive_n}",
    )

    # ── Invio guess ───────────────────────────────
    if not is_eliminated:
        if already_guessed:
            st.success(f"✅ Hai inviato: **{t['guesses'][name]}** — in attesa degli altri...")
        else:
            st.subheader("🎯 Qual è il tuo seme?")
            gk = f"gk_{code}_{t['round']}"
            default_idx = SUITS.index(my_suit) if (is_jack and my_suit in SUITS) else 0
            guess = st.selectbox(
                "Scegli il tuo seme",
                SUITS,
                index=default_idx,
                key=gk,
            )
            if st.button("✅  Invia Guess", type="primary", use_container_width=True):
                submit_guess(code, name, guess)
                st.rerun()

    # ── Auto-refresh ──────────────────────────────
    sleep_time = 1 if (t["duration"] and not already_guessed) else POLL_INTERVAL
    time.sleep(sleep_time)
    st.rerun()


# ─────────────────────────────────────────────────────
# PAGINA: RISULTATI ROUND
# ─────────────────────────────────────────────────────

def pg_results(t: dict, code: str, name: str, is_creator: bool):
    st.markdown(
        f'<p class="hero-title" style="font-size:1.6rem">'
        f'📊 Risultati — Round {t["round"]}</p>',
        unsafe_allow_html=True,
    )

    if not t["history"]:
        st.info("Nessun dato disponibile.")
        return

    last = t["history"][-1]

    # ── Tabella risultati ─────────────────────────
    for pname, result in last["results"].items():
        real = last["suits"].get(pname, "?")
        guess = last["guesses"].get(pname, "?")
        jack_badge = " 👑" if pname == t["jack"] else ""

        if result == "salvato":
            if guess == real:
                label = f"✅ **{pname}{jack_badge}** &nbsp;|&nbsp; Seme: {real} &nbsp;|&nbsp; Guess: {guess} ✓"
            else:
                label = f"✅ **{pname}{jack_badge}** &nbsp;|&nbsp; Seme: {real} *(Jack — salvato automaticamente)*"
            st.markdown(f'<div class="result-saved">{label}</div>', unsafe_allow_html=True)
        else:
            label = f"❌ {pname}{jack_badge} &nbsp;|&nbsp; Seme: {real} &nbsp;|&nbsp; Guess: {guess} ✗"
            st.markdown(f'<div class="result-elim">{label}</div>', unsafe_allow_html=True)

    if last["elim"]:
        st.markdown(f"**Eliminati questo round:** {', '.join(last['elim'])}")

    alive = _alive(t)
    st.markdown(f"**Sopravvissuti:** {', '.join(alive)}")

    st.divider()

    # ── Accusa Jack (opzionale) ───────────────────
    if name in alive and name != t["jack"]:
        with st.expander("🔍 Accusa il Jack di Cuori *(opzionale — rischioso!)*"):
            st.warning(
                "⚠️ Se accusi qualcuno che **non è** il Jack, vieni eliminato tu!  \n"
                "Se accusi quello giusto, il Jack viene eliminato e i giocatori vincono."
            )
            suspects = [p for p in alive if p != name]
            if suspects:
                akk = f"acc_{code}_{t['round']}"
                suspect_sel = st.selectbox("Chi pensi sia il Jack?", suspects, key=akk)
                if st.button(f"⚔️  Accusa {suspect_sel}", type="secondary"):
                    res = accuse_jack(code, name, suspect_sel)
                    if res["correct"]:
                        st.success(f"🎉 Corretto! {res['eliminated']} era il Jack!")
                    else:
                        st.error("❌ Sbagliato — sei stato eliminato!")
                    time.sleep(2)
                    st.rerun()

    st.divider()

    if is_creator:
        if st.button("▶️  Prossimo Round", type="primary", use_container_width=True):
            next_round(code)
            st.rerun()
    else:
        st.info("⏳ In attesa che il creatore avvii il prossimo round...")
        time.sleep(POLL_INTERVAL)
        st.rerun()


# ─────────────────────────────────────────────────────
# PAGINA: FINE PARTITA
# ─────────────────────────────────────────────────────

def pg_finished(t: dict):
    outcome = t["outcome"]

    if outcome == "players_win":
        st.balloons()
        st.markdown(
            '<p class="hero-title">🎉 I Giocatori Vincono!</p>',
            unsafe_allow_html=True,
        )
        st.success(f"Il Jack di Cuori era **{t['jack']}** ed è stato scoperto!")
    else:
        st.markdown(
            '<p class="hero-title">😈 Il Jack Vince!</p>',
            unsafe_allow_html=True,
        )
        st.error(f"**{t['jack']}** era il Jack di Cuori — e ha eliminato tutti.")

    st.divider()

    alive = _alive(t)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🏆 Sopravvissuti**")
        for s in alive:
            badge = " 👑" if s == t["jack"] else ""
            st.write(f"✅ {s}{badge}")
    with col2:
        st.markdown("**💀 Eliminati**")
        for e in t["eliminated"]:
            badge = " 👑" if e == t["jack"] else ""
            st.write(f"❌ {e}{badge}")

    # ── Cronologia completa ───────────────────────
    if t["history"]:
        st.divider()
        with st.expander("📖 Cronologia completa"):
            for rnd in t["history"]:
                st.markdown(f"**Round {rnd['round']}**")
                for pname, suit in rnd["suits"].items():
                    g = rnd["guesses"].get(pname, "?")
                    r = rnd["results"].get(pname, "?")
                    icon = "✅" if r == "salvato" else "❌"
                    jack_tag = " 👑" if pname == t["jack"] else ""
                    st.write(f"  {icon} **{pname}{jack_tag}** — Seme: {suit} | Guess: {g}")
                if rnd["elim"]:
                    st.write(f"  *Eliminati: {', '.join(rnd['elim'])}*")
                st.write("")

    st.divider()
    if st.button("🏠  Torna alla Home", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ─────────────────────────────────────────────────────
# ROUTER PRINCIPALE
# ─────────────────────────────────────────────────────

def main():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    # Auto-sync tra lobby e game se lo stato è cambiato
    code = ss("code")
    if code and ss("page") in ("lobby", "game"):
        t = get_tournament(code)
        if t:
            if t["status"] == "lobby" and ss("page") == "game":
                st.session_state.page = "lobby"
            elif t["status"] != "lobby" and ss("page") == "lobby":
                st.session_state.page = "game"

    pages = {
        "home":   pg_home,
        "create": pg_create,
        "join":   pg_join,
        "lobby":  pg_lobby,
        "game":   pg_game,
    }
    pages.get(ss("page", "home"), pg_home)()


if __name__ == "__main__":
    main()
