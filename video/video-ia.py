# Vídeo curto 9:16 com as imagens geradas por IA + frases.
# Uso: python3 -I video-ia.py <emblema.png> [capa.png]  -> video/anuncio-ia.mp4
import pathlib, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = pathlib.Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
FUNDO, TEXTO, ACENTO = (11, 12, 14), (243, 241, 236), (200, 240, 49)
NEG = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"
f = lambda p, s: ImageFont.truetype(p, s)

emblema = Image.open(sys.argv[1]).convert("RGB")
capa = Image.open(sys.argv[2]).convert("RGB") if len(sys.argv) > 2 else None

# (imagem, segundos, frase em linhas, cor de destaque da última linha)
CENAS = [
    ("capa" if capa else "emblema", 3.6, ["Já pensou em ter", "um site pro", "seu negócio?"]),
    ("emblema", 3.6, ["Com um clique,", "um profissional", "à sua disposição."]),
    ("emblema", 3.2, ["Rápido no celular,", "com WhatsApp", "a um toque."]),
    ("fim", 4.2, None),
]

def fundo_de(img):
    s = max(W / img.width, H / img.height)
    b = img.resize((round(img.width * s), round(img.height * s))).filter(ImageFilter.GaussianBlur(40))
    x, y = (b.width - W) // 2, (b.height - H) // 2
    return Image.blend(b.crop((x, y, x + W, y + H)), Image.new("RGB", (W, H), FUNDO), 0.55)

def legenda(linhas, a):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ft = f(NEG, 92); y = 1330
    for i, l in enumerate(linhas):
        w = d.textlength(l, font=ft)
        cor = ACENTO if i == len(linhas) - 1 else TEXTO
        x = (W - w) / 2
        for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4), (4, 4), (-4, 4)):
            d.text((x + dx, y + dy), l, font=ft, fill=(0, 0, 0, 230))
        d.text((x, y), l, font=ft, fill=cor)
        y += 112
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im

def cena_capa(img, t, dur, linhas):
    z = 1.0 + 0.06 * (t / dur)
    s = max(W / img.width, H / img.height) * z
    p = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (p.width - W) // 2, (p.height - H) // 2
    base = p.crop((x, y, x + W, y + H))
    a = min(1, t / 0.35)
    leg = legenda(linhas, a)
    base.paste(leg, (0, 110 + round(30 * (1 - a))), leg)
    return base

def cena_imagem(img, t, dur, linhas):
    base = fundo_de(img)
    z = 1.0 + 0.08 * (t / dur)                     # zoom lento
    lado = round(900 * z)
    p = img.resize((lado, round(img.height * lado / img.width)), Image.LANCZOS)
    y0 = 230 - round((p.height - 900) / 2)
    base.paste(p, ((W - p.width) // 2, y0))
    a = min(1, t / 0.35)
    leg = legenda(linhas, a)
    base.paste(leg, (0, round(30 * (1 - a))), leg)
    return base

def cena_fim(t):
    im = Image.new("RGB", (W, H), FUNDO); d = ImageDraw.Draw(im)
    e = emblema.resize((560, round(emblema.height * 560 / emblema.width)), Image.LANCZOS)
    im.paste(e, ((W - e.width) // 2, 260))
    def c(y, txt, ft, cor):
        w = d.textlength(txt, font=ft); d.text(((W - w) / 2, y), txt, font=ft, fill=cor)
    pulso = 1 + 0.04 * abs(((t * 1.6) % 2) - 1)
    bw, bh = round(860 * pulso), round(150 * pulso)
    d.rounded_rectangle(((W - bw) / 2, 1000 - bh / 2, (W + bw) / 2, 1000 + bh / 2), bh // 2, fill=ACENTO)
    c(960, "Chame no WhatsApp", f(NEG, 66), FUNDO)
    c(1140, "(81) 99490-8227", f(REG, 74), TEXTO)
    c(1290, "wandercodes.duckdns.org", f(MONO, 44), (160, 162, 170))
    c(1420, "Sites que dão vontade de entrar.", f(REG, 46), TEXTO)
    return im

saida = R / "video" / "anuncio-ia.mp4"
cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
       "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
       "-c:a", "aac", "-b:a", "96k", str(saida)]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
anterior = None
for nome, dur, linhas in CENAS:
    n = round(dur * FPS)
    for k in range(n):
        t = k / FPS
        fr = cena_fim(t) if nome == "fim" else (cena_capa(capa, t, dur, linhas) if nome == "capa" else cena_imagem(emblema, t, dur, linhas))
        if anterior is not None and k < 8:          # transição suave entre cenas
            fr = Image.blend(anterior, fr, (k + 1) / 9)
        p.stdin.write(fr.tobytes())
        ultimo = fr
    anterior = ultimo
p.stdin.close(); p.wait()
print(saida, sum(c[1] for c in CENAS), "s")
