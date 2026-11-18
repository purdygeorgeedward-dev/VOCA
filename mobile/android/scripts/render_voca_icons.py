"""Render VOCA's Android launcher and store icons from docs/voca-icon.webp.

Run from the repository root after changing the artwork; the outputs are committed:
adaptive foreground and monochrome layers (mipmap-*dpi) and the 512 px store icons.
"""
from collections import deque
from pathlib import Path
from PIL import Image, ImageFilter
NAVY = (1, 21, 69)
im = Image.open("docs/voca-icon.webp").convert("RGBA")
W, H = im.size
px = im.load()
lit = [[max(px[x, y][:3]) > 110 and px[x, y][3] > 0 for x in range(W)] for y in range(H)]
# The artwork's frame/glow is the lit region touching the image edge; the
# launcher mask replaces it, so drop it and keep the content components.
frame = [[False] * W for _ in range(H)]
q = deque((x, y) for x in range(W) for y in (0, H - 1) if lit[y][x])
q.extend((x, y) for y in range(H) for x in (0, W - 1) if lit[y][x])
for x, y in q: frame[y][x] = True
while q:
    x, y = q.popleft()
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nx < W and 0 <= ny < H and lit[ny][nx] and not frame[ny][nx]:
            frame[ny][nx] = True; q.append((nx, ny))
mask = Image.new("L", (W, H), 0)
mp = mask.load()
for y in range(H):
    for x in range(W):
        # Content sits in this box (mic, waves, swoosh); faint glow rings outside it are dropped.
        if lit[y][x] and not frame[y][x] and 120 <= x <= 1125 and 205 <= y <= 1040: mp[x, y] = 255
mask = mask.filter(ImageFilter.MaxFilter(5))  # keep anti-aliased edges
content = Image.new("RGBA", (W, H), (0, 0, 0, 0))
content.paste(im, (0, 0), mask)
bbox = mask.getbbox()
content = content.crop(bbox)

res = Path("mobile/android/app/src/main/res")
for name, scale in {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}.items():
    size = round(108 * scale)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    width = round(66 * scale)  # 66dp of the 108dp canvas: the adaptive-icon safe zone
    height = round(content.height * width / content.width)
    canvas.alpha_composite(content.resize((width, height), Image.LANCZOS), ((size - width) // 2, (size - height) // 2))
    out = res / f"mipmap-{name}" / "voca_launcher_foreground.webp"
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, "WEBP", lossless=True)
    # Themed icons (Android 13+) tint a single-colour silhouette.
    mono = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    mono.putalpha(canvas.getchannel("A"))
    mono.save(out.with_name("voca_launcher_monochrome.webp"), "WEBP", lossless=True)
store = Image.new("RGBA", (512, 512), NAVY + (255,))
width = 400
height = round(content.height * width / content.width)
store.alpha_composite(content.resize((width, height), Image.LANCZOS), ((512 - width) // 2, (512 - height) // 2))
store = store.convert("RGB")
store.save("store/google-play/icon-512.png", optimize=True)
store.save("fastlane/metadata/android/en-US/images/icon.png", optimize=True)
print("bbox", bbox)
