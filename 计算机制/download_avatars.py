"""下载 20 个 avataaars 头像到本地"""
import urllib.request
from pathlib import Path

SEEDS = ['Alex','Jordan','Casey','Morgan','Riley','Taylor','Quinn','Sam',
         'Charlie','Drew','Blake','Avery','Skyler','Reese','Finley','Sage',
         'Harper','Emery','Parker','Rowan']

out_dir = Path(r"c:\Users\苏砚仁\thinknote\gnt计算机制\工具\avatars")
out_dir.mkdir(parents=True, exist_ok=True)

for i, seed in enumerate(SEEDS):
    url = f"https://api.dicebear.com/9.x/avataaars/svg?seed={seed}&size=120"
    out_file = out_dir / f"avatar_{i:02d}_{seed}.svg"
    try:
        urllib.request.urlretrieve(url, out_file)
        print(f"OK: {out_file.name}")
    except Exception as e:
        print(f"FAIL: {seed} - {e}")

print(f"\nDone. Saved to {out_dir}")
