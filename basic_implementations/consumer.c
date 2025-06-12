#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

#define BUFFER_SIZE (5)
#define BUFFER_SIZE_BYTES (sizeof(int)*BUFFER_SIZE)

int main()
{
	int buffer[BUFFER_SIZE] = {0};

	while(read(STDIN_FILENO, &buffer, BUFFER_SIZE_BYTES) > 0)
	{
		for (int i = 0; i < BUFFER_SIZE; i++)
			printf("%d, ", buffer[i]);

		printf("\n");
	}

	close(STDIN_FILENO);

	exit(EXIT_SUCCESS);
}
