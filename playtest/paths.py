# paths.py: the same paths as env.sh, for the Python tools
import os
PT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(PT)
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
GAME = os.environ.get('DS_GAME', os.path.join(WORK, 'inst'))
os.environ['DISPLAY'] = ':55'
os.makedirs(WORK, exist_ok=True)
