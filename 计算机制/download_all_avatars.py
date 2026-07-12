"""Download all 42 CHARACTER_SEEDS avatars as local SVG files"""
import urllib.request
from pathlib import Path

SEEDS = [
    'Alex','Jordan','Casey','Morgan','Riley','Taylor','Quinn','Sam',
    'Charlie','Drew','Blake','Avery','Skyler','Reese','Finley','Sage',
    'Harper','Emery','Parker','Rowan','Dakota','Phoenix','River','Jamie',
    'Kai','Sasha','Remy','Jules','Ari','Nico','Luca','Ezra','Theo','Ollie',
    'Max','Leo','Mia','Zoe','Eli','Ivy','Asher','Nova','Kiran','Zuri'
]

out_dir = Path(r"c:\Users\苏砚仁\thinknote\gnt计算机制\工具\avatars")
out_dir.mkdir(parents=True, exist_ok=True)

ok = 0
for i, seed in enumerate(SEEDS):
    url = f"https://api.dicebear.com/9.x/avataaars/svg?seed={seed}&size=200"
    out_file = out_dir / f"av_{i:02d}.svg"
    try:
        urllib.request.urlretrieve(url, out_file)
        ok += 1
    except Exception as e:
        print(f"FAIL {i} {seed}: {e}")

print(f"\nDone: {ok}/{len(SEEDS)} downloaded to {out_dir}")
