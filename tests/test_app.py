import importlib.util
import sys
import types
from pathlib import Path
import unittest


class _DummyContext:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


def load_app_module():
    """Import the Streamlit app module with lightweight stubs if needed."""
    module_name = 'music_wordle_streamlit_app'
    if module_name in sys.modules:
        return sys.modules[module_name]

    # Provide simple stubs so the module can be imported without Streamlit.
    if 'streamlit' not in sys.modules:
        st_stub = types.ModuleType('streamlit')
        st_stub.session_state = {}

        def _noop(*args, **kwargs):
            return None

        st_stub.set_page_config = _noop
        st_stub.markdown = _noop
        st_stub.caption = _noop
        st_stub.title = _noop
        st_stub.write = _noop
        st_stub.info = _noop
        st_stub.success = _noop
        st_stub.text_input = lambda *args, **kwargs: ''
        st_stub.toggle = lambda *args, **kwargs: False
        st_stub.button = lambda *args, **kwargs: False
        st_stub.columns = lambda n, **kwargs: [types.SimpleNamespace(button=lambda *a, **k: False) for _ in range(n)]
        st_stub.file_uploader = lambda *args, **kwargs: None
        st_stub.text_area = _noop
        st_stub.expander = lambda *args, **kwargs: _DummyContext()
        st_stub.sidebar = types.SimpleNamespace(
            header=_noop,
            caption=_noop,
            toggle=lambda *args, **kwargs: False,
            text_input=lambda *args, **kwargs: '',
            button=lambda *args, **kwargs: False,
            write=_noop,
            file_uploader=lambda *args, **kwargs: None,
        )
        st_stub.query_params = {}
        st_stub.rerun = _noop
        sys.modules['streamlit'] = st_stub

    if 'streamlit.components' not in sys.modules:
        components_pkg = types.ModuleType('streamlit.components')
        components_v1 = types.ModuleType('streamlit.components.v1')
        components_v1.html = lambda *args, **kwargs: None
        components_pkg.v1 = components_v1
        sys.modules['streamlit.components'] = components_pkg
        sys.modules['streamlit.components.v1'] = components_v1

    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parents[1] / 'music-wordle-streamlit' / 'app.py',
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module


class TestScoreGuess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = load_app_module()

    def test_score_guess_exact_match(self):
        result = self.app.score_guess('piano', 'piano')
        self.assertEqual(result, ['correct'] * self.app.COLS)

    def test_score_guess_duplicate_handling(self):
        result = self.app.score_guess('allee', 'apple')
        self.assertEqual(result, ['correct', 'present', 'absent', 'absent', 'correct'])


class TestSeededChoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = load_app_module()

    def test_seeded_choice_is_deterministic(self):
        items = ['harps', 'cello', 'oboes']
        pick1 = self.app.seeded_choice(items, 'melody')
        pick2 = self.app.seeded_choice(items, 'melody')
        self.assertEqual(pick1, pick2)
        self.assertIn(pick1, items)


class TestShareSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = load_app_module()

    def test_build_share_summary_format(self):
        statuses = [['correct', 'present', 'absent', 'absent', 'correct']]
        summary = self.app.build_share_summary(statuses, daily=True, seed_str='2024-01-01')
        self.assertEqual(summary[0], 'Music Wordle — Daily 2024-01-01')
        self.assertEqual(summary[1], f'Guesses: 1/{self.app.ROWS}')
        self.assertEqual(summary[2], '🟩🟨⬛⬛🟩')


if __name__ == '__main__':
    unittest.main()
