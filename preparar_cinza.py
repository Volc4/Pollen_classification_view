"""Acrescenta o modelo "ZaykovCNN_cinza": a CNN do Zaykov em escala de cinza, com a receita do autor.

A conversão para cinza acontece dentro do próprio modelo, numa primeira camada fixa
(pesos 0,2989 / 0,5870 / 0,1140, os mesmos de tf.image.rgb_to_grayscale). Assim o
carregador de dados da tese não muda, e o modelo salvo já aceita imagens coloridas.

Rode na raiz do repositório, depois do preparar_receita_zaykov.py:
    python preparar_cinza.py
"""

CORRECOES = [
    ("phase2/FT_DFT_K10_xlsx.py",
     "    if config_model['model'] in ('ZaykovCNN', 'ZaykovCNN_receita'):",
     "    if config_model['model'] in ('ZaykovCNN', 'ZaykovCNN_receita', 'ZaykovCNN_cinza'):"),
    ("models/models_train.py",
     "        if model_fine.name == 'ZaykovCNN_receita':  # receita original do Zaykov",
     "        if model_fine.name in ('ZaykovCNN_receita', 'ZaykovCNN_cinza'):  # receita original do Zaykov"),
    ("models/models_zaykov.py",
     "    m.add(keras.Input(shape=(img_size, img_size, canais)))\n",
     "    m.add(keras.Input(shape=(img_size, img_size, canais)))\n"
     "    if nome == \"ZaykovCNN_cinza\":\n"
     "        # RGB -> cinza dentro do modelo (mesmos pesos de tf.image.rgb_to_grayscale)\n"
     "        import numpy as np\n"
     "        cinza = layers.Conv2D(1, 1, use_bias=False, trainable=False, name=\"rgb_para_cinza\")\n"
     "        m.add(cinza)\n"
     "        cinza.set_weights([np.array([0.2989, 0.5870, 0.1140], dtype=\"float32\").reshape(1, 1, 3, 1)])\n"),
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
        print(f"[ERRO] trecho não encontrado em {caminho}; rode antes o preparar_receita_zaykov.py ou me mande este aviso")