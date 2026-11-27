# Anúncios 9:16 com os sites rolando dentro de um celular (Benefício, Problema, Método).
# Uso: python3 -I video/anuncios_celular.py [beneficio|problema|metodo]  -> video/anuncio-<nome>.mp4
# Precisa dos quadros em fonte/celular/{bacurau,toca,bacurau2,toca2}/q_0001.jpg... (video/gravar_celular.mjs;
# bacurau2 = 170 1800 1700 e toca2 = 170 2200 1900)
# e da música video/musica/beneficio.mp3 (vidIQ, livre de direitos).
import math, pathlib, random, struct, subprocess, tempfile, wave
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CEL = RAIZ / "fonte" / "celular"
W, H, FPS = 1080, 1920, 30
FUNDO, TEXTO, SUAVE, ACENTO, CARTAO = (11, 12, 14), (243, 241, 236), (160, 162, 170), (200, 240, 49), (24, 27, 31)

def achar(*ps):
    return next((p for p in ps if pathlib.Path(p).exists()), ps[-1])
LIB = "/usr/share/fonts/truetype/liberation/"
NEG = achar("/System/Library/Fonts/Supplemental/Arial Bold.ttf", LIB + "LiberationSans-Bold.ttf")
REG = achar("/System/Library/Fonts/Supplemental/Arial.ttf", LIB + "LiberationSans-Regular.ttf")
MONO = achar("/System/Library/Fonts/Menlo.ttc", LIB + "LiberationMono-Regular.ttf")
f = lambda p, s: ImageFont.truetype(p, s)
MED = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
vazio = lambda: Image.new("RGBA", (W, H), (0, 0, 0, 0))

# cenas: (início, fim)
A, B, C, D, E = (0, 3.4), (3.4, 6.4), (6.4, 10.9), (10.9, 15.4), (15.4, 19.5)
TOTAL = E[1]
TELA = (240, 560, 840, 1760)  # tela do celular (600x1200)

camadas, cliques, whooshes = [], [], [A[0], B[0], C[0], D[0], E[0]]
def por(img, ini, fim, fade=0.2, clique=False):
    camadas.append((img, ini, fim, fade))
    if clique: cliques.append(ini)

# ---------- peças
def fundo():
    im = Image.new("RGB", (W, H), FUNDO); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line((x, 0, x, H), fill=(18, 20, 22))
    for y in range(0, H, 60): d.line((0, y, W, y), fill=(18, 20, 22))
    brilho = Image.new("L", (W, H), 0); ImageDraw.Draw(brilho).ellipse((140, 700, 940, 1500), fill=70)
    brilho = brilho.filter(ImageFilter.GaussianBlur(160))
    im.paste(Image.new("RGB", (W, H), (60, 80, 20)), (0, 0), brilho)
    return im.convert("RGBA")

def celular(bg):
    im = bg.copy(); d = ImageDraw.Draw(im)
    sombra = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sombra).rounded_rectangle((235, 575, 865, 1805), 80, fill=200)
    im.paste((0, 0, 0), (0, 0), sombra.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((220, 540, 860, 1780), 72, fill=(28, 30, 34), outline=(80, 82, 90), width=3)
    furo = Image.new("L", (W, H), 0); ImageDraw.Draw(furo).rounded_rectangle(TELA, 52, fill=255)
    im.putalpha(Image.eval(furo, lambda v: 255 - v))
    return im

def titulo(linhas, ini, fim, y=150, tam=104):
    while tam > 50 and max(MED.textlength(l.strip("*"), font=f(NEG, tam)) for l in linhas) > W - 120:
        tam -= 2
    ft, passo, n = f(NEG, tam), round(tam * 1.12), 0
    for l in linhas:
        cor = ACENTO if l.startswith("*") else TEXTO; l = l.strip("*")
        x = (W - MED.textlength(l, font=ft)) / 2
        for p in l.split(" "):
            im = vazio(); d = ImageDraw.Draw(im)
            d.text((x + 4, y + 6), p, font=ft, fill=(0, 0, 0, 170)); d.text((x, y), p, font=ft, fill=cor)
            por(im, ini + 0.1 + n * 0.12, fim, 0.15); n += 1
            x += MED.textlength(p + " ", font=ft)
        y += passo
    return y

def cartao(caixa):
    im = vazio(); d = ImageDraw.Draw(im)
    d.rounded_rectangle(caixa, 40, fill=CARTAO + (245,), outline=(52, 56, 62), width=2)
    return im

def check(d, cx, cy, r=34):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACENTO)
    d.line((cx - 15, cy + 1, cx - 4, cy + 13, cx + 17, cy - 12), fill=FUNDO, width=8, joint="curve")

