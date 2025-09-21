import re
import random
from pathlib import Path
from typing import List, Tuple

import streamlit as st


# --- Config ---
ROWS = 6
COLS = 5

# Curated 5-letter music answers (same spirit as the web version)
ANSWERS = [
    # Composers / artists
    'haydn','liszt','verdi','ravel','bizet','elgar','satie','grieg','glass','reich','adams','faure','dukas','ibert','nyman',
    'berio','weber','wolfe','sousa','price','rouse',
    'adele','bjork','swift','sting','drake','lorde','seger',

    # Instruments
    'piano','viola','cello','organ','oboes','flute','drums','synth','tabla','sitar','lyres','harps','banjo','reeds',
    'kazoo','guqin','zurna','veena','sarod','rebab','mbira','bongo','conga','shawm','cajon','snare','fifes','pipes',
    'guiro','tiple','viols',

    # Notation, technique, and theory
    'forte','largo','tenor','mezzo','lento','dolce','grave','segue','segno','ossia','pedal','clefs','tacet','tutti',
    'theme','motif','rests','slurs','trill','staff','stave','codas','pitch','voice','lyric','sheet','meter','metre','tempo',
    'sharp','flats','third','fifth','sixth','ninth','tenth','round','drone','beats','riffs','licks','tunes','songs','vocal',
    'notes','score','solfa','cresc','frets','capos','barre','beams','octet','nonet','duets','trios','solos','choir','arias',
    'carol','vibes','sines','mixer','delay','phase','codec','music','audio','hertz',

    # Pieces, forms, dances, styles, and genres
    'canon','fugue','etude','opera','rondo','tango','waltz','missa','motet','suite','gigue','salsa','mambo','rumba','polka',
    'choro','djent','drill','swing','disco','house','grime','metal','indie','blues','folky','samba','bossa','noise','chant',
    'chime','psalm','verse',
]


def load_bundled_dictionary() -> List[str]:
    """Attempt to load the bundled JS dictionary and extract 5-letter words.
    It reads music-wordle/allowed-guesses.js and regex-parses 'word' entries.
    Returns an empty list if not found.
    """
    js_path = Path(__file__).resolve().parent.parent / 'music-wordle' / 'allowed-guesses.js'
    if not js_path.exists():
        return []
    text = js_path.read_text(encoding='utf-8', errors='ignore')
    # Extract 'word' in single quotes, 5 letters
    words = re.findall(r"'([a-z]{5})'", text)
    # Deduplicate while preserving order
    seen = set()
    out = []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


def score_guess(guess: str, answer: str) -> List[str]:
    """Wordle scoring with duplicate handling.
    Returns a list with values in {'correct','present','absent'}.
    """
    res = ['absent'] * COLS
    a = list(answer)
    g = list(guess)

    counts = {}
    for i in range(COLS):
        if g[i] == a[i]:
            res[i] = 'correct'
        else:
            counts[a[i]] = counts.get(a[i], 0) + 1
    for i in range(COLS):
        if res[i] == 'correct':
            continue
        ch = g[i]
        if counts.get(ch, 0) > 0:
            res[i] = 'present'
            counts[ch] -= 1
    return res


def tile_html(ch: str, status: str) -> str:
    colors = {
        'correct': '#538d4e',  # green
        'present': '#b59f3b',  # yellow
        'absent':  '#3a3a3c',  # gray
        'empty':   '#1a1a1b',
    }
    bg = colors['empty'] if not status else colors.get(status, colors['empty'])
    border = bg
    return f"""
    <div style="
        width: 52px; height: 52px; display: grid; place-items: center;
        background: {bg}; border: 2px solid {border}; border-radius: 6px;
        font-weight: 800; font-size: 22px; color: #e5e5e5;
        text-transform: uppercase;">
      {ch}
    </div>
    """


