"""CNN leve de Zaykov (ICAI 2025), adaptada ao pipeline da tese.

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
