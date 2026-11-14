"""Prepara o passo 4: a CNN do Zaykov dentro do pipeline da tese.

Rode na raiz do repositório:  python preparar_passo4.py
Faz três coisas (pode rodar de novo sem problema):
1. cria models/models_zaykov.py com a CNN;
2. liga a CNN à hyper_model do script de treino (nome do modelo: ZaykovCNN);
3. cria a planilha results/zaykov_teste/config_teste_zaykov.xlsx (fold 1, 5 épocas).
"""
import os

import pandas as pd

MODELO = '''"""CNN leve de Zaykov (ICAI 2025), adaptada ao pipeline da tese.

Mesma arquitetura da Tabela I do artigo: 7 blocos Conv-BN-ReLU-MaxPool (8 a 512
filtros), Dense de 2048 com Dropout de 0,35 e saída softmax. Diferenças em relação
ao artigo: entrada RGB (como os geradores da tese), número de classes variável e
treino com a receita da tese (perda categórica, early stopping da tese).
"""
import keras
from keras import layers, models


def zaykov_cnn(num_classes=20, canais=3, img_size=224):
    m = models.Sequential(name="ZaykovCNN")
    m.add(keras.Input(shape=(img_size, img_size, canais)))
    for f in [8, 16, 32, 64, 128, 256, 512]:
        m.add(layers.Conv2D(f, 3, padding="same", name=f"conv_{f}"))
        m.add(layers.BatchNormalization(name=f"bn_{f}"))
        m.add(layers.Activation("relu", name=f"relu_{f}"))
        m.add(layers.MaxPooling2D(2, name=f"pool_{f}"))
    m.add(layers.Flatten(name="flatten"))
    m.add(layers.Dense(2048, activation="relu", name="dense_2048"))
    m.add(layers.Dropout(0.35, name="dropout"))
    m.add(layers.Dense(num_classes, activation="softmax", name="predictions"))
    return m


def build_zaykov_model(config_model):
    """Cria e compila a CNN com o otimizador e a taxa de aprendizado da planilha."""
    model = zaykov_cnn(num_classes=int(config_model["num_classes"]))
    otimizadores = {"Adam": keras.optimizers.Adam, "RMSprop": keras.optimizers.RMSprop,
                    "Adagrad": keras.optimizers.Adagrad, "SGD": keras.optimizers.SGD}
    nome = config_model["optimizer"]
    if nome not in otimizadores:
        raise ValueError(f"Unsupported optimizer: {nome}")
    opt = otimizadores[nome](learning_rate=float(config_model["learning_rate"]))
    model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
    model.summary()
    return model
'''

# 1. arquivo do modelo
with open("models/models_zaykov.py", "w", encoding="utf-8") as f:
    f.write(MODELO)
print("[ok] models/models_zaykov.py")

# 2. desvio na hyper_model
caminho = "phase2/FT_DFT_K10_xlsx.py"
antigo = "    # Initialize the specified pre-trained model\n    model = eval(config_model['model'])"
novo = ("    # CNN leve do Zaykov (treinada do zero), fora do caminho dos modelos pré-treinados\n"
        "    if config_model['model'] == 'ZaykovCNN':\n"
        "        from models.models_zaykov import build_zaykov_model\n"
        "        return build_zaykov_model(config_model)\n\n"
        + antigo)
with open(caminho, encoding="utf-8") as f:
    texto = f.read()
if "build_zaykov_model" in texto:
    print(f"[já aplicada] {caminho}")
elif texto.count(antigo) == 1:
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        f.write(texto.replace(antigo, novo))
    print(f"[ok] {caminho}")
else:
    print(f"[ERRO] trecho não encontrado em {caminho}; me mande este aviso")

# 3. planilha do teste rápido (mesmo formato da planilha da fase 3 da tese)
pasta = "results/zaykov_teste"
planilha = f"{pasta}/config_teste_zaykov.xlsx"
os.makedirs(pasta, exist_ok=True)
if os.path.exists(planilha):
    print(f"[já existe] {planilha} (apague a pasta {pasta} para recriar)")
else:
    params = pd.DataFrame([
        ["params", "values"],
        ["working_directory", "."],
        ["observations", "Passo 4: teste rápido da CNN do Zaykov no fold 1"],
        ["epochs", 5],
        ["alpha", 0.00001],
        ["learning_rate", 0.0005],
        ["img_size", 224],
        ["split_valid", 0.2],
        ["last_test_index", 0],
        ["k_fold_number", 1],
        ["num_k_folds", 1],
        ["num_tests", 1],
    ])
    testes = pd.DataFrame([{
        "id_test": 0, "model": "ZaykovCNN", "last_activation": "softmax",
        "activation": "relu", "batch_size": 32, "freeze": 0, "optimizer": "Adam",
        "path_data": "BD/CPD1_Cr_Rs_400", "Type": "Cropped Pollen Grains",
    }])
    with pd.ExcelWriter(planilha) as w:
        params.to_excel(w, sheet_name="Params", header=False, index=False)
        testes.to_excel(w, sheet_name="Test", index=False)
    print(f"[ok] {planilha}")