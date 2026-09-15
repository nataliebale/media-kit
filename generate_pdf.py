"""Regenerate Natalia-Balakhashvili-Media-Kit.pdf to match the site."""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "Natalia-Balakhashvili-Media-Kit.pdf"

INK = HexColor("#272422")
ROSE = HexColor("#b77668")
PAPER = HexColor("#f4eee7")
SAND = HexColor("#ddc8b5")
MUTED = HexColor("#6d6560")
LINE = HexColor("#e0d4c8")

PAGE_W, PAGE_H = A4
MARGIN = 32

GALLERY = [
    ("ketevannes-heels.png", "KETEVANNESS · GERMANY", "https://www.instagram.com/p/Dc_efxQjCUO/?img_index=1", 0.18, 0.72),
    ("city-stories-2.png", "TRAVEL DIARY · PRAGUE", "https://www.instagram.com/nataliee.balee/p/DY2Ke4jjNJ3/", 0.48, 0.86),
    ("ketevannes-red-shoes.png", "STREET STYLE · LISBON", "https://www.instagram.com/nataliee.balee/p/DbYbqhvjOCc/", 0.22, 0.72),
    ("city-stories-3.png", "CITY STORIES", "https://www.instagram.com/nataliee.balee/p/DbS4F0DDIqE/", 0.42, 0.86),
    ("jellyfish-first.jpeg", "JELLYFISH", "https://www.instagram.com/nataliee.balee/p/DY9_nzHDG43/", 0.12, 0.72),
    ("jellyfish-pouch.png", "JELLYFISH · PORTO", "https://www.instagram.com/nataliee.balee/p/DblWTtiDM-4/", 0.42, 0.78),
    ("destination-reel.jpeg", "DESTINATION REEL", "https://www.instagram.com/nataliee.balee/reel/DbqoC7jMDuj/", 0.45, 0.78),
    ("ketevannes-bag.png", "KETEVANNESS · COAST", "https://www.instagram.com/nataliee.balee/p/Db3a3eDjMX2/", 0.12, 0.72),
    ("city-stories.png", "CITY WALK · PORTO", "https://www.instagram.com/nataliee.balee/p/Db8g7TwDHty/", 0.18, 0.78),
    ("fashion-reel.png", "FASHION REEL", "https://www.instagram.com/nataliee.balee/reel/DciQzIjOTSM/", 0.18, 0.72),
    ("chikos-collab.png", "CHICOS · CAFE DATE", "https://www.instagram.com/nataliee.balee/p/DavYnmkjNvn/", 0.12, 0.78),
    ("vietnam.jpeg", "VIETNAM", "https://www.instagram.com/nataliee.balee/p/DXPDBeDDOBO/", 0.16, 0.72),
]


