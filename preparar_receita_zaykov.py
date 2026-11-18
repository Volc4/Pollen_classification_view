"""Acrescenta o modelo "ZaykovCNN_receita": a mesma CNN, treinada com a receita do Zaykov.

Receita (igual ao notebook CNN_MonteCarlo_Validation.ipynb do autor):
- taxa de aprendizado constante nas 30 primeiras épocas e, depois, multiplicada por 0,98 a cada época;
- early stopping na perda de validação com paciência 15, restaurando os melhores pesos.
O modelo "ZaykovCNN" continua com a receita da tese (paciência 10, taxa fixa).

Rode na raiz do repositório:  python preparar_receita_zaykov.py
Pode rodar mais de uma vez: correções já aplicadas são ignoradas.
"""

CALLBACKS = '''

def callbacks_zaykov():
    """Callbacks da receita original do Zaykov."""
    from keras.callbacks import EarlyStopping, LearningRateScheduler

    def agenda(epoch, lr):
        return lr if epoch < 30 else lr * 0.98

    return [
        EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True, mode="min", verbose=1),
        LearningRateScheduler(agenda, verbose=0),
    ]
'''

CORRECOES = [
    ("models/models_zaykov.py",
     'def zaykov_cnn(num_classes=20, canais=3, img_size=224):\n    m = models.Sequential(name="ZaykovCNN")',
     'def zaykov_cnn(num_classes=20, canais=3, img_size=224, nome="ZaykovCNN"):\n    m = models.Sequential(name=nome)'),
    ("models/models_zaykov.py",
     '    model = zaykov_cnn(num_classes=int(config_model["num_classes"]))',
     '    model = zaykov_cnn(num_classes=int(config_model["num_classes"]), nome=config_model["model"])'),
    ("phase2/FT_DFT_K10_xlsx.py",
     "    if config_model['model'] == 'ZaykovCNN':",
     "    if config_model['model'] in ('ZaykovCNN', 'ZaykovCNN_receita'):"),
    ("models/models_train.py",
     "        callbacks_list = create_callbacks()",
     "        callbacks_list = create_callbacks()\n"
     "        if model_fine.name == 'ZaykovCNN_receita':  # receita original do Zaykov\n"
     "            from models.models_zaykov import callbacks_zaykov\n"
     "            callbacks_list = callbacks_zaykov()"),
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

with open("models/models_zaykov.py", encoding="utf-8") as f:
    texto = f.read()
if "def callbacks_zaykov" in texto:
    print("[já aplicada] models/models_zaykov.py (callbacks)")
else:
    with open("models/models_zaykov.py", "a", encoding="utf-8", newline="") as f:
        f.write(CALLBACKS)
    print("[ok] models/models_zaykov.py (callbacks)")