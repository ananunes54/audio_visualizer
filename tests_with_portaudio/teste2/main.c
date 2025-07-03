#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include "portaudio.h"

// --- MACROS DE CONTROLE ---
#define DURACAO_SEGUNDOS   30      // Tempo total de execução da captura
#define SAMPLE_RATE        44100   // Taxa de amostragem
#define FRAMES_PER_BUFFER  512     // Amostras por buffer (controla a latência)
#define NUM_CHANNELS       1       // 1 para mono, 2 para stereo
#define SAMPLE_FORMAT      paInt16 // Formato da amostra (16-bit)
#define PIPE_NAME          "/tmp/audio_pipe" // Nome do pipe para comunicação

// Estrutura para passar dados para o callback do PortAudio
typedef struct {
    int pipe_fd; // File descriptor do pipe
} paTestData;

// Função de callback: chamada pelo PortAudio sempre que um novo buffer de áudio está pronto
static int audioCallback(const void *inputBuffer, void *outputBuffer,
                         unsigned long framesPerBuffer,
                         const PaStreamCallbackTimeInfo* timeInfo,
                         PaStreamCallbackFlags statusFlags,
                         void *userData) {
    paTestData *data = (paTestData*)userData;
    const short *read_ptr = (const short*)inputBuffer;
    long bytes_to_write = framesPerBuffer * NUM_CHANNELS * sizeof(short);

    if (inputBuffer == NULL) {
        return paContinue;
    }

    // Escreve os dados do buffer diretamente no pipe
    write(data->pipe_fd, read_ptr, bytes_to_write);

    return paContinue;
}

// --- FUNÇÃO PRINCIPAL ---
int main(void) {
    PaStream *stream;
    PaError err;
    paTestData data;

    printf("Inicializando PortAudio...\n");
    err = Pa_Initialize();
    if (err != paNoError) goto error;

    // Cria o pipe nomeado (FIFO)
    mkfifo(PIPE_NAME, 0666);
    printf("Aguardando o programa Python se conectar ao pipe '%s'...\n", PIPE_NAME);
    // Abre o pipe para escrita. Esta chamada irá bloquear até que o lado de leitura (Python) seja aberto.
    data.pipe_fd = open(PIPE_NAME, O_WRONLY);
    if (data.pipe_fd == -1) {
        perror("Erro ao abrir o pipe");
        return 1;
    }
    printf("Conexão estabelecida! Iniciando a captura de áudio.\n");


    // Abre o stream de áudio padrão
    err = Pa_OpenDefaultStream(&stream,
                               NUM_CHANNELS,
                               0, // Sem canais de saída
                               SAMPLE_FORMAT,
                               SAMPLE_RATE,
                               FRAMES_PER_BUFFER,
                               audioCallback,
                               &data);
    if (err != paNoError) goto error;

    // Inicia o stream
    err = Pa_StartStream(stream);
    if (err != paNoError) goto error;

    // Mantém o programa rodando pela duração definida
    printf("Gravando por %d segundos...\n", DURACAO_SEGUNDOS);
    Pa_Sleep(DURACAO_SEGUNDOS * 1000);

    // Para o stream
    err = Pa_StopStream(stream);
    if (err != paNoError) goto error;

    printf("Gravação finalizada.\n");

    // Fecha o stream e termina o PortAudio
    Pa_CloseStream(stream);
    Pa_Terminate();

    // Fecha e remove o pipe
    close(data.pipe_fd);
    unlink(PIPE_NAME);

    return 0;

error:
    fprintf(stderr, "Ocorreu um erro no PortAudio\n");
    fprintf(stderr, "Código do Erro: %d\n", err);
    fprintf(stderr, "Mensagem de Erro: %s\n", Pa_GetErrorText(err));
    Pa_Terminate();
    // Garante que o pipe seja removido em caso de erro
    unlink(PIPE_NAME);
    return -1;
}
