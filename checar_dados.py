"""Checagem do CPD1: imagens por classe, extensões, tamanhos e duplicatas exatas.

Uso, na raiz do repositório:
    python checar_dados.py "BD/Cropped Pollen Grains"
    python checar_dados.py "BD/CPD1_Cr_Rs"
"""
import hashlib
import os
import sys
from collections import Counter, defaultdict

from PIL import Image

# Contagens do README da tese (o próprio README diz que podem não ser as atuais)
README = {"asphodelus": 34, "calicotome": 298, "castanea": 218, "ceratonia": 100,
          "ebenus": 22, "erica": 181, "eucalyptus": 170, "ferula": 83, "myrtus": 786,
          "olea": 790, "origanum": 171, "oxalis": 139, "pinus": 29, "pistacia": 34,
          "salvia": 178, "satureja": 71, "sinapis": 197, "thymbra": 146,
          "urginea": 109, "vitis": 269}
EXT_IMG = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")

pasta = sys.argv[1] if len(sys.argv) > 1 else "BD/Cropped Pollen Grains"
if not os.path.isdir(pasta):
    sys.exit(f"Pasta não encontrada: {pasta}")

classes = sorted(d for d in os.listdir(pasta) if os.path.isdir(os.path.join(pasta, d)))
extensoes, tamanhos, por_hash = Counter(), Counter(), defaultdict(list)
total = 0

print(f"\nPasta: {pasta}\n")
print(f"{'classe':<26}{'imagens':>8}{'README':>8}{'dif':>6}")
for c in classes:
    arquivos = [f for f in os.listdir(os.path.join(pasta, c))
                if os.path.isfile(os.path.join(pasta, c, f))]
    imagens = [f for f in arquivos if f.lower().endswith(EXT_IMG)]
    for f in arquivos:
        extensoes[os.path.splitext(f)[1].lower() or "(sem extensão)"] += 1
    for f in imagens:
        caminho = os.path.join(pasta, c, f)
        with open(caminho, "rb") as arq:
            por_hash[hashlib.md5(arq.read()).hexdigest()].append(f"{c}/{f}")
        with Image.open(caminho) as im:
            tamanhos[im.size] += 1
    ref = README.get(c)
    dif = "" if ref is None else f"{len(imagens) - ref:+d}"
    print(f"{c:<26}{len(imagens):>8}{(ref if ref is not None else '-'):>8}{dif:>6}")
    total += len(imagens)

print(f"{'TOTAL':<26}{total:>8}{sum(README.values()):>8}")
print("(a tese fala em 4.034 imagens; o README lista 4.025)\n")

print("Extensões encontradas:", dict(extensoes))
if any(e != ".png" for e in extensoes):
    print("  ATENÇÃO: o resize_img_bd.py só processa .png; os outros tipos seriam ignorados.")

larguras = [w for (w, h) in tamanhos for _ in range(tamanhos[(w, h)])]
alturas = [h for (w, h) in tamanhos for _ in range(tamanhos[(w, h)])]
if larguras:
    print(f"Tamanhos: {len(tamanhos)} diferentes; largura {min(larguras)} a {max(larguras)}, "
          f"altura {min(alturas)} a {max(alturas)} px")

grupos = [v for v in por_hash.values() if len(v) > 1]
print(f"\nDuplicatas exatas (MD5): {len(grupos)} grupo(s), "
      f"{sum(len(g) for g in grupos)} arquivo(s)")
for g in grupos[:30]:
    entre = " <- CLASSES DIFERENTES" if len({x.split('/')[0] for x in g}) > 1 else ""
    print("  ", " = ".join(g), entre)
if len(grupos) > 30:
    print(f"   ... e mais {len(grupos) - 30} grupo(s)")