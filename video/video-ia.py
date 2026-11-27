# Vídeo curto 9:16 com as imagens geradas por IA + frases, numa estética única.
# Uso: python3 -I video-ia.py <emblema.png> <capa.png>  -> video/anuncio-ia.mp4
import pathlib, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = pathlib.Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
FUNDO, TEXTO, SUAVE, ACENTO, ROXO = (10, 10, 13), (246, 244, 238), (150, 152, 160), (200, 240, 49), (124, 92, 255)
AV = "/System/Library/Fonts/Avenir Next.ttc"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
heavy = lambda s: ImageFont.truetype(AV, s, index=8)
demi = lambda s: ImageFont.truetype(AV, s, index=2)
mono = lambda s: ImageFont.truetype(MONO, s)
ease = lambda t: 1 - (1 - min(max(t, 0), 1)) ** 3

emblema = Image.open(sys.argv[1]).convert("RGB")
capa = Image.open(sys.argv[2]).convert("RGB")

# Frase: lista de linhas; palavras entre * ficam em verde.
CENAS = [
    ("capa", 3.8, ["Já pensou em ter", "um site pro", "*seu negócio?*"]),
    ("emblema", 3.6, ["Com um *clique,*", "um profissional", "à sua disposição."]),
    ("emblema", 3.4, ["Rápido no celular.", "*WhatsApp*", "a um toque."]),
    ("fim", 4.4, None),
]
TOTAL = sum(c[1] for c in CENAS)

# fundo único: preto com brilho roxo em cima e verde embaixo, grade sutil
def fazer_fundo():
    im = Image.new("RGB", (W, H), FUNDO)
    g = Image.new("L", (W, H), 0); d = ImageDraw.Draw(g)
    d.ellipse((-200, -700, W + 200, 500), fill=55)
    im.paste(ROXO, (0, 0), g.filter(ImageFilter.GaussianBlur(220)))
    g = Image.new("L", (W, H), 0); d = ImageDraw.Draw(g)
    d.ellipse((150, 1650, W - 150, 2300), fill=45)
    im.paste(ACENTO, (0, 0), g.filter(ImageFilter.GaussianBlur(240)))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 90): d.line([(x, 0), (x, H)], fill=(16, 16, 20))
    for y in range(0, H, 90): d.line([(0, y), (W, y)], fill=(16, 16, 20))
    return im
FUNDO_IMG = fazer_fundo()

def colar_cartao(base, img, largura, cy, brilho=ACENTO, raio=36):
    p = img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *p.size), raio, fill=255)
    x, y = (W - p.width) // 2, cy - p.height // 2
    s = Image.new("L", (W, H), 0); ImageDraw.Draw(s).rounded_rectangle((x - 6, y - 6, x + p.width + 6, y + p.height + 6), raio + 6, fill=110)
    base.paste(brilho, (0, 0), s.filter(ImageFilter.GaussianBlur(45)))
    base.paste(p, (x, y), m)

def topo(base, t_global):
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((70, 70, W - 70, 78), 4, fill=(40, 40, 48))
    d.rounded_rectangle((70, 70, 70 + (W - 140) * min(1, t_global / TOTAL), 78), 4, fill=ACENTO)
    d.text((70, 104), ">_ wandercodes", font=mono(34), fill=ACENTO)

def frase(base, linhas, t, y0, tam=94):
    """Palavras entram uma a uma, subindo e aparecendo."""
    d = ImageDraw.Draw(base); ft = heavy(tam); alt = round(tam * 1.2)
    n = 0
    for i, linha in enumerate(linhas):
        palavras = linha.split(" ")
        larg = d.textlength(" ".join(p.strip("*") for p in palavras), font=ft)
        x = (W - larg) / 2; y = y0 + i * alt
        verde = False
        for p in palavras:
            if p.startswith("*"): verde = True
            limpa = p.strip("*")
            a = ease((t - 0.11 * n) / 0.35)
            if a > 0:
                cor = ACENTO if verde else TEXTO
                camada = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(camada)
                dd.text((x, y + 26 * (1 - a)), limpa, font=ft, fill=cor + (round(255 * a),))
                base.paste(camada, (0, 0), camada)
            if p.endswith("*"): verde = False
            x += d.textlength(limpa + " ", font=ft); n += 1

def cena_capa(t, dur, linhas, tg):
    base = FUNDO_IMG.copy()
    z = 1.0 + 0.05 * (t / dur)
    s = W / capa.width * z
    p = capa.resize((round(capa.width * s), round(capa.height * s)), Image.LANCZOS)
    x = (p.width - W) // 2; y = round(p.height * 0.1)
    recorte = p.crop((x, y, x + W, y + 1180))
    m = Image.new("L", (W, 1180), 255); dm = ImageDraw.Draw(m)
    for yy in range(0, 140): dm.line([(0, yy), (W, yy)], fill=round(255 * yy / 140))
    for yy in range(800, 1180): dm.line([(0, yy), (W, yy)], fill=round(255 * (1 - (yy - 800) / 380)))
    base.paste(recorte, (0, 150), m)
    topo(base, tg)
    frase(base, linhas, t, 1340)
    return base

def cena_emblema(t, dur, linhas, tg):
    base = FUNDO_IMG.copy()
    colar_cartao(base, emblema, round(800 + 50 * (t / dur)), 730)
    topo(base, tg)
    frase(base, linhas, t, 1320)
    return base

def cena_fim(t, tg):
    base = FUNDO_IMG.copy()
    colar_cartao(base, emblema, 500, 570)
    topo(base, tg)
    d = ImageDraw.Draw(base)
    def c(y, txt, ft, cor):
        w = d.textlength(txt, font=ft); d.text(((W - w) / 2, y), txt, font=ft, fill=cor)
    pulso = 1 + 0.035 * (0.5 + 0.5 * math.sin(t * 5))
    bw, bh = round(780 * pulso), round(136 * pulso)
    d.rounded_rectangle(((W - bw) / 2, 1010 - bh / 2, (W + bw) / 2, 1010 + bh / 2), bh // 2, fill=ACENTO)
    c(972, "Chame no WhatsApp", heavy(58), FUNDO)
    c(1130, "(81) 99490-8227", heavy(78), TEXTO)
    c(1262, "wandercodes.duckdns.org", mono(38), SUAVE)
    c(1400, "Sites que dão vontade de entrar.", demi(46), TEXTO)
    return base

saida = R / "video" / "anuncio-ia.mp4"
cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
       "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
       "-c:a", "aac", "-b:a", "96k", str(saida)]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
tg = 0.0; anterior = None
for nome, dur, linhas in CENAS:
    n = round(dur * FPS)
    for k in range(n):
        t = k / FPS
        if nome == "capa": fr = cena_capa(t, dur, linhas, tg)
        elif nome == "emblema": fr = cena_emblema(t, dur, linhas, tg)
        else: fr = cena_fim(t, tg)
        if anterior is not None and k < 9:
            fr = Image.blend(anterior, fr, (k + 1) / 10)
        p.stdin.write(fr.tobytes())
        ultimo = fr; tg += 1 / FPS
    anterior = ultimo
p.stdin.close(); p.wait()
print(saida, f"{TOTAL:.1f}s")
