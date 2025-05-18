#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <portaudio.h>
#include <stdint.h>

#define DEVICE                 (0)
#define CHANNELS               (1)
#define SAMPLE_FORMAT    (paInt16)
#define SAMPLE_RATE        (44100)
#define FRAMES_PER_BUFFER  (44100)
#define TIME                   (1)


void CheckError (PaError error, const char *step) {

	if (error == paNoError)
		printf("No error in: %s\n", step );
	
	else {
		printf("%s\n", Pa_GetErrorText(error));
		exit(EXIT_FAILURE);
	}

}


PaStreamParameters *setParameters(const PaDeviceInfo *device_info) {

	PaStreamParameters *stream_parameters = (PaStreamParameters *)malloc(sizeof(PaStreamParameters));

	stream_parameters->device                    = DEVICE;
	stream_parameters->channelCount              = CHANNELS;
	stream_parameters->sampleFormat              = SAMPLE_FORMAT;
	stream_parameters->suggestedLatency          = device_info->defaultHighInputLatency;
	stream_parameters->hostApiSpecificStreamInfo = NULL;
	
	return stream_parameters;
}


void WriteToFile(uint16_t *buffer, int samples) {

	FILE *fp = fopen("stream_data.bin", "wb");
	size_t written = fwrite(buffer, sizeof(buffer[0]), samples, fp);
	
	if (written != samples) {
		fclose(fp);
		printf("erro ao escrever no arquivo\n");
		exit(EXIT_FAILURE);
	}

	fclose(fp);
}


int main() {

	PaError                  init_terminate;
	PaError                  is_stream_supported;
	PaError                  opening_stream;
	PaError                  starting_stream;
	PaError                  reading_stream;
	PaStream                 *audio_input;
	PaDeviceIndex            default_input; 
	PaStreamParameters       *input_parameters;
	const PaDeviceInfo       *default_input_info; 
	uint16_t                 buff[44100];
	


	//inicializa a biblioteca
	init_terminate = Pa_Initialize();
	CheckError(init_terminate, "initializing port audio");


	//determina o dispositivo padrão de entrada
	default_input = Pa_GetDefaultInputDevice();


	//armazena as informações sobre o dispositivo
	default_input_info = (PaDeviceInfo *)malloc(sizeof(PaDeviceInfo));
	default_input_info = Pa_GetDeviceInfo(default_input);

	
	//define os parametros do stream
	input_parameters = setParameters(default_input_info);
	
	
	is_stream_supported = Pa_IsFormatSupported(input_parameters, NULL, SAMPLE_RATE);
	
	
	//abre stream de input
	opening_stream = Pa_OpenStream(&audio_input, input_parameters, NULL, SAMPLE_RATE, FRAMES_PER_BUFFER, paNoFlag, NULL, NULL);
	CheckError(opening_stream, "opening stream");


	//comeca a processar o audio
	starting_stream = Pa_StartStream(audio_input);
	CheckError(starting_stream, "starting stream");

	
	reading_stream = Pa_ReadStream(audio_input, buff, FRAMES_PER_BUFFER);
	CheckError(reading_stream, "reading stream");


	//para de processar o audio
	starting_stream = Pa_StopStream(audio_input);
	CheckError(starting_stream, "stoping stream");


	//fecha stream de input
	opening_stream = Pa_CloseStream(audio_input);
	CheckError(opening_stream, "closing stream");


	//encerra a biblioteca
	init_terminate = Pa_Terminate();
	CheckError(init_terminate, "terminating port audio");

	WriteToFile(buff, FRAMES_PER_BUFFER);

	return 0;
}
