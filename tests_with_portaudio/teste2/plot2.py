import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sys

# --- CONSTANTES (DEVEM SER IGUAIS ÀS DO PROGRAMA EM C) ---
PIPE_NAME = "/tmp/audio_pipe"
SAMPLE_RATE = 44100
FRAMES_PER_BUFFER = 512
NUM_CHANNELS = 1
SAMPLE_WIDTH = 2  # Bytes por amostra (paInt16 é 2 bytes)

# Tamanho do chunk a ser lido do pipe em bytes
CHUNK_SIZE = FRAMES_PER_BUFFER * NUM_CHANNELS * SAMPLE_WIDTH

# --- CONFIGURAÇÃO DO GRÁFICO PYQTGRAPH ---
app = pg.mkQApp("Real-time Audio Plot")
win = pg.GraphicsLayoutWidget(show=True, title="Áudio do Microfone em Tempo Real")
win.resize(800, 400)

plot_widget = win.addPlot(title="Amplitude do Áudio")
plot_widget.setLabel('bottom', "Amostras")
plot_widget.setLabel('left', "Amplitude")
plot_widget.setYRange(-32768, 32767) # Limites para áudio de 16-bit
plot_widget.setXRange(0, 1024)
plot_widget.showGrid(x=True, y=True)

# Cria uma linha inicial com dados zerados
curve = plot_widget.plot(pen='y')

# Abre o pipe para leitura em modo binário
# O script irá pausar aqui até que o programa em C crie e abra o pipe
print(f"Aguardando dados no pipe '{PIPE_NAME}'...")
try:
    pipe_fd = open(PIPE_NAME, 'rb')
    print("Pipe conectado. Iniciando a plotagem...")
except FileNotFoundError:
    print(f"Erro: O pipe '{PIPE_NAME}' não foi encontrado. Certifique-se de que o programa em C o criou.")
    sys.exit(1) # Exit if the pipe doesn't exist

# --- FUNÇÃO DE ATUALIZAÇÃO ---
def update_plot():
    """
    Função chamada periodicamente pelo timer para atualizar o gráfico.
    """
    try:
        raw_data = pipe_fd.read(CHUNK_SIZE)

        if not raw_data:
            print("Fim da transmissão de dados.")
            pipe_fd.close()
            QtCore.QCoreApplication.quit() # Fecha a aplicação PyQt
            return

        audio_data = np.frombuffer(raw_data, dtype=np.int16)
        curve.setData(audio_data)
    except Exception as e:
        print(f"Erro durante a leitura ou plotagem: {e}")
        pipe_fd.close()
        QtCore.QCoreApplication.quit()

# --- CONFIGURAÇÃO DO TIMER ---
# Use um QTimer para chamar a função de atualização periodicamente
timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(10) # Atualiza a cada 10 ms (ajuste conforme necessário, mas o principal é a chegada dos dados)

# --- INICIA A APLICAÇÃO PYQTGRAPH ---
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.exec() # Inicia o loop de eventos do PyQt

# Garante que o pipe seja fechado ao final, mesmo que a janela seja fechada manualmente
# Este bloco 'finally' não é tão direto como no matplotlib.show(),
# mas o 'quit()' no 'update_plot' e a estrutura do Qt garantem o fechamento.
print("Fechando o pipe.")
pipe_fd.close()
