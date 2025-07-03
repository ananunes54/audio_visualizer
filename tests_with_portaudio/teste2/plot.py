import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- CONSTANTES (DEVEM SER IGUAIS ÀS DO PROGRAMA EM C) ---
PIPE_NAME = "/tmp/audio_pipe"
SAMPLE_RATE = 44100
FRAMES_PER_BUFFER = 512
NUM_CHANNELS = 1
SAMPLE_WIDTH = 2  # Bytes por amostra (paInt16 é 2 bytes)

# Tamanho do chunk a ser lido do pipe em bytes
CHUNK_SIZE = FRAMES_PER_BUFFER * NUM_CHANNELS * SAMPLE_WIDTH

# --- CONFIGURAÇÃO DO GRÁFICO ---
fig, ax = plt.subplots()
x = np.arange(0, FRAMES_PER_BUFFER)
# Cria uma linha inicial com dados zerados
line, = ax.plot(x, np.zeros(FRAMES_PER_BUFFER, dtype=np.int16))

# Define os limites do gráfico
ax.set_ylim(-32768, 32767) # Limites para áudio de 16-bit
ax.set_xlim(0, FRAMES_PER_BUFFER)
ax.set_title("Áudio do Microfone em Tempo Real")
ax.set_xlabel("Amostras")
ax.set_ylabel("Amplitude")
plt.grid(True)

# Abre o pipe para leitura em modo binário
# O script irá pausar aqui até que o programa em C crie e abra o pipe
print(f"Aguardando dados no pipe '{PIPE_NAME}'...")
pipe_fd = open(PIPE_NAME, 'rb')
print("Pipe conectado. Iniciando a plotagem...")


# --- FUNÇÃO DE ANIMAÇÃO ---
def update(frame):
    """
    Função chamada periodicamente pela animação para atualizar o gráfico.
    """
    # Lê um chunk de dados do pipe
    raw_data = pipe_fd.read(CHUNK_SIZE)

    # Se não houver mais dados, o programa em C terminou
    if not raw_data:
        print("Fim da transmissão de dados.")
        plt.close() # Fecha a janela do gráfico
        return line,

    # Converte os bytes brutos para um array de inteiros de 16-bit
    audio_data = np.frombuffer(raw_data, dtype=np.int16)

    # Atualiza os dados da linha do gráfico
    line.set_ydata(audio_data)
    
    return line,

# Cria a animação
# blit=True otimiza a renderização, redesenhando apenas o que mudou.
# interval=10 define um pequeno atraso, mas a velocidade real será ditada
# pela velocidade com que os dados chegam no pipe.
# cache_frame_data=False é importante para evitar consumo excessivo de memória.
ani = animation.FuncAnimation(
    fig,
    update,
    blit=True,
    interval=10,
    cache_frame_data=False
)

try:
    plt.show()
finally:
    # Garante que o pipe seja fechado ao final
    print("Fechando o pipe.")
    pipe_fd.close()
