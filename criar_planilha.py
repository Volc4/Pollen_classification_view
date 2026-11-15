"""Cria uma planilha de configuração de treino no formato da tese.

Uso, na raiz do repositório (exemplos):
    python criar_planilha.py densenet_k1 --modelo DenseNet201 --lr 0.0001 --batch 8 --epocas 500 --folds 1
    python criar_planilha.py zaykov_rgb --modelo ZaykovCNN --lr 0.0005 --batch 32 --epocas 500 --folds 10

Cria results/<nome>/config_<nome>.xlsx. Para treinar:
    python phase2/FT_DFT_K10_xlsx.py results/<nome>/config_<nome>.xlsx
"""
import argparse
import os

import pandas as pd

p = argparse.ArgumentParser(description="Cria a planilha de configuração de um treino.")
p.add_argument("nome", help="nome do experimento (vira a pasta em results/)")
p.add_argument("--modelo", required=True, help="DenseNet201, ZaykovCNN, MobileNet...")
p.add_argument("--lr", type=float, required=True, help="taxa de aprendizado")
p.add_argument("--batch", type=int, required=True, help="tamanho do lote")
p.add_argument("--epocas", type=int, default=500, help="máximo de épocas (o early stopping para antes)")
p.add_argument("--folds", type=int, default=10, help="quantos folds rodar")
p.add_argument("--fold-inicial", type=int, default=1, help="primeiro fold (para retomar)")
p.add_argument("--dados", default="BD/CPD1_Cr_Rs_400", help="pasta com Train/ e Test/")
p.add_argument("--obs", default="", help="observação livre")
a = p.parse_args()

pasta = os.path.join("results", a.nome)
planilha = os.path.join(pasta, f"config_{a.nome}.xlsx")
if os.path.exists(planilha):
    raise SystemExit(f"Já existe: {planilha}. Escolha outro nome ou apague a pasta {pasta}.")
os.makedirs(pasta, exist_ok=True)

params = pd.DataFrame([
    ["params", "values"],
    ["working_directory", "."],
    ["observations", a.obs or f"{a.modelo}, folds {a.fold_inicial} a {a.fold_inicial + a.folds - 1}"],
    ["epochs", a.epocas],
    ["alpha", 0.00001],
    ["learning_rate", a.lr],
    ["img_size", 224],
    ["split_valid", 0.2],
    ["last_test_index", 0],
    ["k_fold_number", a.fold_inicial],
    ["num_k_folds", a.folds],
    ["num_tests", 1],
])
teste = pd.DataFrame([{
    "id_test": 0, "model": a.modelo, "last_activation": "softmax", "activation": "relu",
    "batch_size": a.batch, "freeze": 0, "optimizer": "Adam", "path_data": a.dados,
    "Type": "Cropped Pollen Grains",
}])
with pd.ExcelWriter(planilha) as w:
    params.to_excel(w, sheet_name="Params", header=False, index=False)
    teste.to_excel(w, sheet_name="Test", index=False)

print(f"[ok] {planilha}")
print(f"Para treinar:  python phase2/FT_DFT_K10_xlsx.py {planilha}")