def fitted(path: Path, w_pt: float, h_pt: float, focus_y: float = 0.35, focus_x: float = 0.5) -> ImageReader:
    im = Image.open(path).convert("RGB")
    target = w_pt / h_pt
    iw, ih = im.size
    if iw / ih > target:
        new_w = max(1, int(ih * target))
        center = int(iw * focus_x)
        left = max(0, min(iw - new_w, center - new_w // 2))
        im = im.crop((left, 0, left + new_w, ih))
    else:
        new_h = max(1, int(iw / target))
        center = int(ih * focus_y)
        top = max(0, min(ih - new_h, center - new_h // 2))
        im = im.crop((0, top, iw, top + new_h))
    im = im.resize((max(2, int(w_pt * 2.6)), max(2, int(h_pt * 2.6))), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=86, optimize=True)
    buf.seek(0)
    return ImageReader(buf)


def round_clip(c: canvas.Canvas, x: float, y: float, w: float, h: float, r: float) -> None:
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    c.clipPath(p, stroke=0, fill=0)


def draw_photo(
    c: canvas.Canvas,
    path: Path,
    x: float,
    y: float,
    w: float,
    h: float,
    focus_y: float = 0.3,
    focus_x: float = 0.5,
    radius: float = 8,
    caption: str | None = None,
    url: str | None = None,
) -> None:
    c.saveState()
    round_clip(c, x, y, w, h, radius)
    c.drawImage(fitted(path, w, h, focus_y, focus_x), x, y, width=w, height=h, mask="auto")
    if caption:
        c.setFillColor(Color(0, 0, 0, alpha=0.4))
        c.rect(x, y, w, 18, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont("Helvetica", 5)
        c.drawString(x + 5, y + 7, caption)
    c.restoreState()
    if url:
        c.linkURL(url, (x, y, x + w, y + h), relative=0, thickness=0)


def header(c: canvas.Canvas, right: str, beige: bool = False) -> None:
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(MARGIN, PAGE_H - 28, "NATALIA BALAKHASHVILI")
    c.setFont("Helvetica", 7)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 28, right)
    c.setStrokeColor(SAND if beige else LINE)
    c.setLineWidth(0.6)
    c.line(MARGIN, PAGE_H - 36, PAGE_W - MARGIN, PAGE_H - 36)


def page_num(c: canvas.Canvas, n: str) -> None:
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W - MARGIN, 22, n)


def build_page1(c: canvas.Canvas) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # Magazine cover: pdf-hero collage fills the right panel with no extra crop.
    hero = Image.open(ASSETS / "pdf-hero.png")
    hero_ratio = hero.size[0] / hero.size[1]
    img_w = PAGE_H * hero_ratio
    img_x = PAGE_W - img_w
    draw_photo(
        c,
        ASSETS / "pdf-hero.png",
        img_x,
        0,
        img_w,
        PAGE_H,
        focus_y=0.5,
        focus_x=0.5,
        radius=0,
        url="https://www.instagram.com/nataliee.balee/p/DblWTtiDM-4/",
    )
    c.setFillColor(white)
    c.setFont("Helvetica", 7)
    c.drawRightString(PAGE_W - 18, 22, "PORTO, PORTUGAL")

    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(36, PAGE_H - 88, "TRAVEL  |  LIFESTYLE  |  FASHION")

    c.setFillColor(INK)
    c.setFont("Times-Roman", 44)
    c.drawString(36, PAGE_H - 162, "MEDIA")
    c.drawString(36, PAGE_H - 212, "KIT")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    text = c.beginText(36, PAGE_H - 268)
    text.setLeading(15)
    text.textLines(
        "Creating personal, art-led travel\nstories with a warm, playful point of\nview."
    )
    c.drawText(text)

    c.setFillColor(white)
    c.roundRect(36, 86, 196, 54, 10, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 118, "@nataliee.balee")
    c.linkURL(
        "https://www.instagram.com/nataliee.balee",
        (50, 108, 188, 130),
        relative=0,
        thickness=0,
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(50, 98, "Tbilisi, Georgia  |  Available worldwide")

    c.setFillColor(ROSE)
    c.setFont("Helvetica", 8)
    c.drawString(36, 36, "2026")


def build_page2(c: canvas.Canvas) -> None:
    header(c, "CREATOR PROFILE")

    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN, PAGE_H - 70, "STORYTELLING THAT FEELS")
    c.setFillColor(INK)
    c.setFont("Times-Italic", 34)
    c.drawString(MARGIN, PAGE_H - 108, "like being there.")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9.5)
    bio = c.beginText(MARGIN, PAGE_H - 142)
    bio.setLeading(14)
    bio.textLines(
        "I'm Natalia, a Tbilisi-based lifestyle, travel and fashion creator. My content\n"
        "blends thoughtful visuals, handwritten details and self-aware humor - turning\n"
        "destinations, stays and everyday moments into stories people want to save and share."
    )
    c.drawText(bio)

    # Lookbook row: coast collage + Porto city walk.
    gap = 10
    photo_w = (PAGE_W - 2 * MARGIN - gap) / 2
    photo_h = photo_w / 0.80
    photo_y = PAGE_H - 198 - photo_h
    draw_photo(
        c,
        ASSETS / "ketevannes-bag.png",
        MARGIN,
        photo_y,
        photo_w,
        photo_h,
        focus_y=0.48,
        radius=8,
        url="https://www.instagram.com/nataliee.balee/p/Db3a3eDjMX2/",
    )
    draw_photo(
        c,
        ASSETS / "city-stories.png",
        MARGIN + photo_w + gap,
        photo_y,
        photo_w,
        photo_h,
        focus_y=0.42,
        radius=8,
        url="https://www.instagram.com/nataliee.balee/p/Db8g7TwDHty/",
    )

    y = photo_y - 28
    box_h = 96
    content_w = PAGE_W - 2 * MARGIN
    c.setFillColor(PAPER)
    c.roundRect(MARGIN, y - box_h, content_w, box_h, 10, stroke=0, fill=1)
    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN + 18, y - 22, "CONTENT PILLARS")
    pillars = [
        "Boutique stays & travel diaries",
        "Fashion as part of the destination story",
        "Cafes, design, local details & real moments",
    ]
    c.setFillColor(INK)
    c.setFont("Helvetica", 9.5)
    py = y - 42
    for line in pillars:
        c.drawString(MARGIN + 18, py, "·   " + line)
        py -= 16

    y = y - box_h - 22
    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN, y, "CONTENT STYLE")
    y -= 16
    c.setFillColor(INK)
    c.setFont("Helvetica", 9)
    style = c.beginText(MARGIN, y)
    style.setLeading(13)
    style.textLines(
        "Premium but personal. Aesthetic without feeling staged. English-language content for\n"
        "an international, travel-minded audience."
    )
    c.drawText(style)
    page_num(c, "02")



