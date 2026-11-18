"""Medições finais do estudo do Zaykov: tempo de inferência em CPU e Grad-CAM lado a lado.

Rode na raiz do repositório:  python medir_final.py
Usa os modelos do fold 1 de cada experimento e as imagens de teste do fold 1.
Grava em results/final/:
  - tempo_cpu.csv           tempo por imagem (lote 1, CPU), parâmetros e tamanho do arquivo
  - gradcam_comparacao.png  original + Grad-CAM de cada modelo, nas mesmas imagens
"""
import glob
import os
import time

import tensorflow as tf

tf.config.set_visible_devices([], "GPU")  # mede na CPU, como num computador sem placa de vídeo

import keras
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from models import grad_cam_lib

FOLD = 1
TESTE = f"BD/CPD1_Cr_Rs_400/Test/k{FOLD}"
SAIDA = "results/final"
N_TEMPO = 100          # imagens usadas para medir o tempo
AQUECIMENTO = 10       # previsões descartadas antes de medir

# (rótulo, pasta do experimento, nome do modelo, camada do Grad-CAM ou None)
MODELOS = [
    ("DenseNet201", "densenet_dft", "DenseNet201", "relu"),
    ("CNN Zaykov (receita da tese)", "zaykov_rgb", "ZaykovCNN", None),
    ("CNN Zaykov (receita do autor)", "zaykov_receita", "ZaykovCNN_receita", "relu_256"),
    ("CNN Zaykov (cinza)", "zaykov_cinza", "ZaykovCNN_cinza", "relu_256"),
]
CLASSES_GRADCAM = ["ebenus", "pinus", "asphodelus", "olea", "myrtus", "sinapis"]

os.makedirs(SAIDA, exist_ok=True)
classes = sorted(d for d in os.listdir(TESTE) if os.path.isdir(os.path.join(TESTE, d)))


def carregar(caminho):
    img = keras.utils.load_img(caminho, target_size=(224, 224))
    return np.asarray(img, dtype="float32") / 255.0   # mesmo pré-processamento dos geradores da tese


arquivos = sorted(glob.glob(f"{TESTE}/*/*.png"))[:N_TEMPO]
imagens = [carregar(a)[None] for a in arquivos]

modelos, linhas = {}, []
for rotulo, exp, nome, camada in MODELOS:
    achados = glob.glob(f"results/{exp}/0_{nome}/*_{FOLD}.keras")
    if not achados:
        print(f"[faltando] {rotulo}: nenhum modelo em results/{exp}/0_{nome}/")
        continue
    caminho = achados[0]
    modelo = keras.models.load_model(caminho)
    modelos[rotulo] = (modelo, camada)

    for x in imagens[:AQUECIMENTO]:
        modelo(x, training=False)
    tempos = []
    for x in imagens:
        t0 = time.perf_counter()
        modelo(x, training=False)
        tempos.append((time.perf_counter() - t0) * 1000)
    linhas.append({
        "modelo": rotulo,
        "parametros": modelo.count_params(),
        "arquivo_MB": round(os.path.getsize(caminho) / 1e6, 1),
        "ms_por_imagem_mediana": round(float(np.median(tempos)), 2),
        "ms_por_imagem_p90": round(float(np.percentile(tempos, 90)), 2),
    })
    print(f"[ok] {rotulo}: {linhas[-1]['ms_por_imagem_mediana']} ms por imagem")

tabela = pd.DataFrame(linhas)
if len(tabela):
    base = tabela.loc[tabela.modelo == "DenseNet201", "ms_por_imagem_mediana"]
    if len(base):
        tabela["vezes_mais_rapido_que_DenseNet"] = (base.iloc[0] / tabela.ms_por_imagem_mediana).round(1)
    tabela.to_csv(f"{SAIDA}/tempo_cpu.csv", index=False)
    print("\n", tabela.to_string(index=False))

# Grad-CAM: mesmas imagens para todos os modelos que têm camada definida
com_cam = [(r, m, c) for r, (m, c) in modelos.items() if c]
escolhidas = [c for c in CLASSES_GRADCAM if c in classes] or classes[:6]
if com_cam:
    fig, eixos = plt.subplots(len(escolhidas), 1 + len(com_cam),
                              figsize=(3 * (1 + len(com_cam)), 3 * len(escolhidas)), squeeze=False)
    for i, classe in enumerate(escolhidas):
        caminho = sorted(glob.glob(f"{TESTE}/{classe}/*.png"))[0]
        img = carregar(caminho)
        eixos[i][0].imshow(img)
        eixos[i][0].set_title(f"original: {classe}", fontsize=9)
        for j, (rotulo, modelo, camada) in enumerate(com_cam, start=1):
            prob = modelo(img[None], training=False).numpy()[0]
            prevista = classes[int(np.argmax(prob))]
            mapa = grad_cam_lib.make_gradcam_heatmap(img, modelo, camada)
            mapa = tf.image.resize(np.asarray(mapa)[..., None], (224, 224)).numpy()[..., 0]
            eixos[i][j].imshow(img)
            eixos[i][j].imshow(mapa, cmap="jet", alpha=0.4)
            cor = "green" if prevista == classe else "red"
            eixos[i][j].set_title(f"{rotulo}\n{prevista} ({prob.max():.0%})", fontsize=8, color=cor)
    for linha in eixos:
        for e in linha:
            e.axis("off")
    plt.tight_layout()
    plt.savefig(f"{SAIDA}/gradcam_comparacao.png", dpi=120)
    print(f"\n[ok] {SAIDA}/gradcam_comparacao.png")