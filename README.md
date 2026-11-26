# wandercodes

Site da wandercodes: sites sob medida para bandas, espaços culturais, consultórios e negócios locais, feitos no Recife por Eduardo Wanderley.

No ar: https://wandercodes.duckdns.org

Projetos em destaque:
- [Toca do Cuco](https://tocadocuco.duckdns.org) · [tour](https://www.youtube.com/watch?v=PF5lrPWg60A)
- [Casa Bacurau](https://casabacurau.com.br) · [tour](https://www.youtube.com/watch?v=d-goyrjrlYI)
- [Dra. Niedja Wanderley](https://draniedja.duckdns.org) · [tour](https://www.youtube.com/watch?v=OtBZA78j4-E)

## Estrutura

- `site/index.html`, `site/estilo.css`, `site/app.js`: HTML, CSS e JavaScript puros, sem framework
- `site/config.js`: WhatsApp e e-mail do botão de contato
- `site/midia/`: vídeos dos tours (H.264, sem som) e imagens em WebP

## Publicar

```bash
rsync -a --delete site/ fleet-vps:Sites/wandercodes/site/
```
