import re
import random
import datetime
import hashlib
from pathlib import Path
from typing import List, Tuple

import streamlit as st
import streamlit.components.v1 as components


# Simple haptic feedback helper usable across the module
def haptic():
    try:
        components.html(
            """
            <script>
            try { if (navigator.vibrate) navigator.vibrate(12); } catch(e) {}
            </script>
            """,
            height=0,
        )
    except Exception:
        pass


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
    if 'current_guess' not in st.session_state:
        st.session_state.current_guess = ''


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
      .mw-board { display:flex; flex-direction:column; gap:4px; align-items:center; }
      .mw-row { display:flex; gap:4px; justify-content:center; }
      .mw-tile { --tile-size: 44px; }
      @media (max-width: 420px) { .mw-tile { --tile-size: 38px; } .mw-tile { font-size: 16px; } }
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

    # Handle fallback keyboard clicks via query param (?k=VALUE) using the modern API only
    def _get_qp_key():
        qp = st.query_params
        k = qp.get('k')
        if isinstance(k, list):
            return k[0]
        return k

    def _clear_qp():
        try:
            # Remove only our key to avoid clobbering other params
            if 'k' in st.query_params:
                del st.query_params['k']
        except Exception:
            # As a last resort, clear all
            try:
                st.query_params.clear()
            except Exception:
                pass

    qp_event = _get_qp_key()
    if qp_event:
        # Clear query param first to avoid repeated processing on rerun
        _clear_qp()
        if qp_event == 'ENTER':
            submit_guess_from_state()
        elif qp_event == 'BACK':
            if st.session_state.get('current_guess'):
                st.session_state.current_guess = st.session_state.get('current_guess','')[:-1]
                haptic()
                try:
                    st.rerun()
                except Exception:
                    pass
        elif re.fullmatch(r"[A-Z]", qp_event):
            if len(st.session_state.get('current_guess','')) < COLS:
                st.session_state.current_guess = st.session_state.get('current_guess','') + qp_event.lower()
                haptic()
                try:
                    st.rerun()
                except Exception:
                    pass

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

    # Input form
    def submit_guess_from_state():
        g = re.sub(r"[^A-Za-z]", "", st.session_state.get('current_guess', '')).lower()
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
            st.session_state.current_guess = ''
        haptic()
        # Rerun to refresh board/keyboard
        try:
            st.rerun()
        except Exception:
            import streamlit as _st
            if hasattr(_st, 'experimental_rerun'):
                _st.experimental_rerun()

    if not st.session_state.finished:
        st.write(f"Current guess: {st.session_state.current_guess.upper():<{COLS}}")
        if st.button('Guess', disabled=(len(st.session_state.get('current_guess','')) != COLS)):
            submit_guess_from_state()

        # Colored keyboard removed for reliability on Cloud; using robust fallbacks below

        # Fallback input: typed guess field
        typed = st.text_input('Type a guess (fallback)', key='typed_guess', max_chars=COLS)
        if st.button('Submit typed guess', disabled=(len(typed or '') != COLS)):
            # Use a copy to avoid mutating the widget value
            tg = re.sub(r"[^A-Za-z]", "", typed or '').lower()
            if len(tg) == COLS:
                # Temporarily set current_guess for unified submission path
                st.session_state.current_guess = tg
                submit_guess_from_state()

        # Fallback clickable keyboard using HTML links to avoid column stacking on mobile
        st.caption('If the colored keyboard above does not appear, use this fallback:')
        fb_css = """
        <style>
          .fb-kb { display:flex; flex-direction:column; gap:6px; align-items:center; }
          .fb-row { display:flex; gap:6px; justify-content:center; }
          .fb-key { min-width:28px; padding:7px 6px; border-radius:6px; font-weight:700; font-size:14px; border:none; cursor:pointer; }
          .fb-neutral { background:#1f1f20; color:#f0f0f0; }
          .fb-correct { background:#538d4e; color:#fff; }
          .fb-present { background:#b59f3b; color:#fff; }
          .fb-absent  { background:#3a3a3c; color:#fff; }
          .fb-key:disabled { opacity:.6; cursor:default; }
          @media (max-width:420px){ .fb-key { min-width:24px; font-size:13px; padding:6px 5px; } }
        </style>
        """
        fb_js = """
        <script>
          function fbSet(k){
            try{
              const u=new URL(window.location.href);
              if(k===null){ u.searchParams.delete('k'); } else { u.searchParams.set('k', k); }
              window.location.href = u.toString();
            }catch(e){
              if(k===null){ window.location.search=''; } else { window.location.search='k='+encodeURIComponent(k); }
            }
          }
        </script>
        """
        def fb_row_html(chars):
            parts = []
            for ch in chars:
                stt = key_status.get(ch, '')
                cls = 'fb-neutral'
                if stt == 'correct': cls='fb-correct'
                elif stt == 'present': cls='fb-present'
                elif stt == 'absent': cls='fb-absent'
                parts.append(f'<button type="button" class="fb-key {cls}" onclick="fbSet(\'{ch}\')">{ch}</button>')
            return '<div class="fb-row">' + ''.join(parts) + '</div>'

        # Build rows + enter/back
        rows_html = [fb_row_html(kb_rows[0]), fb_row_html(kb_rows[1])]
        disable_enter = len(st.session_state.current_guess) != COLS
        disable_back = len(st.session_state.current_guess) == 0
        enter_btn = f'<button type="button" class="fb-key fb-neutral" onclick="fbSet(\'ENTER\')" {"disabled" if disable_enter else ""}>ENTER</button>'
        back_btn = f'<button type="button" class="fb-key fb-neutral" onclick="fbSet(\'BACK\')" {"disabled" if disable_back else ""}>⌫</button>'
        row3_keys = ''.join([enter_btn, fb_row_html(kb_rows[2]), back_btn])
        rows_html.append(f'<div class="fb-row">{row3_keys}</div>')
        st.markdown(fb_css + fb_js + '<div class="fb-kb">' + ''.join(rows_html) + '</div>', unsafe_allow_html=True)

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
        components.html(
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