def build_page3(c: canvas.Canvas) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    header(c, "AUDIENCE & PERFORMANCE", beige=True)

    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN, PAGE_H - 72, "A SMALL AUDIENCE WITH")
    c.setFillColor(INK)
    c.setFont("Times-Italic", 32)
    c.drawString(MARGIN, PAGE_H - 110, "strong attention.")

    stats = [
        ("2,157", "FOLLOWERS"),
        ("~8%", "ENGAGEMENT RATE"),
        ("221.9K", "30-DAY VIEWS"),
        ("+135", "NEW FOLLOWERS / 30 DAYS"),
    ]
    card_w, card_h, gap = 252, 78, 10
    top = PAGE_H - 148
    for i, (val, label) in enumerate(stats):
        col, row = i % 2, i // 2
        x = MARGIN + col * (card_w + gap)
        y = top - card_h - row * (card_h + gap)
        c.setFillColor(white)
        c.roundRect(x, y, card_w, card_h, 10, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Times-Roman", 26)
        c.drawString(x + 18, y + 38, val)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7)
        c.drawString(x + 18, y + 18, label)

    y = top - 2 * (card_h + gap) - 36
    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN, y, "AUDIENCE SNAPSHOT")
    snap = [("73.5%", "women"), ("59%", "aged 25-34"), ("28.3%", "Georgia"), ("71.7%", "international")]
    y -= 28
    for i, (val, label) in enumerate(snap):
        x = MARGIN + i * 130
        c.setFillColor(INK)
        c.setFont("Times-Roman", 18)
        c.drawString(x, y, val)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(x, y - 14, label)

    y -= 48
    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN, y, "TOP COUNTRIES")
    countries = [
        ("Georgia", 0.94, "28.3%"),
        ("United States", 0.45, "13.5%"),
        ("United Kingdom", 0.18, "5.5%"),
        ("Italy", 0.14, "4.3%"),
        ("Germany", 0.14, "4.3%"),
    ]
    y -= 22
    bar_x, bar_w = 150, 300
    for name, pct, label in countries:
        c.setFillColor(INK)
        c.setFont("Helvetica", 8.5)
        c.drawString(MARGIN, y, name)
        c.setFillColor(SAND)
        c.roundRect(bar_x, y - 1, bar_w, 8, 4, stroke=0, fill=1)
        c.setFillColor(ROSE)
        c.roundRect(bar_x, y - 1, bar_w * pct, 8, 4, stroke=0, fill=1)
        c.setFillColor(MUTED)
        c.drawRightString(PAGE_W - MARGIN, y, label)
        y -= 20

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawString(
        MARGIN,
        40,
        "Recent post engagement calculated from five selected posts. 30-day metrics: 15 Aug-13 Sep 2026.",
    )
    page_num(c, "03")


