#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>


#define FILE_NAME "440Hz_44100Hz_16bit_05sec.wav"

#define FORMAT_OFFSET 20
#define CHANNELS_OFFSET 22
#define SAMPLE_RATE_OFFSET 24
#define CHUNK_SIZE_OFFSET 40
#define FILE_ENTRY_POINT 44

#define BUFFER_SIZE 1764

typedef struct info {
	uint16_t format_type;
	uint16_t channels;
	uint32_t sample_rate;
	uint32_t data_chunk_size;
} info;


//criar função para lidar com diferentes tipos de dados e verificando se o ponteiro para eles é nulo
void CheckError(void *ptr, const char *message) {
	if (ptr == NULL) {
		printf("erro ao %s\n", message);
		exit(EXIT_FAILURE);
	}
}


info *SetFileInfo(FILE *fp) {
	info *file_info = (info *)malloc(sizeof(info));
	size_t read;

	fseek(fp, FORMAT_OFFSET, SEEK_SET);
	read = fread(&file_info->format_type, sizeof(uint16_t), 1, fp);
	
	fseek(fp, CHANNELS_OFFSET, SEEK_SET);
	read = fread(&file_info->channels, sizeof(uint16_t), 1, fp);
	
	fseek(fp, SAMPLE_RATE_OFFSET, SEEK_SET);
	read = fread(&file_info->sample_rate, sizeof(uint32_t), 1, fp);

	fseek(fp, CHUNK_SIZE_OFFSET, SEEK_SET);
	read = fread(&file_info->data_chunk_size, sizeof(uint32_t), 1, fp);

	return file_info;
}


void FreeInfo(info *file_info) {
	free(file_info);
}


void PrintInfo(info *file_info) {
	printf("format type: %hu\n", file_info->format_type);
	printf("channels: %hu\n", file_info->channels);
	printf("sample rate: %u\n", file_info->sample_rate);
	printf("data chunk size: %u\n", file_info->data_chunk_size);
}


void FillDataFile(FILE *fp_read, info *file_info) {

	uint16_t buffer[BUFFER_SIZE] = {0};
	FILE *fp_write = fopen("data.bin", "wb");

	CheckError(fp_write, "abrir arquivo de escrita");
	
	size_t read, written;
	for (int i = 0; i < file_info->sample_rate/BUFFER_SIZE; i++) {

		read = fread(&buffer, sizeof(uint16_t), BUFFER_SIZE, fp_read);
		written = fwrite(&buffer, sizeof(uint16_t), read, fp_write);
		printf("read: %lu, written: %lu\n", read, written);

	}

	fclose(fp_write);
}


int main() {
	
	//abrir o arquivo em modo binario
	FILE *fp = fopen(FILE_NAME, "rb");

	CheckError(fp, "abrir arquivo de leitura");

	info *file_info = SetFileInfo(fp);

	CheckError(file_info, "configurar informações sobre o arquivo");	

	PrintInfo(file_info);

	FillDataFile(fp, file_info);

	printf("\n");

	FreeInfo(file_info);
	fclose(fp);

	return 0;
}

