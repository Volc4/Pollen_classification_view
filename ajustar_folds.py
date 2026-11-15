"""Muda quais folds a próxima sessão de treino vai rodar, sem apagar resultados.

Uso, na raiz do repositório:
    python ajustar_folds.py results/densenet_dft/config_densenet_dft.xlsx --fold-inicial 3 --folds 2

Mostra também os folds que já têm resultado gravado na aba Table_Exp.
"""
import argparse

import openpyxl

p = argparse.ArgumentParser(description="Ajusta os folds da próxima sessão de treino.")
p.add_argument("planilha")
p.add_argument("--fold-inicial", type=int, help="primeiro fold da próxima sessão")
p.add_argument("--folds", type=int, help="quantos folds rodar na próxima sessão")
a = p.parse_args()

wb = openpyxl.load_workbook(a.planilha)
params = wb["Params"]

# folds já concluídos (cada fold só é gravado quando termina)
feitos = []
if "Table_Exp" in wb.sheetnames:
    aba = wb["Table_Exp"]
    cab = [c.value for c in aba[1]]
    if "k" in cab:
        col = cab.index("k")
        feitos = [linha[col] for linha in aba.iter_rows(min_row=2, values_only=True) if linha[col] is not None]
print("Folds com resultado gravado:", sorted(feitos) if feitos else "nenhum")
repetidos = sorted({k for k in feitos if feitos.count(k) > 1})
if repetidos:
    print("ATENÇÃO: folds gravados mais de uma vez:", repetidos)

if a.fold_inicial is None and a.folds is None:
    raise SystemExit("Nada alterado (use --fold-inicial e --folds para mudar a próxima sessão).")

for linha in params.iter_rows(min_row=1):
    nome = linha[0].value
    if nome == "k_fold_number" and a.fold_inicial is not None:
        linha[1].value = a.fold_inicial
    if nome == "num_k_folds" and a.folds is not None:
        linha[1].value = a.folds
wb.save(a.planilha)

ini = next(l[1].value for l in params.iter_rows() if l[0].value == "k_fold_number")
n = next(l[1].value for l in params.iter_rows() if l[0].value == "num_k_folds")
ja = sorted(set(range(ini, ini + n)) & set(feitos))
print(f"Próxima sessão: folds {ini} a {ini + n - 1}")
if ja:
    print(f"ATENÇÃO: os folds {ja} já têm resultado; rodá-los de novo cria linhas repetidas.")