def etiqueta(texto, x, y, lado):
    im = vazio(); d = ImageDraw.Draw(im); ft = f(NEG, 48)
    w = MED.textlength(texto, font=ft) + 110
    x0 = x if lado == "esq" else x - w
    d.rounded_rectangle((x0 + 6, y + 8, x0 + w + 6, y + 96), 44, fill=(0, 0, 0, 120))
    d.rounded_rectangle((x0, y, x0 + w, y + 88), 44, fill=ACENTO)
    check(d, x0 + 46, y + 44, 24)
    d.text((x0 + 82, y + 18), texto, font=ft, fill=FUNDO)
    return im

def rodape(url):
    im = vazio(); d = ImageDraw.Draw(im); ft = f(MONO, 32)
    d.text(((W - MED.textlength(url, font=ft)) / 2, 1820), url, font=ft, fill=SUAVE)
    return im

def balao(texto, y, dir_, ft):
    im = vazio(); d = ImageDraw.Draw(im); w = MED.textlength(texto, font=ft) + 64
    x0 = 950 - w if dir_ else 130
    d.rounded_rectangle((x0, y, x0 + w, y + ft.size + 44), 34, fill=ACENTO if dir_ else (44, 48, 54))
    d.text((x0 + 32, y + 20), texto, font=ft, fill=FUNDO if dir_ else TEXTO)
    return im

# ---------- roteiros
ROTEIROS = {
    "beneficio": dict(
        a=("chat", ["PERGUNTEI PRA IA:", "*ONDE IR HOJE*", "*NO RECIFE?*"], "onde ir hoje no Recife?"),
        b=(["ELA INDICA QUEM", "*ELA CONSEGUE ACHAR*"], "o que a IA confere", "ok",
           ["Site com endereço", "Horário e agenda", "Avaliações no Google"]),
        sites=[("bacurau", ["ESPAÇO CULTURAL", "*COM SITE PRÓPRIO*"], "casabacurau.com.br",
                [("Agenda", "esq", 820), ("Endereço", "dir", 1120), ("Ingresso", "esq", 1420)]),
               ("toca", ["BANDA PRA FESTA", "*QUE SE CONTRATA*"], "tocadocuco.duckdns.org",
                [("Show", "dir", 820), ("Contratar", "esq", 1120), ("WhatsApp", "dir", 1420)])],
        fim=["SEU NEGÓCIO", "APARECE QUANDO", "*PERGUNTAM?*"]),
    "problema": dict(
        a=("dms", ["SEU NEGÓCIO SÓ", "EXISTE NO", "*INSTAGRAM?*"],
           ["qual o endereço?", "abre hoje?", "como compro ingresso?", "tem agenda do mês?"]),
        b=(["O CLIENTE NÃO ACHA", "*E DESISTE*"], "perdido entre posts e stories", "x",
           ["Endereço", "Horário", "Agenda e preços"]),
        sites=[("bacurau2", ["NO SITE ESTÁ", "*TUDO NUM LUGAR SÓ*"], "casabacurau.com.br",
                [("Agenda", "esq", 820), ("Datas e horários", "dir", 1120), ("Lojinha", "esq", 1420)]),
               ("toca2", ["E QUEM QUER", "*CONTRATA DIRETO*"], "tocadocuco.duckdns.org",
                [("Contratar", "dir", 820), ("Sobre a banda", "esq", 1120), ("WhatsApp", "dir", 1420)])],
        fim=["SEU NEGÓCIO", "MERECE UM", "*ENDEREÇO SEU*"]),
    "metodo": dict(
        a=("toque", ["SEU CLIENTE", "CHAMA VOCÊ", "*COM UM TOQUE?*"], "Oi! Vi o site, quero um orçamento"),
        b=(["O SITE FAZ", "*O CAMINHO CURTO*"], "do site pro seu WhatsApp", "ok",
           ["Botão sempre à vista", "Mensagem já escrita", "Abre direto no celular"]),
        sites=[("toca2", ["UM TOQUE E", "*JÁ É CONVERSA*"], "tocadocuco.duckdns.org",
                [("Contratar um show", "dir", 820), ("Botão fixo", "esq", 1120), ("WhatsApp", "dir", 1420)]),
               ("bacurau", ["AGENDA À MÃO,", "*CONTATO TAMBÉM*"], "casabacurau.com.br",
                [("Ver a agenda", "esq", 820), ("Ingresso", "dir", 1120), ("WhatsApp", "dir", 1420)])],
        fim=["MENOS CLIQUES,", "*MAIS CLIENTES*"]),
}

def xis(d, cx, cy, r=34):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(70, 72, 78))
    for s_ in (1, -1):
        d.line((cx - 13, cy - 13 * s_, cx + 13, cy + 13 * s_), fill=TEXTO, width=7)

