# Capa do Facebook (1640x624) no visual do site. Uso: python3 -I capa.py
import pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = pathlib.Path(__file__).resolve().parent.parent
W, H = 1640, 624
FUNDO, TEXTO, SUAVE, ACENTO = (11, 12, 14), (243, 241, 236), (160, 162, 170), (200, 240, 49)
NEG = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"; MONO = "/System/Library/Fonts/Menlo.ttc"
im = Image.new("RGB", (W, H), FUNDO); d = ImageDraw.Draw(im)
for x in range(0, W, 64): d.line([(x, 0), (x, H)], fill=(22, 24, 28))
for y in range(0, H, 64): d.line([(0, y), (W, y)], fill=(22, 24, 28))
brilho = Image.new("L", (W, H), 0); ImageDraw.Draw(brilho).ellipse((W * .55, -200, W * 1.15, H + 200), fill=90)
im.paste((124, 92, 255), (0, 0), brilho.filter(ImageFilter.GaussianBlur(140)))
d = ImageDraw.Draw(im)
# telas dos três sites (lado direito, dentro da área que aparece no celular)
def tela(nome, w):
    p = Image.open(R / "site/midia" / f"{nome}.webp").convert("RGB"); h = round(w * 9 / 16)
    p = p.resize((w, h), Image.LANCZOS); bar = 26
    t = Image.new("RGB", (w, h + bar), (23, 25, 30)); t.paste(p, (0, bar))
    dd = ImageDraw.Draw(t)
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]): dd.ellipse((12 + i * 18, 8, 22 + i * 18, 18), fill=c)
    m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *t.size), 14, fill=255)
    return t, m
for nome, w, x, y in [("bacurau", 360, 930, 70), ("niedja", 360, 1190, 320), ("toca", 440, 1010, 190)]:
    t, m = tela(nome, w)
    s = Image.new("L", (t.width + 80, t.height + 80), 0); ImageDraw.Draw(s).rounded_rectangle((40, 50, t.width + 40, t.height + 50), 14, fill=170)
    im.paste((0, 0, 0), (x - 40, y - 40), s.filter(ImageFilter.GaussianBlur(22)))
    im.paste(t, (x, y), m)
    ImageDraw.Draw(im).rounded_rectangle((x, y, x + t.width - 1, y + t.height - 1), 14, outline=(200, 240, 49) if nome == "toca" else (60, 62, 70), width=2)
d = ImageDraw.Draw(im)
# texto (lado esquerdo, acima de onde fica a foto do perfil)
d.text((300, 140), ">_ wandercodes", font=ImageFont.truetype(MONO, 34), fill=ACENTO)
ft = ImageFont.truetype(NEG, 54)
d.text((300, 200), "Sites que dão vontade", font=ft, fill=TEXTO)
d.text((300, 264), "de ", font=ft, fill=TEXTO)
d.text((300 + d.textlength("de ", font=ft), 264), "entrar.", font=ft, fill=ACENTO)
d.text((302, 352), "Recife · WhatsApp (81) 99490-8227", font=ImageFont.truetype(NEG, 26), fill=SUAVE)
d.text((302, 394), "wandercodes.duckdns.org", font=ImageFont.truetype(MONO, 24), fill=SUAVE)
out = pathlib.Path(__file__).with_name("capa-facebook.png"); im.save(out); print(out)
