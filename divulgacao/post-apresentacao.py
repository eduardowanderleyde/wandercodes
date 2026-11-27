# Arte do post de apresentação (1080x1350) com a foto do Eduardo. Uso: python3 -I post-apresentacao.py
import pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = pathlib.Path(__file__).resolve().parent.parent
W, H = 1080, 1350
FUNDO, TEXTO, SUAVE, ACENTO = (11, 12, 14), (243, 241, 236), (160, 162, 170), (200, 240, 49)
NEG = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"; MONO = "/System/Library/Fonts/Menlo.ttc"
im = Image.new("RGB", (W, H), FUNDO)
foto = Image.open(R / "fonte/eduardo-linkedin.png").convert("RGB")      # 874x1092
fundo = foto.resize((W, round(foto.height * W / foto.width))).crop((0, 0, W, 900)).filter(ImageFilter.GaussianBlur(30))
im.paste(Image.blend(fundo, Image.new("RGB", fundo.size, FUNDO), 0.45), (0, 0))
alt = 880; f2 = foto.resize((round(foto.width * alt / foto.height), alt), Image.LANCZOS)
im.paste(f2, ((W - f2.width) // 2, 20))
grad = Image.new("L", (W, H), 0); g = ImageDraw.Draw(grad)
for y in range(520, 870): g.line([(0, y), (W, y)], fill=int(255 * min(1, (y - 520) / 340) ** 1.4))
g.rectangle((0, 870, W, H), fill=255)
im.paste(FUNDO, (0, 0), grad)
d = ImageDraw.Draw(im)
d.text((70, 820), ">_ wandercodes", font=ImageFont.truetype(MONO, 40), fill=ACENTO)
ft = ImageFont.truetype(NEG, 82)
d.text((70, 890), "Sites que dão vontade", font=ft, fill=TEXTO)
d.text((70, 985), "de ", font=ft, fill=TEXTO)
d.text((70 + d.textlength("de ", font=ft), 985), "entrar.", font=ft, fill=ACENTO)
d.text((72, 1110), "Eduardo Wanderley · desenvolvedor no Recife", font=ImageFont.truetype(NEG, 34), fill=SUAVE)
d.rounded_rectangle((70, 1185, 650, 1265), 40, fill=ACENTO)
d.text((110, 1205), "wandercodes.duckdns.org", font=ImageFont.truetype(MONO, 32), fill=FUNDO)
out = pathlib.Path(__file__).with_name("post-apresentacao.png"); im.save(out); print(out)
