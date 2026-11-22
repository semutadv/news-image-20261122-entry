# The Sunday Globe — news-image-20261122

Entry for make.fun's **news-image-20261122**: "Sum up 22 November's world
news in one image."

The entry is a single-file Python program, `main.py` (stdlib only, no
network), that draws a complete newspaper front page for **Sunday,
22 November 2026** and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output/entry.png`). It is fully deterministic — run it twice
and the PNG bytes are identical.

## What's on the page

- A masthead naming the day: **Sunday, 22 November 2026**.
- Three illustrated lead stories: Iran's strike on a Bahraini industrial
  site and tankers hit near the Strait of Hormuz; Russia's 110-missile
  barrage on Ukraine and NATO's vow over Poland; and the COP31 climate
  talks deadlocked in overtime in Antalya. Each lead carries a
  procedurally drawn illustration (a tanker and burning plant, missiles
  over a night skyline, a globe with a thermometer) plus a short summary.
- A dense grid of 30 further stories grouped into six regions —
  Americas, Europe, Middle East, Asia-Pacific, Africa & Global, and
  Money, Science & Sport.
- An hour-by-hour UTC timeline strip of eight timestamped events.

All artwork and the 5×7 pixel typeface used for every letter on the page
are drawn in code, glyph by glyph and pixel by pixel, inside `main.py`
itself. No image assets, no font files, no dependencies.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 -P -s main.py
# writes /tmp/out/entry.png (1024×1024 PNG)
```

## Badges

![competition](https://make.fun/badge/news-image-20261122.svg)
![rank](https://make.fun/badge/news-image-20261122/semutadv/news-image-20261122-entry/rank.svg)
![reward](https://make.fun/badge/news-image-20261122/semutadv/news-image-20261122-entry/reward.svg)

## License

MIT — see `LICENSE`.
