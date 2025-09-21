import re
import random
import datetime
import hashlib
from pathlib import Path
from typing import List, Tuple

import streamlit as st
import streamlit.components.v1 as components


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
    <div class="mw-tile" style="
        display:flex; align-items:center; justify-content:center;
        width: var(--tile-size,48px); height: var(--tile-size,48px);
        background: {bg}; border: 2px solid {border}; border-radius: 6px;
        font-weight: 800; font-size: 22px; line-height: 1; color: #e5e5e5; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
        text-transform: uppercase; text-align:center;">
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
        # Secret will be set by seeded picker later in main()
        st.session_state.secret = None
    if 'guesses' not in st.session_state:
        st.session_state.guesses = []  # list[str]
    if 'statuses' not in st.session_state:
        st.session_state.statuses = []  # list[list[str]]
    if 'message' not in st.session_state:
        st.session_state.message = ''
    if 'finished' not in st.session_state:
        st.session_state.finished = False


def new_game():
    # Pick a deterministic secret based on the current seed string
    seed_str = st.session_state.get('seed_str') or 'default'
    st.session_state.secret = seeded_choice(st.session_state.answers, seed_str)
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

    # Sidebar game settings: daily seed vs custom seed
    st.sidebar.header('Game settings')
    daily = st.sidebar.toggle('Daily mode', value=True, help="Use today's UTC date as the seed")
    seed_text = st.sidebar.text_input('Custom seed', value='', placeholder='(ignored if Daily mode is on)')

    # Compute seed string and store for callbacks
    if daily:
        seed_str = datetime.datetime.utcnow().date().isoformat()
    else:
        seed_str = seed_text.strip() or 'default'
    st.session_state.seed_str = seed_str

    # Initialize secret deterministically if not set
    if not st.session_state.secret:
        st.session_state.secret = seeded_choice(st.session_state.answers, seed_str)

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

    st.caption(f"Seeded with: {seed_str}")

    st.title('Music Wordle')

    # Helper to render raw HTML reliably (avoid stray closing tags in markdown)
    def render_html(html: str, height: int):
        # Use components.html for broad Streamlit compatibility across versions
        components.html(html, height=height, scrolling=False)

    # Build entire board as one HTML block with CSS to keep rows intact on mobile
    css = """
    <style>
      .mw-board { display:flex; flex-direction:column; gap:6px; align-items:center; }
      .mw-row { display:flex; gap:6px; justify-content:center; }
      .mw-tile { --tile-size: 48px; }
      @media (max-width: 420px) { .mw-tile { --tile-size: 42px; } .mw-tile { font-size: 18px; } }
    </style>
    """
    rows_html = []
    for r in range(ROWS):
        if r < len(st.session_state.guesses):
            guess = st.session_state.guesses[r]
            status = st.session_state.statuses[r]
            tiles = "".join(tile_html(guess[c].upper(), status[c]) for c in range(COLS))
        else:
            tiles = "".join(tile_html('', '') for _ in range(COLS))
        rows_html.append(f'<div class="mw-row">{tiles}</div>')
    board_html = css + '<div class="mw-board">' + "".join(rows_html) + '</div>'
    render_html(board_html, height=ROWS * 56)

    st.write('')
    st.info(st.session_state.message or 'Guess the music word!')

    # On-screen keyboard status (shows which letters you've tried)
    def compute_key_status(guesses: List[str], stats_rows: List[List[str]]):
        priority = {'absent': 0, 'present': 1, 'correct': 2}
        ks = {ch: '' for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
        for r, guess in enumerate(guesses):
            if r >= len(stats_rows):
                break
            row_stats = stats_rows[r]
            for i, ch in enumerate(guess.upper()):
                if i >= len(row_stats):
                    continue
                stv = row_stats[i] or ''
                if stv not in priority:
                    continue
                cur = ks.get(ch, '')
                if (not cur) or priority[stv] > priority.get(cur, -1):
                    ks[ch] = stv
        return ks

    key_status = compute_key_status(st.session_state.guesses, st.session_state.statuses)
    kb_rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    kb_css = """
    <style>
      .mw-kb { display:flex; flex-direction:column; gap:6px; align-items:center; margin-top: 10px; }
      .mw-kb-row { display:flex; gap:6px; }
      .mw-key { min-width: 30px; padding: 8px 6px; border-radius:6px; background:#2a2a2b; color:#e5e5e5; font-weight:600; font-size:14px; text-align:center; }
      .mw-key.correct { background:#538d4e; }
      .mw-key.present { background:#b59f3b; }
      .mw-key.absent  { background:#3a3a3c; }
      @media (max-width: 420px) { .mw-key { min-width: 26px; font-size:13px; padding:7px 5px; } }
    </style>
    """
    kb_rows_html = []
    for row in kb_rows:
        keys_html = ''.join(f'<div class="mw-key {key_status.get(ch, "")}">{ch}</div>' for ch in row)
        kb_rows_html.append(f'<div class="mw-kb-row">{keys_html}</div>')
    keyboard_html = kb_css + '<div class="mw-kb">' + "".join(kb_rows_html) + '</div>'
    render_html(keyboard_html, height=120)

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
                # Rerun to refresh the board after a submission
                try:
                    st.rerun()
                except Exception:
                    # Fallback for older versions
                    import streamlit as _st
                    if hasattr(_st, 'experimental_rerun'):
                        _st.experimental_rerun()
    else:
        st.success(st.session_state.message)
        # Shareable results block
        summary_lines = build_share_summary(st.session_state.statuses, daily, seed_str)
        result_text = "\n".join(summary_lines)
        with st.expander('Share your result'):
            copy_ui(result_text)

def seeded_choice(items, seed_str: str):
    """Deterministic choice from a list based on the provided seed string."""
    h = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)
    rng = random.Random(h)
    return rng.choice(items)

def build_share_summary(status_rows, daily: bool, seed_str: str):
    title = f"Music Wordle — {'Daily' if daily else 'Seeded'} {seed_str}"
    tries = len(status_rows)
    header = f"Guesses: {tries}/{ROWS}"
    emoji_map = {'correct': '🟩', 'present': '🟨', 'absent': '⬛'}
    grid = ["".join(emoji_map.get(s, '⬛') for s in row) for row in status_rows]
    return [title, header, *grid]

def copy_ui(result_text: str):
    st.text_area('Result', result_text, height=140)
    if st.button('Copy to clipboard'):
        # Inject small JS to copy; works in most browsers/Streamlit hosts
        components.v1.html(
            f"""
            <script>
            const text = {result_text!r};
            navigator.clipboard.writeText(text).then(() => {{
              const el = document.createElement('div');
              el.innerText = 'Copied to clipboard';
              document.body.appendChild(el);
              setTimeout(()=>document.body.removeChild(el), 800);
            }});
            </script>
            """,
            height=0,
        )


if __name__ == '__main__':
    main()
