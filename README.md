# Polling-Simulator

Simulador de uso de polling para Acesso ao meio baseado em teoria das filas.  
Entradas:

- Número de Nós (inicial e final)
- Intervalos e distribuição da geração de pacotes dos nós (Aleatório, Poisson, Exponencial)
- Tempo de simulação
- modelo de polling (FIFO (Round-Robin), Aleatório, Predict (knowing), hibrido)
- Sucesso da transmissão


Saídas (CSV file):

- Delay
- Packets Send
- Lost Packets
- Total Packets
- Success Polls
- Failed Polls
- Total Polls
