# Vídeos de anúncio 9:16 (tráfego pago) com os tours reais dos sites.
# Uso: python3 -I anuncios.py [problema|metodo]  -> video/anuncio-{problema,metodo}.mp4
# (o Benefício agora sai de video/beneficio_celular.py)
# Fontes do Mac; no Linux cai nas Liberation (mesmas medidas da Arial).
# FONTE=/pasta muda a pasta dos tours (aceita também toca.mp4, bacurau.mp4, niedja.mp4).
import os, pathlib, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTE = pathlib.Path(os.environ.get("FONTE", RAIZ / "fonte"))
OUT = RAIZ / "video"
W, H = 1080, 1920
FUNDO, TEXTO, SUAVE, ACENTO = (11, 12, 14), (243, 241, 236), (160, 162, 170), (200, 240, 49)
def achar(*ps):
    return next((p for p in ps if pathlib.Path(p).exists()), ps[-1])
LIB = "/usr/share/fonts/truetype/liberation/"
NEG = achar("/System/Library/Fonts/Supplemental/Arial Bold.ttf", LIB + "LiberationSans-Bold.ttf")
REG = achar("/System/Library/Fonts/Supplemental/Arial.ttf", LIB + "LiberationSans-Regular.ttf")
MONO = achar("/System/Library/Fonts/Menlo.ttc", LIB + "LiberationMono-Regular.ttf")
f = lambda p, s: ImageFont.truetype(p, s)

TOURS = {
    "toca": (FONTE / "toca-do-cuco-vitrine-16x9.mp4", "banda · Toca do Cuco", "tocadocuco.duckdns.org"),
    "bacurau": (FONTE / "casa-bacurau-vitrine-16x9.mp4", "espaço cultural · Casa Bacurau", "casabacurau.com.br"),
    "niedja": (FONTE / "dra-niedja-tour.mp4", "pediatra · Dra. Niedja", "draniedja.duckdns.org"),
}

ANUNCIOS = {
    "problema": {
        "gancho": ["Seu negócio só", "existe no", "*Instagram?*"],
        "corpo": "Agenda, endereço e contato\nperdidos entre posts e stories.",
        "clipes": [("toca", 3), ("bacurau", 2), ("niedja", 1)],
    },
    "metodo": {
        "gancho": ["Seu cliente", "chama você", "*com um toque?*"],
        "corpo": "Botão de WhatsApp com\nmensagem pronta, rápido no celular.",
        "clipes": [("niedja", 12), ("toca", 22), ("bacurau", 16)],
    },
}
def tour(chave):
    p = TOURS[chave][0]
    return p if p.exists() else FONTE / f"{chave}.mp4"

T_GANCHO, T_CLIPE, T_LISTA, T_CTA = 3.2, 2.8, 3.4, 4.0

def centro(d, y, txt, fonte, cor, esp=12):
    for linha in txt.split("\n"):
        w = d.textlength(linha, font=fonte)
        d.text(((W - w) / 2, y), linha, font=fonte, fill=cor)
        y += fonte.size + esp
    return y

def png(nome, img, pasta):
    p = pasta / f"{nome}.png"; img.save(p); return str(p)

def tela_gancho(linhas):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((80, 300), ">_ wandercodes", font=f(MONO, 40), fill=ACENTO)
    # fonte encolhe até a linha mais larga caber com 70 px de margem de cada lado
    tam = 118
    while tam > 60 and max(d.textlength(l.strip("*"), font=f(NEG, tam)) for l in linhas) > W - 140:
        tam -= 2
    ft = f(NEG, tam); passo = round(tam * 1.19); y = 760 + (140 - passo) * (len(linhas) - 1) / 2
    for l in linhas:
        cor = ACENTO if l.startswith("*") else TEXTO
        l = l.strip("*"); w = d.textlength(l, font=ft)
        d.text(((W - w) / 2, y), l, font=ft, fill=cor); y += passo
    return im

def tela_clipes(corpo):
    im = Image.new("RGBA", (W, H), FUNDO + (255,)); d = ImageDraw.Draw(im)
    d.text((70, 170), ">_ wandercodes", font=f(MONO, 38), fill=ACENTO)
    centro(d, 1340, corpo, f(NEG, 58), TEXTO, 16)
    centro(d, 1610, "sites reais, no ar", f(MONO, 34), SUAVE)
    # janela do navegador (o vídeo entra em 40,760 com 1000x562)
    d.rounded_rectangle((40, 700, 1040, 1322), 22, fill=(23, 25, 30), outline=(60, 62, 70), width=2)
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        d.ellipse((70 + i * 30, 721, 88 + i * 30, 739), fill=c)
    return im

def rotulo(texto, url):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ft = f(MONO, 26); w = d.textlength(url, font=ft)
    d.rounded_rectangle(((W - w) / 2 - 18, 714, (W + w) / 2 + 18, 748), 8, fill=FUNDO)
    d.text(((W - w) / 2, 717), url, font=ft, fill=SUAVE)
    ft = f(NEG, 50); w = d.textlength(texto, font=ft)
    d.rounded_rectangle(((W - w) / 2 - 30, 560, (W + w) / 2 + 30, 650), 45, fill=ACENTO)
    d.text(((W - w) / 2, 578), texto, font=ft, fill=FUNDO)
    return im