def ensure_state():
    if 'answers' not in st.session_state:
        st.session_state.answers = [w for w in ANSWERS if len(w) == COLS]
    if 'allowed' not in st.session_state:
        bundled = load_bundled_dictionary()
        # Union with answers to ensure every answer is guessable
        allowed = set(bundled or []) | set(st.session_state.answers)
        # Fallback small seed if bundled missing
        if not allowed:
            allowed = set([
                'about','other','which','their','there','first','would','these','music','audio','piano','opera','canon','fugue'
            ])
        st.session_state.allowed = sorted(allowed)
    if 'secret' not in st.session_state:
        st.session_state.secret = random.choice(st.session_state.answers)
    if 'guesses' not in st.session_state:
        st.session_state.guesses = []  # list[str]
    if 'statuses' not in st.session_state:
        st.session_state.statuses = []  # list[list[str]]
    if 'message' not in st.session_state:
        st.session_state.message = ''
    if 'finished' not in st.session_state:
        st.session_state.finished = False


def new_game():
    st.session_state.secret = random.choice(st.session_state.answers)
    st.session_state.guesses = []
    st.session_state.statuses = []
    st.session_state.message = 'New secret picked. Good luck!'
    st.session_state.finished = False


def load_custom_dictionary(file_bytes: bytes):
    text = file_bytes.decode('utf-8', errors='ignore')
    words = []
    # Try JSON array first
    try:
        import json
        parsed = json.loads(text)
        if isinstance(parsed, list):
            words = parsed
    except Exception:
        # Fallback: split by non-alpha
        words = re.split(r"[^A-Za-z]+", text)
    cleaned = [w.strip().lower() for w in words if re.fullmatch(r"[a-z]{5}", str(w).strip().lower())]
    if len(cleaned) < 50:
        st.session_state.message = 'Loaded dictionary seems small; keeping bundled too.'
        # keep bundled
        bundled = load_bundled_dictionary()
        cleaned.extend([w for w in bundled if w not in cleaned])
    # Always include answers
    allowed = set(cleaned) | set(st.session_state.answers)
    st.session_state.allowed = sorted(allowed)


def main():
    st.set_page_config(page_title='Music Wordle (Streamlit)', page_icon='🎵', layout='centered')
    ensure_state()

    # Sidebar controls
    with st.sidebar:
        st.markdown('### 🎵 Music Wordle')
        st.caption('Answers are music-related. Guesses must be valid English 5-letter words.')
        st.button('New Game', on_click=new_game, use_container_width=True)
        st.write(f"Answers: {len(st.session_state.answers)}")
        st.write(f"Dictionary: {len(st.session_state.allowed)}")
        uploaded = st.file_uploader('Load Dictionary (.txt or .json)', type=['txt', 'json'])
        if uploaded is not None:
            load_custom_dictionary(uploaded.getvalue())
            st.success(f"Loaded dictionary with {len(st.session_state.allowed)} words (answers included).")

    st.title('Music Wordle')

    # Grid rendering
    for r in range(ROWS):
        cols = st.columns(COLS, gap='small')
        if r < len(st.session_state.guesses):
            guess = st.session_state.guesses[r]
            status = st.session_state.statuses[r]
            for c in range(COLS):
                with cols[c]:
                    st.markdown(tile_html(guess[c].upper(), status[c]), unsafe_allow_html=True)
        else:
            for c in range(COLS):
                with cols[c]:
                    st.markdown(tile_html('', ''), unsafe_allow_html=True)

    st.write('')
    st.info(st.session_state.message or 'Guess the music word!')

    # Input form
    if not st.session_state.finished:
        with st.form('guess_form', clear_on_submit=True):
            guess = st.text_input('Your guess', max_chars=COLS, help='Type a 5-letter English word and press Guess').strip()
            submitted = st.form_submit_button('Guess')
        if submitted:
            g = re.sub(r"[^A-Za-z]", "", guess).lower()
            if len(g) != COLS:
                st.session_state.message = 'Not enough letters'
            elif g not in st.session_state.allowed:
                st.session_state.message = 'Not in dictionary'
            else:
                res = score_guess(g, st.session_state.secret)
                st.session_state.guesses.append(g)
                st.session_state.statuses.append(res)
                if g == st.session_state.secret:
                    tries = len(st.session_state.guesses)
                    st.session_state.message = f"Bravo! You solved it in {tries} {'try' if tries == 1 else 'tries'}."
                    st.session_state.finished = True
                elif len(st.session_state.guesses) >= ROWS:
                    st.session_state.message = f"Out of guesses — it was “{st.session_state.secret.upper()}”."
                    st.session_state.finished = True
                else:
                    st.session_state.message = ''
                st.experimental_rerun()
    else:
        st.success(st.session_state.message)


if __name__ == '__main__':
    main()

