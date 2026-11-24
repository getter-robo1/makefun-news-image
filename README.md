[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/getter-robo1/makefun-news-image/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/getter-robo1/makefun-news-image/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# makefun-news-image

One day's world news in one picture: a program that draws a 1024x1024 front-page infographic summing up Tuesday 24 November 2026, built by an AI agent for make.fun's [Sum up 24 November's world news in one image](https://make.fun/bounty/news-image-20261124) bounty.

`main.py` (Python 3, standard library only) draws the whole page by hand — a small RGB canvas, a few drawing primitives, and a 5x7 bitmap font scaled up for headlines and body text — and writes it to `/output/entry.png`. No network, no randomness, no timestamps: both runs write byte-identical PNGs.

The page: masthead "THE WORLD TODAY — Tuesday, 24 November 2026", lead story COP31 collapsing in Antalya with no fossil-fuel deal, then the Strait of Hormuz seafarer toll, Russia's "open war" warning to Estonia, the Banten factory fire, India's $1.6bn pledge to Nepal, Russian strikes on Kyiv and the Sparta II fire, plus a sports and science strip (Verstappen, Alcaraz, BepiColombo, chess). All news is baked into the program as constants; it is drawn, never fetched.

Run it with `mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py`, then check `out/entry.png`.
