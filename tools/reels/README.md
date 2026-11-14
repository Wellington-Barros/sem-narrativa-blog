# Ferramentas de reels e capas (não fazem parte do site)

Esta pasta guarda os arquivos usados para gerar os reels e as capas do blog. Ela fica fora de src, então o Astro não a publica no site.

## Reels
- reel11.html: reel das 106 urnas (com pausa de cerca de 3 s por cena).
- reel12.html: reel da CBS de 11,3%. Use este como modelo para reels novos.
- reel13.html: reel do fim da escala 6x1 (Emenda 141).
- reel14.html: linha do tempo de Flávio Bolsonaro (passaporte, Argentina, Miami e Fantástico).
- reel15.html: primeiro reel com narração (crise do Ueno Bank no Paraguai). Os tempos das cenas e das legendas vêm de reel15-data.json, gerado a partir dos áudios.
- reel16.html: Lei Rouanet, como funciona, números, críticas e defesas (vídeo mudo, cenas com durações em DURS).
- reel17.html: PEC da Segurança, estilo de alto engajamento (gancho nos 2 primeiros segundos, placar animado, cards, pergunta final para comentários). Áudio original sintetizado por audio17.py.
- reel18.html: checagem das 6 mudanças da reforma tributária em 2027, mesmo estilo do reel17. Áudio por audio18.py.
- reel19.html: liminar de Flávio Dino sobre o fim da 6x1, com a semana de trabalho animada (folgas, calendário, relógio de 8h24, cabo de guerra e plenário). Áudio por audio19.py.
- render11.py a render14.py, render16.py, render17.py, render18.py e render19.py: renderizam o HTML correspondente (vídeo mudo).
- render15.py: renderiza o reel15 com a trilha de áudio: python3 render15.py saida.mp4 /caminho/audio.wav (imagens de teste: python3 render15.py PREFIXO 6.5 14.5). Os áudios de voz não ficam no repositório.
- voz/: scripts usados no reel15 (transcrição com Whisper turbo em ONNX, corte de pausas, tempos das legendas e efeitos sonoros). São referência: os caminhos estão fixos no início de cada arquivo e precisam ser ajustados.

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
- mkcapa_urnas.py, mkcapa_cbs.py, mkcapa_6x1.py, mkcapa_espectro.py, mkcapa_flavio.py, mkcapa_paraguai.py e mkcapa_rouanet.py: capas 1200x600 com PIL e fonte Inter (/usr/share/fonts/opentype/inter/). Os caminhos de saída e de referência estão no início de cada script e precisam ser ajustados ao ambiente.
