import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sys
from collections import deque

# --- CONSTANTES (DEVEM SER IGUAIS ÀS DO PROGRAMA EM C) ---
PIPE_NAME = "/tmp/audio_pipe"
SAMPLE_RATE = 44100
FRAMES_PER_BUFFER = 512 # TAMANHO DO CHUNK QUE VEM DO C
NUM_CHANNELS = 1
SAMPLE_WIDTH = 2  # Bytes por amostra (paInt16 é 2 bytes)

# Tamanho do chunk a ser lido do pipe em bytes
CHUNK_SIZE = FRAMES_PER_BUFFER * NUM_CHANNELS * SAMPLE_WIDTH

# --- NOVAS CONSTANTES PARA VISUALIZAÇÃO ---
# Quantidade de amostras que você quer exibir no gráfico de tempo
SAMPLES_TO_DISPLAY = 1024 # Aumentei para 4096 para uma FFT mais significativa
# Garante que SAMPLES_TO_DISPLAY seja um múltiplo de FRAMES_PER_BUFFER
if SAMPLES_TO_DISPLAY % FRAMES_PER_BUFFER != 0:
    raise ValueError("SAMPLES_TO_DISPLAY deve ser um múltiplo de FRAMES_PER_BUFFER")

# Buffer circular para armazenar os dados para plotagem no tempo
audio_buffer = deque(np.zeros(SAMPLES_TO_DISPLAY, dtype=np.int16), maxlen=SAMPLES_TO_DISPLAY)


# --- CONFIGURAÇÃO DA APLICAÇÃO E JANELA PYQTGRAPH ---
app = pg.mkQApp("Real-time Audio Plot with FFT")
win = pg.GraphicsLayoutWidget(show=True, title="Áudio do Microfone em Tempo Real com FFT")
win.resize(1000, 800) # Aumenta o tamanho da janela para acomodar dois gráficos

# --- GRÁFICO DA ONDA NO TEMPO ---
plot_time = win.addPlot(title="Onda de Áudio no Tempo")
plot_time.setLabel('bottom', "Amostras")
plot_time.setLabel('left', "Amplitude")
plot_time.setYRange(-32768, 32767) # Limites para áudio de 16-bit
plot_time.setXRange(0, SAMPLES_TO_DISPLAY)
plot_time.showGrid(x=True, y=True)
curve_time = plot_time.plot(pen='y')

win.nextRow() # Adiciona o próximo gráfico na linha de baixo

# --- GRÁFICO DA FFT (ESPECTRO DE FREQUÊNCIA) ---
plot_fft = win.addPlot(title="Espectro de Frequência (FFT)")
plot_fft.setLabel('bottom', "Frequência", units='Hz')
plot_fft.setLabel('left', "Magnitude")
# Limites Y para a magnitude da FFT (pode precisar de ajuste dependendo do volume)
plot_fft.setYRange(0, 1e7) # Valor inicial, ajuste conforme a amplitude do seu áudio
# Limites X para a frequência (até a metade da taxa de amostragem = Nyquist)
plot_fft.setXRange(0, SAMPLE_RATE / 2)
plot_fft.showGrid(x=True, y=True)
curve_fft = plot_fft.plot(pen='c') # Cor ciano para a curva da FFT


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
    Função chamada periodicamente pelo timer para atualizar os gráficos.
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

        # Adiciona os novos dados ao buffer circular
        audio_buffer.extend(audio_data_chunk)

        # Converte o deque para um array numpy para plotagem
        data_to_plot = np.array(audio_buffer)

        # --- ATUALIZA O GRÁFICO NO TEMPO ---
        curve_time.setData(data_to_plot)

        # --- CALCULA E ATUALIZA O GRÁFICO DA FFT ---
        # Aplica uma janela (ex: Hanning) para reduzir vazamento espectral
        windowed_data = data_to_plot * np.hanning(len(data_to_plot))
        
        # Calcula a FFT
        # np.fft.rfft é para dados reais, mais eficiente
        fft_result = np.fft.rfft(windowed_data)
        # Calcula a magnitude (amplitude) do espectro
        fft_magnitude = np.abs(fft_result)
        
        # Calcula as frequências correspondentes ao espectro
        # np.fft.rfftfreq é para dados reais
        fft_frequencies = np.fft.rfftfreq(len(data_to_plot), 1/SAMPLE_RATE)

        # Atualiza o gráfico da FFT
        curve_fft.setData(fft_frequencies, fft_magnitude)

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
