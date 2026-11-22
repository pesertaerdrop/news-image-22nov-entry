# Sunday 22 November 2026 — The World in One Day

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/pesertaerdrop/news-image-22nov-entry/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/pesertaerdrop/news-image-22nov-entry/reward.svg)](https://make.fun/bounty/news-image-20261122)

One page, one day. **36 stories, 7 regions, every one dated Sunday 22 November 2026.**

## What is on the page

- **Three heroes.** Russia fires 186 drones at Ukraine overnight (161 downed,
  a block in Dymer destroyed); COP31 ends with no deal as fossil fuels are
  left out of the final text; Iran claims it hit two US radars in Bahrain,
  Bahrain denies it and reports two injured.
- **The Day in UTC.** Six timed moments that moved the day, from Hong Kong's
  polls opening at 01:00 UTC to the COP31 approval slipping again at 07:30.
- **Twelve small leads.** Hong Kong's Election Committee, India's 720/9 in
  Wellington, Verstappen in Las Vegas, Wembanyama's 50, the Sparta II fire,
  Iran's power rationing, Bolsonaro in intensive care, the FBI probe, the
  Belgian controllers' strike, Manipur's toxic-liquor toll, the Cikande
  factory fire, the Peru quake.
- **Where it happened.** A dotted world map with numbered pins that match
  the story numbers, and **21 more stories** (16–36), including two forecasts
  still to happen when drawn.
- **Certainty, labelled.** Every story is marked REPORTED, CLAIM or FORECAST,
  with a legend in the footer. A claim is never printed as a fact.
- **Date check.** A closed red box at the foot of the page states the wires
  cutoff (20:15 UTC) and names the big stories deliberately kept out, so no
  reader mistakes a 19–20 November event for a 22 November one.

## How it is made

`make_image.py` draws the page from scratch with Pillow — every picture,
icon and map dot is generated in code, no photo or reference image is
embedded or traced. `main.py` does one thing only: it copies the committed
`entry.png` to `MAKEFUN_OUTPUT_DIR` (default `/output`). It never rebuilds
the image at runtime and never writes into the repository directory, so the
graded program runs cleanly in a read-only sandbox.

## Files

| File | What it is |
| --- | --- |
| `entry.png` | The page itself, 1024×1024, deterministic |
| `make_image.py` | The generator that draws the page |
| `main.py` | Copies `entry.png` to the output directory |
| `LICENSE` | MIT |
| `README.md` | This file |
| `.makefun/owner.json` | Entry owner (payout wallet) |
| `.gitignore` | Ignores Python bytecode |

## Sources

Reuters, BBC, Al Jazeera, DW, Straits Times, Sky News, CNA, ABC, TOI,
Guardian, Kyiv Independent, ISNA, ESPN, FIA, SCMP, Detiknews, Xinhua,
EMSC. Pictures are original, drawn in code.
