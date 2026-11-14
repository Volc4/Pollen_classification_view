"""Aplica as correções necessárias para rodar o código da tese no Windows sem GPU NVIDIA.

1. import do WhatsApp opcional;
2. monitor de memória sem NVIDIA;
3. cópia das imagens para os folds com caminhos do Windows;
4. ordem fixa dos arquivos antes da divisão em folds (mesmos folds em qualquer sistema);
5. nomes únicos para as imagens aumentadas (no Windows o relógio é grosso e os nomes se repetiam).

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
    (
        "models/split_BD_Views_k.py",
        "        folder = file_path.split('/')[-2]\n        filename = file_path.split('/')[-1]",
        "        file_path = os.path.normpath(file_path)\n"
        "        folder = os.path.basename(os.path.dirname(file_path))\n"
        "        filename = os.path.basename(file_path)",
    ),
    (
        "models/split_BD_Views_k.py",
        "        filenames = [f for f in os.listdir(category_path) if os.path.isfile(os.path.join(category_path, f)) and not f.startswith(\".\")]",
        "        filenames = [f for f in os.listdir(category_path) if os.path.isfile(os.path.join(category_path, f)) and not f.startswith(\".\")]\n"
        "        filenames.sort()  # ordem fixa: mesmos folds no Windows e no Linux",
    ),
    (
        "models/augmentation_BD_k.py",
        "    aug_images = []\n"
        "    for _ in range(factor):\n"
        "        augmented_batch = aug(images=images)\n"
        "        for img in augmented_batch:\n"
        "            filename = os.path.join(save_dir, f\"aug_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.{img_type}\")",
        "    aug_images = []\n"
        "    contador = len(os.listdir(save_dir))  # nomes únicos mesmo com relógio de baixa resolução\n"
        "    for _ in range(factor):\n"
        "        augmented_batch = aug(images=images)\n"
        "        for img in augmented_batch:\n"
        "            contador += 1\n"
        "            filename = os.path.join(save_dir, f\"aug_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{contador:05d}.{img_type}\")",
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