# Polling-Simulator

Simulador de uso de polling para Acesso ao meio baseado em teoria das filas.  
Entradas:

- grupo de nós inicial
- grupo de nós final
- passo de nós entre cada simulação
- intevalo entre cada geração de pacotes por nó em mseg
- tempo de simulação para cada grupo em min
- regra de atendimento (Cíclico, Aleatório, Predict, Predict com correção de STD )
- Datarate nominal (250000, 1000000, 2000000)
- Intervalos e distribuição da geração de pacotes dos nós (Aleatório, poisson, exponential, )
- Taxa de sucesso na transmissão dos pacotes de 0-1 (padrão 0.9)  

- tamanho do payload do pacote de dados (padrão 32)
- tamanho do payload do pacote de controle (padrão 3)
- tamanho do overhead por pacote (padrão 9)
- tempo para o modulo de rádio entrar nos modos RX ou TX (0.000130)
- velocidade de comunicação entre o microcontrolador e o módulo de rádio em  bps (padrão 400000)
- coeficiente de erro nos tempos de comunicação (padrão 1.7)

Saídas (CSV file):

- Delay/Tempo de espera na fila
- Packets Send
- Lost Packets
- Total Packets
- Success Polls
- Failed Polls
- Total Polls