import sys
NOME = sys.argv[1] if len(sys.argv) > 1 else None
if NOME is None:
    for n in ROTEIROS:
        subprocess.run([sys.executable, "-I", __file__, n], check=True)
    raise SystemExit
R = ROTEIROS[NOME]

bg = fundo()
por(bg, 0, TOTAL, 0.01)

# A) gancho
tipo, tit, extra = R["a"]
titulo(tit, *A)
ft = f(REG, 46)
if tipo == "chat":
    por(cartao((90, 760, 990, 1330)), A[0] + 0.3, A[1], 0.25)
    cab = vazio(); d = ImageDraw.Draw(cab)
    d.ellipse((130, 800, 186, 856), fill=(52, 56, 62)); d.text((143, 813), "IA", font=f(NEG, 26), fill=ACENTO)
    d.text((206, 812), "Assistente de IA", font=f(NEG, 34), fill=SUAVE)
    por(cab, A[0] + 0.3, A[1], 0.25)
    for i in range(1, len(extra) + 1):  # digitando letra por letra
        por(balao(extra[:i], 920, True, ft), 0.7 + i * 0.045, 0.7 + (i + 1) * 0.045 if i < len(extra) else A[1], 0.01)
    for k in range(3):
        por(balao("Procurando lugares" + "." * (k + 1), 1100, False, ft), 1.9 + k * 0.35, 1.9 + (k + 1) * 0.35 if k < 2 else A[1], 0.05)
elif tipo == "dms":
    por(cartao((90, 700, 990, 1420)), A[0] + 0.3, A[1], 0.25)
    cab = vazio(); d = ImageDraw.Draw(cab); d.text((140, 745), "mensagens · 27 não lidas", font=f(MONO, 34), fill=SUAVE)
    por(cab, A[0] + 0.3, A[1], 0.25)
    for i, t in enumerate(extra):
        por(balao(t, 830 + i * 145, False, ft), 1.0 + i * 0.5, A[1], 0.12, clique=True)
else:  # toque: botão, dedo tocando, mensagem pronta
    por(cartao((90, 720, 990, 1380)), A[0] + 0.3, A[1], 0.25)
    im = vazio(); d = ImageDraw.Draw(im); d.rounded_rectangle((170, 800, 910, 940), 70, fill=ACENTO)
    t = "Chamar no WhatsApp"; ftb = f(NEG, 58); d.text(((W - MED.textlength(t, font=ftb)) / 2, 836), t, font=ftb, fill=FUNDO)
    por(im, A[0] + 0.5, A[1], 0.2)
    for r, t0 in [(40, 1.3), (70, 1.42), (100, 1.54)]:
        im = vazio(); ImageDraw.Draw(im).ellipse((640 - r, 870 - r, 640 + r, 870 + r), outline=(255, 255, 255, 200), width=6)
        por(im, t0, t0 + 0.14, 0.01)
    cliques.append(1.3)
    im = vazio(); ImageDraw.Draw(im).text((140, 1010), "mensagem já escrita:", font=f(MONO, 34), fill=SUAVE)
    por(im, 1.7, A[1], 0.2)
    ftm = f(REG, 44)
    for i in range(1, len(extra) + 1):
        por(balao(extra[:i], 1080, True, ftm), 1.8 + i * 0.03, 1.8 + (i + 1) * 0.03 if i < len(extra) else A[1], 0.01)

# B) cartão com a lista
tit, rotulo_b, marca, itens = R["b"]
titulo(tit, *B)
por(cartao((90, 640, 990, 1420)), B[0] + 0.2, B[1], 0.25)
im = vazio(); ImageDraw.Draw(im).text((150, 690), rotulo_b, font=f(MONO, 36), fill=SUAVE)
por(im, B[0] + 0.2, B[1], 0.25)
for i, t in enumerate(itens):
    im = vazio(); d = ImageDraw.Draw(im); y = 820 + i * 190
    (check if marca == "ok" else xis)(d, 190, y + 32)
    d.text((260, y), t, font=f(NEG, 58), fill=TEXTO if marca == "ok" else SUAVE)
    por(im, B[0] + 0.7 + i * 0.5, B[1], 0.15, clique=True)

# C, D) sites no celular
moldura = celular(bg)
videos = []
for (ini, fim), (pasta, tit, url, tags) in zip([C, D], R["sites"]):
    videos.append((CEL / pasta, ini, fim))
    camadas.append(("__video__", ini, fim, 0))
    por(moldura, ini, fim, 0.01)
    titulo(tit, ini, fim)
    por(rodape(url), ini + 0.3, fim, 0.3)
    for j, (t, lado, y) in enumerate(tags):
        por(etiqueta(t, 70 if lado == "esq" else W - 70, y, lado), ini + 1.0 + j * 0.9, fim, 0.15, clique=True)

