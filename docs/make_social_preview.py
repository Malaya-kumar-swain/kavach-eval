"""Renders docs/social-preview.png (1280x640), the image GitHub and LinkedIn show for the repo link.

Run:  python docs/make_social_preview.py   (needs Pillow; macOS system fonts)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
OUT = Path(__file__).with_name("social-preview.png")
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


img = Image.new("RGB", (W, H), "#070B17")
d = ImageDraw.Draw(img)

# vertical gradient background
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(7 + 9 * t), int(11 + 15 * t), int(23 + 28 * t)))
# dot grid
for x in range(0, W, 24):
    for y in range(0, H, 24):
        d.point((x + 2, y + 2), fill="#26324F")

# language-gap motif: attack success bars per language, English guard vs layered guard
bars = [("en", 38), ("hi", 83), ("hing", 43), ("or", 67), ("ta", 67)]
for i, (lang, v) in enumerate(bars):
    x0 = 880 + i * 66
    h = int(v * 2.4)
    d.rounded_rectangle([x0, 430 - h, x0 + 40, 430], radius=5, fill=(255, 122, 89) if lang != "en" else (127, 167, 255))
    d.rounded_rectangle([x0 + 8, 426, x0 + 32, 430], radius=2, fill=(95, 211, 154))
    d.text((x0 + 20, 448), lang, font=font(MONO, 18), fill="#94A3B8", anchor="mt")
d.text((880, 486), "English-only guard: leaks", font=font(MONO, 18), fill="#64748B")
d.text((880, 510), "layered guard: 0% everywhere", font=font(MONO, 18), fill="#5FD39A")

# accent bar (saffron → white → green)
for i in range(240):
    t = i / 239
    if t < 0.5:
        a, b, u = (255, 153, 51), (245, 245, 245), t * 2
    else:
        a, b, u = (245, 245, 245), (47, 175, 98), (t - 0.5) * 2
    d.line([(80 + i, 214), (80 + i, 219)], fill=tuple(int(a[k] + (b[k] - a[k]) * u) for k in range(3)))

d.text((76, 110), "Kavach-Eval", font=font(FONT, 92, 1), fill="#F8FAFC")
d.text((80, 250), "Red-team your AI in the languages", font=font(FONT, 36), fill="#C7D2FE")
d.text((80, 298), "India actually speaks.", font=font(FONT, 36), fill="#C7D2FE")
d.text((80, 378), "Prompt injection · Data-leak probes · Hindi, Hinglish,", font=font(FONT, 26), fill="#94A3B8")
d.text((80, 414), "Odia, Tamil · Judge-free scoring · CI release gate", font=font(FONT, 26), fill="#94A3B8")
d.text((80, 548), "github.com/Malaya-kumar-swain/kavach-eval", font=font(MONO, 22), fill="#64748B")
d.text((80, 580), "Apache-2.0 · Python · zero core dependencies", font=font(MONO, 22), fill="#64748B")

img.save(OUT, optimize=True)
print(OUT, img.size)
