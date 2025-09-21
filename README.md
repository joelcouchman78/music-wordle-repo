# Music Wordle

Two ways to play:

1) Static browser app (no server)
- Open `music-wordle/index.html` in a browser (or host the folder on GitHub Pages/Netlify).

2) Streamlit app (server hosted)
- App code: `music-wordle-streamlit/app.py`
- Dependencies: `requirements.txt` (Streamlit only)

## Streamlit Cloud deploy

1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io and click “New app”.
3. Select your repo/branch and set the app path to `music-wordle-streamlit/app.py`.
4. Deploy. The app reads the bundled dictionary in `music-wordle/allowed-guesses.js`.

Notes
- Answers are curated 5-letter music words (in the app code).
- Guesses validate against an English dictionary parsed from `music-wordle/allowed-guesses.js`.
- You can upload a custom dictionary from the app sidebar (.txt/.json).

## Local run (Streamlit)

```bash
pip install -r requirements.txt
streamlit run music-wordle-streamlit/app.py
```

## Local run (static site)

Open `music-wordle/index.html`, or serve locally:

```bash
python3 -m http.server -d music-wordle 8000
# then open http://localhost:8000/
```

