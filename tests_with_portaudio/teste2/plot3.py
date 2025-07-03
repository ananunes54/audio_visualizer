import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sys
from collections import deque # Para armazenar os dados de forma eficiente

# --- CONSTANTES (DEVEM SER IGUAIS ÀS DO PROGRAMA EM C) ---
PIPE_NAME = "/tmp/audio_pipe"
SAMPLE_RATE = 44100
FRAMES_PER_BUFFER = 512 # TAMANHO DO CHUNK QUE VEM DO C
NUM_CHANNELS = 1
SAMPLE_WIDTH = 2  # Bytes por amostra (paInt16 é 2 bytes)

# Tamanho do chunk a ser lido do pipe em bytes
CHUNK_SIZE = FRAMES_PER_BUFFER * NUM_CHANNELS * SAMPLE_WIDTH

# --- NOVAS CONSTANTES PARA VISUALIZAÇÃO ---
# Quantidade de amostras que você quer exibir no gráfico
SAMPLES_TO_DISPLAY = 20*FRAMES_PER_BUFFER
# Garante que SAMPLES_TO_DISPLAY seja um múltiplo de FRAMES_PER_BUFFER
if SAMPLES_TO_DISPLAY % FRAMES_PER_BUFFER != 0:
    raise ValueError("SAMPLES_TO_DISPLAY deve ser um múltiplo de FRAMES_PER_BUFFER")

# Buffer circular para armazenar os dados para plotagem
# Ele armazenará os últimos SAMPLES_TO_DISPLAY amostras
audio_buffer = deque(np.zeros(SAMPLES_TO_DISPLAY, dtype=np.int16), maxlen=SAMPLES_TO_DISPLAY)


# --- CONFIGURAÇÃO DO GRÁFICO PYQTGRAPH ---
app = pg.mkQApp("Real-time Audio Plot")
win = pg.GraphicsLayoutWidget(show=True, title="Áudio do Microfone em Tempo Real")
win.resize(800, 400)

plot_widget = win.addPlot(title="Amplitude do Áudio")
plot_widget.setLabel('bottom', "Amostras")
plot_widget.setLabel('left', "Amplitude")
plot_widget.setYRange(-32768, 32767) # Limites para áudio de 16-bit
plot_widget.setXRange(0, SAMPLES_TO_DISPLAY) # AGORA O EIXO X VAI ATÉ SAMPLES_TO_DISPLAY
plot_widget.showGrid(x=True, y=True)

# Cria uma linha inicial com dados zerados
curve = plot_widget.plot(pen='y')

# Abre o pipe para leitura em modo binário
print(f"Aguardando dados no pipe '{PIPE_NAME}'...")
try:
    pipe_fd = open(PIPE_NAME, 'rb')
    print("Pipe conectado. Iniciando a plotagem...")
except FileNotFoundError:
    print(f"Erro: O pipe '{PIPE_NAME}' não foi encontrado. Certifique-se de que o programa em C o criou.")
    sys.exit(1)

# --- FUNÇÃO DE ATUALIZAÇÃO ---
def update_plot():
    """
    Função chamada periodicamente pelo timer para atualizar o gráfico.
    """
    global audio_buffer # Precisamos modificar o buffer global

    try:
        raw_data = pipe_fd.read(CHUNK_SIZE)

        if not raw_data:
            print("Fim da transmissão de dados.")
            pipe_fd.close()
            QtCore.QCoreApplication.quit() # Fecha a aplicação PyQt
            return

        audio_data_chunk = np.frombuffer(raw_data, dtype=np.int16)

        # Adiciona os novos dados ao buffer, removendo os mais antigos automaticamente
        # 'extend' adiciona múltiplos elementos eficientemente
        audio_buffer.extend(audio_data_chunk)

        # Converte o deque para um array numpy para plotagem
        # A cópia aqui é necessária, pois pyqtgraph espera um array numpy
        data_to_plot = np.array(audio_buffer)

        curve.setData(data_to_plot) # Atualiza o gráfico com os dados acumulados

    except Exception as e:
        print(f"Erro durante a leitura ou plotagem: {e}")
        pipe_fd.close()
        QtCore.QCoreApplication.quit()

# --- CONFIGURAÇÃO DO TIMER ---
timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(10) # Atualiza a cada 10 ms (ou tão rápido quanto os dados chegam)

# --- INICIA A APLICAÇÃO PYQTGRAPH ---
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.exec() # Inicia o loop de eventos do PyQt

print("Fechando o pipe.")
pipe_fd.close()
