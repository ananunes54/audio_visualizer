#include <stdio.h>
#include <stdlib.h>
#include <portaudio.h>

#define CHANNELS (1)
#define SAMPLE_FORMAT (paInt16)
#define FRAMES_PER_BUFFER (44100)
#define SAMPLE_RATE (44100)
#define ARQUIVO "teste.bin"


void SetParameters(PaStreamParameters *stream_parameters, const PaDeviceInfo *device_info, PaDeviceIndex device)
{
	stream_parameters->device = device;
	stream_parameters->channelCount = CHANNELS;
	stream_parameters->sampleFormat = SAMPLE_FORMAT;
	stream_parameters->suggestedLatency = device_info->defaultHighOutputLatency;
	stream_parameters->hostApiSpecificStreamInfo = NULL;
}



void GetError(PaError error, const char *function)
{
	if (error == paNoError)
		printf("No error in: \"%s\"\n", function);
	else
		printf("Error: %s \nin: \"%s\"\n", Pa_GetErrorText(error), function);

}



void ReadFile(short int *buffer)
{
	FILE *fp = fopen(ARQUIVO, "rb");

	fread(buffer, sizeof(paInt16), FRAMES_PER_BUFFER, fp);

	fclose(fp);

	for (int i = 0; i < FRAMES_PER_BUFFER; i++) buffer[i] = 10*buffer[i];
}



int main()
{
	PaError init_terminate;
	PaError opening_stream;
	PaError starting_stream;
	PaError writing_stream;
	PaStream *output_stream;
	PaStreamParameters output_stream_parameters;
	PaDeviceIndex default_output_device;
	const PaDeviceInfo *output_device_info;
	
	
	init_terminate = Pa_Initialize();
	GetError(init_terminate, "initializing portaudio");

	short int buff[FRAMES_PER_BUFFER] = {0};

	ReadFile(buff);

	output_device_info = (PaDeviceInfo *)malloc(sizeof(PaDeviceInfo));

	default_output_device = Pa_GetDefaultOutputDevice();


	output_device_info = Pa_GetDeviceInfo(default_output_device);

	SetParameters(&output_stream_parameters, output_device_info, default_output_device);



	opening_stream = Pa_OpenStream(&output_stream, NULL, &output_stream_parameters, SAMPLE_RATE, FRAMES_PER_BUFFER, paNoFlag, NULL, NULL);
	GetError(opening_stream, "opening stream");


	starting_stream = Pa_StartStream(output_stream);
	GetError(starting_stream, "starting stream");


	writing_stream = Pa_WriteStream(output_stream, &buff, FRAMES_PER_BUFFER);
	GetError(writing_stream, "reproducing audio");

	Pa_Sleep(1000);

	starting_stream = Pa_StopStream(output_stream);
	GetError(starting_stream, "stop stream");


	opening_stream = Pa_CloseStream(output_stream);
	GetError(opening_stream, "closing stream");


	init_terminate = Pa_Terminate();
	GetError(init_terminate, "terminating portaudio");

}
