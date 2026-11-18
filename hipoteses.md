\# Hipóteses registradas antes dos treinos da CNN do Zaykov



Data: 18/11/2026

Referência: DenseNet201 com DFT, 10 folds, no mesmo ambiente e nos mesmos folds:

acurácia 98,63% ± 0,76; F1 98,59%; kappa 98,44%.

Teste estatístico: Wilcoxon pareado sobre os 10 folds, nível de 5%.



\## H1. CNN do Zaykov (RGB, treinada do zero) contra a DenseNet201

Hipótese: a CNN fica abaixo da DenseNet201, com acurácia média entre 94% e 97,5%,

e a perda se concentra nas classes pequenas (ebenus, pinus, asphodelus, pistacia).

Base: treinar do zero rende menos com poucas imagens; na tese, a VGG19+CBAM do zero

ficou abaixo da DenseNet201 com fine-tuning.

Critério: a CNN entra no app como modelo leve opcional se a acurácia média for de

pelo menos 97% e nenhuma classe tiver F1 médio abaixo de 90%.



\## H2. Velocidade de inferência em CPU

Hipótese: a CNN é pelo menos 10 vezes mais rápida que a DenseNet201 por imagem,

com lote de 1, na mesma CPU.

Base: cerca de 50 vezes menos operações por imagem (88 milhões contra 4 bilhões).

Critério: a vantagem de velocidade só justifica o modelo leve se H1 também passar.



\## H3. CNN do Zaykov em escala de cinza contra a mesma CNN em cor

Hipótese: a versão em cinza perde até 1 ponto de acurácia, porque a coloração

do CPD1 pode carregar informação útil.

Critério: adotar cinza só se a diferença ficar dentro de 1 desvio (cerca de 0,8 ponto)

e o Wilcoxon der p > 0,05.



\## H4. Grad-CAM

Hipótese: usando a camada relu\_256 (mapa 7x7), os mapas da CNN destacam regiões

do grão comparáveis às da DenseNet201.

Critério: avaliação visual em uma amostra fixa de imagens de teste.