def tela_lista():
    im = Image.new("RGBA", (W, H), FUNDO + (255,)); d = ImageDraw.Draw(im)
    centro(d, 470, "Um site simples\nresolve o básico", f(NEG, 92), TEXTO, 16)
    itens = ["onde você está e\nquando atende", "WhatsApp com\nmensagem pronta", "seu trabalho num\nendereço seu"]
    y = 860
    for t in itens:
        d.ellipse((140, y + 18, 176, y + 54), fill=ACENTO)
        yy = y
        for l in t.split("\n"):
            d.text((220, yy), l, font=f(NEG, 64), fill=TEXTO); yy += 78
        y += 250
    return im

def tela_cta():
    im = Image.new("RGBA", (W, H), FUNDO + (255,)); d = ImageDraw.Draw(im)
    centro(d, 420, ">_ wandercodes", f(MONO, 64), ACENTO)
    ft = f(NEG, 84)
    centro(d, 620, "Sites que dão vontade", ft, TEXTO)
    l1, l2 = "de ", "entrar."; w1 = d.textlength(l1, font=ft); w = w1 + d.textlength(l2, font=ft)
    d.text(((W - w) / 2, 716), l1, font=ft, fill=TEXTO); d.text(((W - w) / 2 + w1, 716), l2, font=ft, fill=ACENTO)
    centro(d, 860, "Recife", f(REG, 52), SUAVE)
    d.rounded_rectangle((110, 1060, W - 110, 1220), 80, fill=ACENTO)
    centro(d, 1100, "Chame no WhatsApp", f(NEG, 66), FUNDO)
    centro(d, 1290, "(81) 99490-8227", f(NEG, 70), TEXTO)
    centro(d, 1440, "wandercodes.duckdns.org", f(MONO, 44), SUAVE)
    return im

def fundo_gancho(src, ini, pasta):
    # quadro do site, borrado e escurecido, atrás do gancho
    q = pasta / "q.png"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(ini), "-i", str(src), "-frames:v", "1", str(q)], check=True)
    im = Image.open(q).convert("RGB"); s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)))
    x = (im.width - W) // 2; im = im.crop((x, 0, x + W, H)).filter(ImageFilter.GaussianBlur(28))
    im = Image.blend(im, Image.new("RGB", (W, H), FUNDO), 0.72)
    return png("fundo", im, pasta)

def montar(nome, a):
    pasta = pathlib.Path(tempfile.mkdtemp())
    total = T_GANCHO + 3 * T_CLIPE + T_LISTA + T_CTA
    t1 = T_GANCHO; t2 = t1 + 3 * T_CLIPE; t3 = t2 + T_LISTA
    ent = ["-f", "lavfi", "-i", f"color=c=0x0b0c0e:s={W}x{H}:r=30:d={total}"]
    fil, ultimo, k = [], "[0:v]", 1
    def junta(rotulo_in, ini, fim, pos="0:0"):
        nonlocal ultimo
        saida = f"[v{len(fil)}]"
        fil.append(f"{ultimo}{rotulo_in}overlay={pos}:enable='between(t,{ini:.2f},{fim:.2f})'{saida}"); ultimo = saida
    def imagem(caminho, ini, fim, fade=0.35):
        nonlocal k
        ent.extend(["-loop", "1", "-t", f"{total}", "-i", caminho])
        fil.append(f"[{k}:v]format=rgba,fade=t=in:st={ini:.2f}:d={fade}:alpha=1[i{k}]")
        lab = f"[i{k}]"; k += 1; junta(lab, ini, fim)
    src0 = tour(a["clipes"][0][0])
    imagem(fundo_gancho(src0, a["clipes"][0][1], pasta), 0, t1, 0.01)
    imagem(png("gancho", tela_gancho(a["gancho"]), pasta), 0, t1, 0.5)
    imagem(png("clipes", tela_clipes(a["corpo"]), pasta), t1, t2, 0.3)
    for i, (chave, ini) in enumerate(a["clipes"]):
        _, texto, url = TOURS[chave]; src = tour(chave); ti = t1 + i * T_CLIPE
        ent.extend(["-ss", str(ini), "-t", f"{T_CLIPE}", "-i", str(src)])
        fil.append(f"[{k}:v]scale=1000:562,setpts=PTS-STARTPTS+{ti:.2f}/TB[c{k}]")
        lab = f"[c{k}]"; k += 1; junta(lab, ti, ti + T_CLIPE, "40:760")
        imagem(png(f"rot{i}", rotulo(texto, url), pasta), ti, ti + T_CLIPE, 0.2)
    imagem(png("lista", tela_lista(), pasta), t2, t3, 0.3)
    imagem(png("cta", tela_cta(), pasta), t3, total, 0.3)
    saida = OUT / f"anuncio-{nome}.mp4"
    cmd = ["ffmpeg", "-loglevel", "error", "-y", *ent, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", ";".join(fil) + f";{ultimo}format=yuv420p[out]",
           "-map", "[out]", "-map", f"{k}:a", "-t", f"{total}", "-r", "30",
           "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(saida)]
    subprocess.run(cmd, check=True)
    print(saida.name, f"{total:.1f}s")

for nome, a in ANUNCIOS.items():
    if len(sys.argv) < 2 or nome in sys.argv[1:]:
        montar(nome, a)
