import os
import sys


def main():
    # Make the subfolder importable and delegate to the real app
    here = os.path.dirname(os.path.abspath(__file__))
    sub = os.path.join(here, 'music-wordle-streamlit')
    if sub not in sys.path:
        sys.path.insert(0, sub)
    from app import main as run
    run()


if __name__ == '__main__':
    main()

