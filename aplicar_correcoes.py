"""Aplica as duas correções necessárias para rodar a tese sem GPU NVIDIA.

Rode na raiz do repositório:  python aplicar_correcoes.py
Pode rodar mais de uma vez: se a correção já estiver aplicada, ele avisa e segue.
"""

CORRECOES = [
    (
        "phase2/FT_DFT_K10_xlsx.py",
        "from models import  utils, get_data, models_train, sound_test_finalizado, maneger_gpu, send_whatsApp_msn",
        "from models import  utils, get_data, models_train, sound_test_finalizado, maneger_gpu\n"
        "try:\n"
        "    from models import send_whatsApp_msn\n"
        "except Exception:\n"
        "    send_whatsApp_msn = None",
    ),
    (
        "models/maneger_gpu.py",
        "    nvidia_smi.nvmlInit()\n    handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)",
        "    try:\n"
        "        nvidia_smi.nvmlInit()\n"
        "    except Exception:\n"
        "        # Sem GPU NVIDIA (ex.: AMD com DirectML): devolve valores neutros\n"
        "        return 0.0, 1.0, 1.0\n"
        "    handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)",
    ),
]

for caminho, antigo, novo in CORRECOES:
    with open(caminho, encoding="utf-8") as f:
        texto = f.read()
    if novo in texto:
        print(f"[já aplicada] {caminho}")
    elif texto.count(antigo) == 1:
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            f.write(texto.replace(antigo, novo))
        print(f"[ok] {caminho}")
    else:
        print(f"[ERRO] trecho não encontrado em {caminho}; me mande este aviso")
