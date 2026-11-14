"""Confere os folds gerados pelo split_aug_bd_k.py.

Uso, na raiz do repositório:
    python verificar_folds.py "BD/CPD1_Cr_Rs_400" "BD/CPD1_Cr_Rs"

Checa, para cada fold: imagens de treino e teste por classe, se alguma imagem
de teste também está no treino, se há imagens aumentadas no teste e, no fim,
se cada imagem original aparece no teste de exatamente um fold.
"""
import os
import sys
from collections import Counter

base = sys.argv[1] if len(sys.argv) > 1 else "BD/CPD1_Cr_Rs_400"
origem = sys.argv[2] if len(sys.argv) > 2 else "BD/CPD1_Cr_Rs"


def listar(pasta):
    """Devolve {classe: [arquivos]} de uma pasta com subpastas por classe."""
    return {c: sorted(os.listdir(os.path.join(pasta, c)))
            for c in sorted(os.listdir(pasta)) if os.path.isdir(os.path.join(pasta, c))}


sufixo = os.path.basename(os.path.normpath(base)).rsplit("_", 1)[-1]
meta = int(sufixo) if sufixo.isdigit() else None   # alvo do aumento (ex.: 400)
folds = sorted((d for d in os.listdir(os.path.join(base, "Test"))), key=lambda d: int(d[1:]))
vezes_no_teste = Counter()
problemas = 0

for k in folds:
    treino = listar(os.path.join(base, "Train", k))
    teste = listar(os.path.join(base, "Test", k))
    nomes_treino = {(c, f) for c, fs in treino.items() for f in fs}
    nomes_teste = {(c, f) for c, fs in teste.items() for f in fs}
    vazados = nomes_teste & nomes_treino
    aumentadas = [x for x in nomes_teste if x[1].lower().startswith("aug")]
    vezes_no_teste.update(nomes_teste)
    originais_treino = sum(1 for _, f in nomes_treino if not f.lower().startswith("aug"))
    print(f"{k:>4}: treino {len(nomes_treino):5d} ({originais_treino} originais), "
          f"teste {len(nomes_teste):4d} | teste também no treino: {len(vazados)} | "
          f"aumentadas no teste: {len(aumentadas)}")
    menor = min(treino, key=lambda c: len(treino[c]))
    maior = max(treino, key=lambda c: len(treino[c]))
    print(f"      treino por classe: menor {menor} ({len(treino[menor])}), "
          f"maior {maior} ({len(treino[maior])})")
    abaixo = [c for c, fs in treino.items() if meta and len(fs) < meta]
    if abaixo:
        print(f"      ATENÇÃO: classes com menos de {meta} imagens no treino: {abaixo}")
    problemas += len(vazados) + len(aumentadas) + len(abaixo)

originais = {(c, f) for c, fs in listar(origem).items() for f in fs}
fora = originais - set(vezes_no_teste)
repetidas = [x for x, n in vezes_no_teste.items() if n > 1]
print(f"\nImagens originais: {len(originais)}")
print(f"Originais que não caíram em nenhum teste: {len(fora)}")
print(f"Originais que caíram em mais de um teste: {len(repetidas)}")
problemas += len(fora) + len(repetidas)

print("\nRESULTADO:", "folds OK" if problemas == 0 else f"{problemas} problema(s); me mande esta saída")