def build_page4(c: canvas.Canvas) -> None:
    header(c, "SELECTED WORK")

    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN, PAGE_H - 68, "SELECTED WORK")
    c.setFillColor(INK)
    c.setFont("Times-Roman", 26)
    c.drawString(MARGIN, PAGE_H - 98, "The stay becomes")
    c.setFillColor(ROSE)
    c.setFont("Times-Italic", 26)
    c.drawString(MARGIN, PAGE_H - 126, "part of the story.")

    gap, col_gap, drop = 4.2, 3.6, 14
    content_w = PAGE_W - 2 * MARGIN
    col_w = (content_w - 5 * col_gap) / 6
    gallery_top = PAGE_H - 126 - 28

    first, second = GALLERY[:6], GALLERY[6:]
    bottoms = []
    for i, (name, caption, url, focus, aspect) in enumerate(first):
        x = MARGIN + i * (col_w + col_gap)
        h = col_w / aspect
        top = gallery_top - (drop if i % 2 else 0)
        y = top - h
        draw_photo(c, ASSETS / name, x, y, col_w, h, focus_y=focus, radius=5, caption=caption, url=url)
        bottoms.append(y)
    for i, (name, caption, url, focus, aspect) in enumerate(second):
        x = MARGIN + i * (col_w + col_gap)
        h = col_w / aspect
        y = bottoms[i] - gap - h
        draw_photo(c, ASSETS / name, x, y, col_w, h, focus_y=focus, radius=5, caption=caption, url=url)
        bottoms[i] = y

    y = min(bottoms) - 22
    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN, y, "SELECTED BRAND WORK")
    y -= 14
    c.setFillColor(INK)
    c.setFont("Helvetica", 8.5)
    c.drawString(MARGIN, y, "Jellyfish Store  |  Ketevannes  |  fashion, accessories and destination-led collaborations")

    y -= 28
    box_h = 118
    c.setFillColor(PAPER)
    c.roundRect(MARGIN, y - box_h, content_w, box_h, 10, stroke=0, fill=1)
    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN + 16, y - 18, "HOTEL PARTNERSHIP DELIVERABLES")
    items = [
        "01   Instagram Reel — a personality-led stay story built around atmosphere and design.",
        "02   Curated carousel — editorial photography with natural storytelling.",
        "03   Story coverage — real-time moments with tags, location and a path to the property.",
        "04   Edited assets — high-quality photo and video available by agreement.",
    ]
    c.setFillColor(INK)
    c.setFont("Helvetica", 8.2)
    ty = y - 38
    for line in items:
        c.drawString(MARGIN + 16, ty, line)
        ty -= 16

    y = y - box_h - 22
    c.setFillColor(ROSE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN, y, "CONTACT")
    y -= 16
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Instagram")
    c.setFont("Helvetica", 11)
    handle = "@nataliee.balee"
    hx = MARGIN + 62
    c.drawString(hx, y, handle)
    c.linkURL(
        "https://www.instagram.com/nataliee.balee",
        (hx, y - 3, hx + c.stringWidth(handle, "Helvetica", 11), y + 12),
        relative=0,
        thickness=0,
    )
    y -= 16
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, y, "Rates and tailored packages available upon request.")
    page_num(c, "04")


def main() -> None:
    c = canvas.Canvas(str(OUT), pagesize=A4)
    build_page1(c)
    c.showPage()
    build_page2(c)
    c.showPage()
    build_page3(c)
    c.showPage()
    build_page4(c)
    c.save()
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
