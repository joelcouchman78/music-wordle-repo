// Music Wordle – standalone client-side game

(function () {
  const ROWS = 6;
  const COLS = 5;

  // Expanded 5-letter music words: composers, pieces/forms, instruments, genres, terms
  // Curated answers only
  const ANSWERS = [
    // Composers / artists
    'haydn','liszt','verdi','ravel','bizet','elgar','satie','grieg','glass','reich','adams','faure','dukas','ibert','nyman',
    'berio','weber','wolfe','sousa','price','rouse',
    'adele','bjork','swift','sting','drake','lorde','seger',

    // Instruments
    'piano','viola','cello','organ','oboes','flute','drums','synth','tabla','sitar','lyres','harps','banjo','reeds',
    'kazoo','guqin','zurna','veena','sarod','rebab','mbira','bongo','conga','shawm','cajon','snare','fifes','pipes',
    'guiro','tiple','viols',

    // Notation, technique, and theory
    'forte','largo','tenor','mezzo','lento','dolce','grave','segue','segno','ossia','pedal','clefs','tacet','tutti',
    'theme','motif','rests','slurs','trill','staff','stave','codas','pitch','voice','lyric','sheet','meter','metre','tempo',
    'sharp','flats','third','fifth','sixth','ninth','tenth','round','drone','beats','riffs','licks','tunes','songs','vocal',
    'notes','score','solfa','cresc','frets','capos','barre','beams','octet','nonet','duets','trios','solos','choir','arias',
    'carol','vibes','sines','mixer','delay','phase','codec','music','audio','hertz',

    // Pieces, forms, dances, styles, and genres
    'canon','fugue','etude','opera','rondo','tango','waltz','missa','motet','suite','gigue','salsa','mambo','rumba','polka',
    'choro','djent','drill','swing','disco','house','grime','metal','indie','blues','folky','samba','bossa','noise','chant',
    'chime','psalm','verse',
  ].filter(w => w.length === 5);

  // Guesses: English 5-letter words. Seed with a small built-in list and
  // allow loading a larger dictionary file via the UI (Load Dictionary).
  const SEED_GUESSES = [
    'about','above','actor','acute','adopt','adult','after','again','agent','agree','ahead','alarm','album','alert','alike','alive','allow','alone','along','alter','among','anger','angle','angry','apart','apple','apply','arena','argue','arise','armed','aside','asset','audio','avoid','awake','award','aware',
    'badly','baker','basic','basis','beach','beard','beast','begin','being','below','bench','birth','black','blade','blame','blank','blast','bleed','blend','bless','blind','block','blood','board','boast','bonus','booth','bored','bound','brain','brand','brave','bread','break','breed','brick','bride','brief','bring','broad','broke','brown','brush','build','built','buyer',
    'cabin','cable','camel','candy','canoe','canon','carry','cause','chain','chair','chalk','charm','chart','chase','cheap','cheat','check','cheer','chest','chief','child','chill','china','choir','chose','cider','civic','civil','claim','class','clean','clear','clerk','click','cliff','climb','cloak','clock','close','cloud','coach','coast','cocoa','color','comic','coral','could','count','court','cover','crack','craft','crash','cream','creep','crest','crisp','crowd','crown','cruel','crush','crust',
    'dance','daily','dairy','daisy','death','debut','delay','dense','depth','diary','digit','diner','donor','doubt','dough','dozen','draft','drain','drama','drawn','dream','dress','drift','drill','drink','drive','drone','droop','drown','dryer','dwarf','dwell',
    'eager','early','earth','eaten','eater','eight','elect','elbow','elder','elite','embed','ember','empty','enact','endow','enjoy','enter','entry','envoy','equal','equip','erase','erect','error','erupt','essay','ethic','every','evict','evoke','exact','exile','exist','expel','extra',
    'faith','false','fancy','favor','feast','fetch','fever','fiber','field','fiery','fifth','fifty','fight','final','finer','first','fixed','flare','flash','fleet','flesh','flick','fling','float','flora','flour','focus','forge','forth','forty','forum','found','frame','fraud','fresh','front','frost','fruit','fully','funny',
    'gauge','gavel','ghost','giant','given','giver','glare','glass','glaze','globe','gloom','glory','glove','going','goose','grade','grain','grand','grant','grape','graph','grasp','grass','grave','great','greed','green','greet','grief','grind','grown','guard','guess','guest','guide','guilt','guise',
    'habit','happy','hardy','harsh','haste','hasty','hatch','haunt','haven','havoc','heavy','hedge','heard','heart','heist','hello','hence','hinge','hobby','holly','honey','honor','horde','horse','hotel','hover','humid','humor','husky','hutch',
    'ideal','ideas','idiom','idiot','idler','idler','igloo','image','imply','inbox','incur','index','inept','infer','input','inter','ionic','irony','issue','itchy',
    'japan','jelly','jerky','jewel','joint','jolly','judge','juice','juicy','jumpy','junky',
    'karma','kayak','kneel','knelt','knife','knock','known','koala',
    'label','labor','laden','lance','large','laser','later','laugh','layer','learn','lease','least','leave','ledge','legal','lemon','level','lever','light','limit','linen','liner','links','liver','livid','lobby','local','logic','loose','loyal','lucky','lunar','lunch','lunge','lurch','lurid',
    'macro','magic','major','maker','maple','march','marker','marry','match','maybe','mayor','meals','meant','media','medic','meets','melon','merit','metal','meter','micro','midst','might','minor','minus','mixed','model','modem','modal','money','month','moral','motor','mount','mouth','movie','music','myths',
    'nabla','nacho','naive','nanny','nasty','naval','navel','needy','nerdy','nerve','never','newer','newly','nicer','niche','niece','night','ninth','noble','nodes','noise','north','notch','noted','novel','nudge','nurse','nylon',
    'oasis','ocean','octet','oddly','offer','often','oiled','older','olive','omega','onion','onset','opera','optic','orbit','order','organ','other','otter','ounce','outer','ovary','ovate','owing','owner',
    'paddy','pagan','paint','panel','panic','paper','parer','parka','party','patch','patio','pause','peace','peach','pearl','pedal','peers','penal','penny','perch','peril','piano','picky','piece','piety','pilot','pinch','pique','pitch','pixel','pizza','place','plain','plane','plant','plate','plead','pleat','plenty','plier','plots','plumb','plush','poems','point','polar','polka','porch','pound','power','press','price','pride','primo','print','prior','prism','prize','probe','prone','proof','proud','prove','pseud','pulse','punch','pupil','purse','pylon',
    'quack','quake','qualm','quart','quash','queen','query','quiet','quilt','quirk','quite','quota','quote',
    'rabid','racer','radii','radio','raise','rally','ranch','range','rapid','ratio','reach','react','ready','realm','rebel','rebut','recap','relax','relay','relic','remit','renew','repay','reply','reset','resin','retro','reuse','rhyme','rider','ridge','right','rigid','riley','rinse','risky','rival','river','roast','robin','robot','rocky','rogue','roman','rough','round','rouse','route','rover','royal','rugby','ruler','rural','rusty',
    'sabre','sugar','safer','saint','salad','salon','sandy','satin','sauce','sauce','sauna','saved','saver','scale','scald','scalp','scare','scarf','scene','scent','scoop','scope','score','scorn','scout','scrap','screw','seams','seats','seize','selle','sense','serif','serve','seven','sever','sewer','shade','shaft','shake','shall','shame','shape','share','shark','sharp','shear','sheep','sheer','sheet','shelf','shell','shift','shine','shiny','shirt','shock','shoot','shore','short','shout','shrub','shrug','sight','silly','since','siren','sixth','sixty','sizey','skate','skirt','skull','slack','slate','slave','sleek','sleep','sleet','slice','slide','slope','small','smart','smell','smile','smoke','snack','snake','sneak','snoop','sober','solar','solid','solve','sonar','sonic','sorry','sound','south','space','spade','spare','spark','speak','spear','speck','speed','spell','spend','spent','sperm','spice','spicy','spike','spill','spine','spice','spoke','sport','spout','spray','spare','squad','squid','stack','stage','stain','stair','stake','stale','stalk','stall','stamp','stand','stare','start','state','stead','steal','steam','steep','steer','stern','stick','stiff','still','sting','stint','stock','stole','stone','stony','stood','stool','stoop','store','storm','story','stout','stove','strap','straw','stuck','study','stuff','stump','style','sugar','suite','sunny','super','surge','swear','sweat','sweep','sweet','swell','swift','swing','syrup',
    'table','taken','taker','tally','talon','tango','taper','tapir','tardy','taste','tasty','teach','teary','teens','teeth','tempo','tense','tenth','tepid','terra','thank','theft','their','theme','there','these','thick','thief','thigh','thing','think','third','those','three','threw','throw','thumb','tiger','tight','timer','timid','tipsy','tired','title','toast','today','token','tonal','tonic','tooth','topic','torch','total','tough','tower','toxic','trace','track','tract','trade','trail','train','trait','trans','trash','treat','trend','trial','tribe','trick','tried','truer','truly','trump','trunk','trust','truth','tubal','tubes','tulip','tummy','tuned','tunic','turbo','turns','tutor','twice','twist',
    'ultra','umbra','uncle','uncut','under','undue','unfit','unify','union','unite','unity','unlit','untie','until','upper','upset','urban','urged','urine','usage','usher','using','usual','utter',
    'vague','valet','valid','value','vapor','vault','vegan','venom','verge','verse','verso','vigor','villa','vinyl','viola','viral','virus','visit','vital','vivid','vocal','vodka','vogue','voice','voted','voter','vouch','vowel',
    'wagon','waist','waive','waltz','waste','watch','water','waver','waxed','weary','weave','wedge','weigh','weird','welsh','whale','wheat','wheel','where','which','while','whine','whirl','whisk','white','whole','whose','wider','widow','width','wield','wight','wills','windy','wiser','wishy','witch','witty','woken','woman','women','woods','woody','wooly','words','world','worry','worse','worst','worth','would','wound','woven','wrack','wrath','wreak','wreck','wrist','write','wrong','wrote','wrung',
    'xenon','xerox','xylem',
    'yacht','yearn','yeast','yield','young','youth',
    'zebra','zesty','zonal'
  ];
  // Start with seed; if bundled dictionary present (window.ALLOWED_GUESSES), prefer it.
  let allowedSet = new Set([
    ...(((typeof window !== 'undefined' && window.ALLOWED_GUESSES && Array.isArray(window.ALLOWED_GUESSES))
      ? window.ALLOWED_GUESSES
      : SEED_GUESSES)),
    ...ANSWERS
  ]);

  const boardEl = document.getElementById('board');
  const keyboardEl = document.getElementById('keyboard');
  const messageEl = document.getElementById('message');
  const newGameBtn = document.getElementById('new-game');
  const loadDictBtn = document.getElementById('load-dict');
  const dictFileInput = document.getElementById('dict-file');
  const dailyToggle = document.getElementById('daily-mode');
  const seedInput = document.getElementById('seed-input');
  const shareBtn = document.getElementById('share-btn');
  const shareText = document.getElementById('share-text');
  const shareContainer = document.getElementById('share-container');

  let secret = null;
  let currentRow = 0;
  let currentCol = 0;
  let grid = Array.from({ length: ROWS }, () => Array(COLS).fill(''));
  let statuses = Array.from({ length: ROWS }, () => Array(COLS).fill('')); // correct/present/absent
  let finished = false;
  let seedStr = computeSeed();

  // Deterministic RNG helpers for seeded choice
  function xmur3(str) {
    let h = 1779033703 ^ str.length;
    for (let i = 0; i < str.length; i++) {
      h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
      h = (h << 13) | (h >>> 19);
    }
    return function () {
      h = Math.imul(h ^ (h >>> 16), 2246822507);
      h = Math.imul(h ^ (h >>> 13), 3266489909);
      h ^= h >>> 16;
      return h >>> 0;
    };
  }
  function mulberry32(a) {
    return function () {
      let t = (a += 0x6D2B79F5);
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function seededChoice(arr, seed) {
    const seedInt = xmur3(seed)();
    const rnd = mulberry32(seedInt);
    const idx = Math.floor(rnd() * arr.length);
    return arr[idx];
  }
  function computeSeed() {
    const daily = dailyToggle ? dailyToggle.checked : true;
    if (daily) {
      const now = new Date();
      const iso = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
        .toISOString()
        .slice(0, 10);
      return iso;
    }
    return (seedInput && seedInput.value.trim()) || 'default';
  }

  // Build board and keyboard UI
  buildBoard();
  buildKeyboard();
  // Init seed + secret
  updateSeedUIState();
  secret = seededChoice(ANSWERS, seedStr);
  updateBoard();
  setMessage(`Guess the music word! Answers: ${ANSWERS.length}, Dictionary: ${allowedSet.size}. Seeded with: ${seedStr}`);

  // Events
  document.addEventListener('keydown', onKeyDown);
  newGameBtn.addEventListener('click', resetGame);
  loadDictBtn.addEventListener('click', () => dictFileInput.click());
  dictFileInput.addEventListener('change', onLoadDictionary);
  if (dailyToggle) dailyToggle.addEventListener('change', onSeedControlsChange);
  if (seedInput) seedInput.addEventListener('input', onSeedControlsChange);
  if (shareBtn) shareBtn.addEventListener('click', onShare);

  function pickSecret() {
    return seededChoice(ANSWERS, seedStr);
  }

  function buildBoard() {
    boardEl.innerHTML = '';
    boardEl.style.gridTemplateRows = `repeat(${ROWS}, 1fr)`;
    for (let r = 0; r < ROWS; r++) {
      const row = document.createElement('div');
      row.className = 'row';
      for (let c = 0; c < COLS; c++) {
        const tile = document.createElement('div');
        tile.className = 'tile';
        tile.id = tileId(r, c);
        row.appendChild(tile);
      }
      boardEl.appendChild(row);
    }
  }

  function buildKeyboard() {
    keyboardEl.innerHTML = '';
    const rows = [
      'QWERTYUIOP',
      'ASDFGHJKL',
      'ENTERZXCVBNM⌫',
    ];
    rows.forEach((row, idx) => {
      const rowEl = document.createElement('div');
      rowEl.className = 'key-row';
      for (const ch of row) {
        const label = ch === '⌫' ? 'BACK' : ch;
        const btn = document.createElement('button');
        btn.className = 'key' + ((label === 'ENTER' || label === 'BACK') ? ' wide' : '');
        btn.textContent = label === 'BACK' ? '⌫' : label;
        btn.dataset.key = label;
        btn.addEventListener('click', () => handleKey(label));
        rowEl.appendChild(btn);
      }
      keyboardEl.appendChild(rowEl);
    });
  }

  function onKeyDown(e) {
    if (finished) return;
    const k = e.key;
    if (k === 'Enter') return handleKey('ENTER');
    if (k === 'Backspace' || k === 'Delete') return handleKey('BACK');
    if (/^[a-z]$/i.test(k)) return handleKey(k.toUpperCase());
  }

  function handleKey(key) {
    if (finished) return;
    if (key === 'ENTER') {
      if (currentCol < COLS) {
        shakeRow(currentRow);
        return setMessage('Not enough letters');
      }
      const guess = grid[currentRow].join('').toLowerCase();
      if (!allowedSet.has(guess)) {
        shakeRow(currentRow);
        return setMessage('Not in dictionary');
      }
      revealGuess(guess);
      return;
    }
    if (key === 'BACK') {
      if (currentCol > 0) {
        currentCol--;
        grid[currentRow][currentCol] = '';
        updateBoard();
      }
      return;
    }
    // Letter
    if (currentCol < COLS) {
      grid[currentRow][currentCol] = key;
      currentCol++;
      updateBoard();
    }
  }

  function revealGuess(guess) {
    const res = scoreGuess(guess, secret);
    statuses[currentRow] = res;
    // Update keyboard statuses with max priority: correct > present > absent
    res.forEach((st, i) => updateKeyStatus(guess[i].toUpperCase(), st));

    flipRow(currentRow, res);

    if (guess === secret) {
      finished = true;
      setMessage(winMessage());
      showShare();
      return;
    }

    currentRow++;
    currentCol = 0;
    if (currentRow >= ROWS) {
      finished = true;
      setMessage(`Out of guesses — it was “${secret.toUpperCase()}”.`);
      showShare();
    } else {
      setMessage('');
    }
  }

  function scoreGuess(guess, answer) {
    const res = Array(COLS).fill('absent');
    const a = answer.split('');
    const g = guess.split('');

    // Count letters in answer
    const counts = {};
    for (let i = 0; i < COLS; i++) {
      if (g[i] === a[i]) {
        res[i] = 'correct';
      } else {
        counts[a[i]] = (counts[a[i]] || 0) + 1;
      }
    }
    // Second pass: present
    for (let i = 0; i < COLS; i++) {
      if (res[i] === 'correct') continue;
      const ch = g[i];
      if (counts[ch] > 0) {
        res[i] = 'present';
        counts[ch]--;
      }
    }
    return res;
  }

  function updateBoard() {
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const el = document.getElementById(tileId(r, c));
        const ch = grid[r][c];
        el.textContent = ch;
        el.classList.toggle('filled', !!ch);
        el.classList.remove('correct', 'present', 'absent');
        if (r < currentRow) {
          const st = statuses[r][c];
          if (st) el.classList.add(st);
        }
      }
    }
  }

  function flipRow(r, res) {
    for (let c = 0; c < COLS; c++) {
      const el = document.getElementById(tileId(r, c));
      el.classList.remove('correct', 'present', 'absent');
      // Small staged delay for flip effect
      setTimeout(() => {
        el.classList.add(res[c]);
      }, c * 120);
    }
  }

  function updateKeyStatus(letter, status) {
    const btn = keyboardEl.querySelector(`[data-key="${letter}"]`);
    if (!btn) return;
    const priority = { absent: 0, present: 1, correct: 2 };
    const current = btn.dataset.status || '';
    if (!current || priority[status] > priority[current]) {
      btn.dataset.status = status;
      btn.classList.remove('absent', 'present', 'correct');
      btn.classList.add(status);
    }
  }

  function setMessage(msg) {
    messageEl.textContent = msg;
  }

  function winMessage() {
    const tries = currentRow + 1;
    const phrases = [
      'Encore!', 'Bravo!', 'Forte!', 'Allegro!', 'In tune!', 'On beat!'
    ];
    const p = phrases[Math.floor(Math.random() * phrases.length)];
    return `${p} You solved it in ${tries} ${tries === 1 ? 'try' : 'tries'}.`;
  }

  function resetGame() {
    seedStr = computeSeed();
    secret = pickSecret();
    currentRow = 0;
    currentCol = 0;
    finished = false;
    grid = Array.from({ length: ROWS }, () => Array(COLS).fill(''));
    statuses = Array.from({ length: ROWS }, () => Array(COLS).fill(''));
    // Reset keyboard colors
    keyboardEl.querySelectorAll('.key').forEach(k => {
      k.dataset.status = '';
      k.classList.remove('absent', 'present', 'correct');
    });
    updateBoard();
    hideShare();
    setMessage(`New secret picked. Seed: ${seedStr}`);
  }

  async function onLoadDictionary(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    try {
      const text = await file.text();
      let words = [];
      // If JSON array provided
      try {
        const parsed = JSON.parse(text);
        if (Array.isArray(parsed)) {
          words = parsed;
        }
      } catch (_) {
        // Fallback: newline or comma-separated text
        words = text.split(/[^A-Za-z]+/g);
      }
      const cleaned = words
        .map(w => String(w || '').trim().toLowerCase())
        .filter(w => /^[a-z]{5}$/.test(w));
      if (cleaned.length < 50) {
        setMessage('Loaded dictionary is quite small; keeping built-in too.');
        cleaned.push(...SEED_GUESSES);
      }
      allowedSet = new Set([...cleaned, ...ANSWERS]);
      setMessage(`Loaded ${allowedSet.size} dictionary words (answers included).`);
    } catch (err) {
      console.error(err);
      setMessage('Could not load dictionary file.');
    } finally {
      dictFileInput.value = '';
    }
  }

  function tileId(r, c) { return `t-${r}-${c}`; }

  function shakeRow(r) {
    const rowEl = boardEl.children[r];
    if (!rowEl) return;
    rowEl.animate([
      { transform: 'translateX(0)' },
      { transform: 'translateX(-6px)' },
      { transform: 'translateX(6px)' },
      { transform: 'translateX(0)' },
    ], { duration: 150, iterations: 2 });
  }

  function updateSeedUIState() {
    if (!dailyToggle || !seedInput) return;
    seedInput.disabled = dailyToggle.checked;
  }

  function onSeedControlsChange() {
    updateSeedUIState();
    resetGame();
  }

  function buildShareSummary() {
    const daily = dailyToggle ? dailyToggle.checked : true;
    const title = `Music Wordle — ${daily ? 'Daily' : 'Seeded'} ${seedStr}`;
    const usedRows = Math.min(currentRow, ROWS);
    const header = `Guesses: ${usedRows}/${ROWS}`;
    const emoji = { correct: '🟩', present: '🟨', absent: '⬛' };
    const rows = [];
    for (let r = 0; r < usedRows; r++) {
      rows.push(statuses[r].map(s => emoji[s] || '⬛').join(''));
    }
    return [title, header, ...rows].join('\n');
  }

  function showShare() {
    if (!shareBtn || !shareText || !shareContainer) return;
    const text = buildShareSummary();
    shareText.value = text;
    shareBtn.style.display = 'inline-block';
    shareContainer.style.display = 'block';
  }
  function hideShare() {
    if (!shareBtn || !shareText || !shareContainer) return;
    shareBtn.style.display = 'none';
    shareContainer.style.display = 'none';
    shareText.value = '';
  }
  function onShare() {
    const text = shareText.value;
    if (!text) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        setMessage('Copied result to clipboard');
      }).catch(() => {
        setMessage('Copy failed — select text and press Ctrl/Cmd+C');
      });
    } else {
      shareText.select();
      setMessage('Select text and press Ctrl/Cmd+C');
    }
  }
})();
