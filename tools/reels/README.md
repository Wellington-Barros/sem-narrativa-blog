# Ferramentas de reels e capas (não fazem parte do site)

Esta pasta guarda os arquivos usados para gerar os reels e as capas do blog. Ela fica fora de src, então o Astro não a publica no site.

## Reels
- reel11.html: reel das 106 urnas (com pausa de cerca de 3 s por cena).
- reel12.html: reel da CBS de 11,3%. Use este como modelo para reels novos.
- render11.py e render12.py: renderizam o HTML correspondente.

Render completo (de 4 a 10 minutos, rodar em segundo plano):
python3 render12.py /caminho/saida.mp4

Imagens de teste em tempos específicos (segundos):
python3 render12.py PREFIXO 6.5 14.5 22.5

Requisitos: Python com playwright (Chromium) e ffmpeg.

## Como fazer um reel novo
1. Copie reel12.html e troque o conteúdo das cenas (blocos div.scene).
2. Ajuste STARTS e ENDV e os tempos de cada cena. Deixe cerca de 3 s de pausa depois do último elemento de cada cena.
3. Gere imagens de teste, confira os números contra o artigo e só então renderize.
4. O vídeo tem 1080x1920, 30 fps, sem áudio (faixa muda).

## Capas
- mkcapa_urnas.py, mkcapa_cbs.py e mkcapa_6x1.py: capas 1200x600 com PIL e fonte Inter (/usr/share/fonts/opentype/inter/). Os caminhos de saída e de referência estão no início de cada script e precisam ser ajustados ao ambiente.