# E) chamada final
titulo(R["fim"], E[0], E[1], y=330 if len(R["fim"]) == 3 else 420, tam=110)
im = vazio(); d = ImageDraw.Draw(im); ft = f(MONO, 60); t = ">_ wandercodes"
d.text(((W - MED.textlength(t, font=ft)) / 2, 840), t, font=ft, fill=ACENTO)
por(im, E[0] + 0.9, TOTAL, 0.3)
im = vazio(); d = ImageDraw.Draw(im); d.rounded_rectangle((110, 1010, W - 110, 1170), 80, fill=ACENTO)
ft = f(NEG, 66); t = "Chame no WhatsApp"; d.text(((W - MED.textlength(t, font=ft)) / 2, 1052), t, font=ft, fill=FUNDO)
por(im, E[0] + 1.3, TOTAL, 0.2, clique=True)
im = vazio(); d = ImageDraw.Draw(im)
for t, ft, y, cor in [("(81) 99490-8227", f(NEG, 70), 1250, TEXTO), ("sites para negócios do Recife", f(REG, 44), 1370, SUAVE),
                      ("wandercodes.duckdns.org", f(MONO, 42), 1450, SUAVE)]:
    d.text(((W - MED.textlength(t, font=ft)) / 2, y), t, font=ft, fill=cor)
por(im, E[0] + 1.7, TOTAL, 0.3)

# ---------- efeitos sonoros (whoosh nas trocas, clique nos destaques)
def sfx(caminho):
    sr = 44100; n = int(TOTAL * sr); buf = [0.0] * n; rnd = random.Random(7)
    for t0 in whooshes:
        dur = 0.45; m = int(dur * sr); s0 = int(max(0, t0 - 0.12) * sr); lp = 0.0
        for i in range(m):
            p = i / m; corte = 0.02 + 0.25 * math.sin(math.pi * p)  # filtro abre e fecha
            lp += corte * (rnd.uniform(-1, 1) - lp)
            if s0 + i < n: buf[s0 + i] += 0.5 * lp * math.sin(math.pi * p) ** 2
    for t0 in cliques:
        s0 = int(t0 * sr)
        for i in range(int(0.06 * sr)):
            if s0 + i < n: buf[s0 + i] += 0.35 * math.sin(2 * math.pi * 1500 * i / sr) * math.exp(-i / (0.008 * sr))
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in buf))

# ---------- montagem: cada quadro é desenhado aqui e vai direto pro ffmpeg
pasta = pathlib.Path(tempfile.mkdtemp())
pecas = []  # (recorte, posição, ini, fim, fade) ou vídeo
iv = 0
for img, ini, fim, fade in camadas:
    if img == "__video__":
        src, vi, vf = videos[iv]; iv += 1; pecas.append(("v", src, ini, fim)); continue
    caixa = img.getbbox()
    if caixa: pecas.append(("i", img.crop(caixa), caixa[:2], ini, fim, fade))
x0, y0, x1, y1 = TELA
sfx(pasta / "sfx.wav")
saida = RAIZ / "video" / f"anuncio-{NOME}.mp4"
ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
     "-r", str(FPS), "-i", "-", "-i", str(RAIZ / "video" / "musica" / "beneficio.mp3"), "-i", str(pasta / "sfx.wav"),
     "-filter_complex", f"[1:a]volume=0.55,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[mu];[2:a]aformat=channel_layouts=stereo[fx];"
     "[mu][fx]amix=inputs=2:normalize=0:duration=first[a]", "-map", "0:v", "-map", "[a]", "-t", f"{TOTAL}",
     "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
     "-movflags", "+faststart", str(saida)], stdin=subprocess.PIPE)
cache = {}
for n in range(round(TOTAL * FPS)):
    t = n / FPS; quadro = Image.new("RGBA", (W, H), FUNDO + (255,))
    for pc in pecas:
        if pc[0] == "v":
            _, src, ini, fim = pc
            if ini <= t < fim:
                q = src / f"q_{min(11 + int((t - ini) * FPS), 170):04d}.jpg"
                quadro.paste(Image.open(q).convert("RGB").resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
            continue
        _, im, pos, ini, fim, fade = pc
        if not (ini <= t <= fim): continue
        a = min(1.0, (t - ini) / max(fade, 0.01))
        if a < 1:
            im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        quadro.alpha_composite(im, pos)
    ff.stdin.write(quadro.convert("RGB").tobytes())
ff.stdin.close(); ff.wait()
if ff.returncode: raise SystemExit("ffmpeg falhou")
print(saida.name, f"{TOTAL}s", len(pecas), "peças")
