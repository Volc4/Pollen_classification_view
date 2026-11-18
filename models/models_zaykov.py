"""CNN leve de Zaykov (ICAI 2025), adaptada ao pipeline da tese.

Mesma arquitetura da Tabela I do artigo: 7 blocos Conv-BN-ReLU-MaxPool (8 a 512
filtros), Dense de 2048 com Dropout de 0,35 e saída softmax. Diferenças em relação
ao artigo: entrada RGB (como os geradores da tese), número de classes variável e
treino com a receita da tese (perda categórica, early stopping da tese).
"""
import keras
from keras import layers, models


def zaykov_cnn(num_classes=20, canais=3, img_size=224, nome="ZaykovCNN"):
    m = models.Sequential(name=nome)
    m.add(keras.Input(shape=(img_size, img_size, canais)))
    if nome == "ZaykovCNN_cinza":
        # RGB -> cinza dentro do modelo (mesmos pesos de tf.image.rgb_to_grayscale)
        import numpy as np
        cinza = layers.Conv2D(1, 1, use_bias=False, trainable=False, name="rgb_para_cinza")
        m.add(cinza)
        cinza.set_weights([np.array([0.2989, 0.5870, 0.1140], dtype="float32").reshape(1, 1, 3, 1)])
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
    model = zaykov_cnn(num_classes=int(config_model["num_classes"]), nome=config_model["model"])
    otimizadores = {"Adam": keras.optimizers.Adam, "RMSprop": keras.optimizers.RMSprop,
                    "Adagrad": keras.optimizers.Adagrad, "SGD": keras.optimizers.SGD}
    nome = config_model["optimizer"]
    if nome not in otimizadores:
        raise ValueError(f"Unsupported optimizer: {nome}")
    opt = otimizadores[nome](learning_rate=float(config_model["learning_rate"]))
    model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
    model.summary()
    return model


def callbacks_zaykov():
    """Callbacks da receita original do Zaykov."""
    from keras.callbacks import EarlyStopping, LearningRateScheduler

    def agenda(epoch, lr):
        return lr if epoch < 30 else lr * 0.98

    return [
        EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True, mode="min", verbose=1),
        LearningRateScheduler(agenda, verbose=0),
    ]
