"""The manual's older name: the player's guide was its only web page (player-guide.html, beside
the Loader) until every player's page became one, in manual/ (manual.py). `python -m
dsloader.guidepage` still writes the whole manual, as `python -m dsloader.manual` does."""

from .manual import *  # noqa: F401,F403
from .manual import main

if __name__ == "__main__":
    main()
