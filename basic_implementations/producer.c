#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

#define BUFFER_SIZE (5)
#define BUFFER_SIZE_BYTES (sizeof(int)*BUFFER_SIZE)

int main()
{
	int pipefd[2];

	pipe(pipefd);

	int buffer[BUFFER_SIZE] = {0};

	if (fork() == 0)
	{
		close(pipefd[1]);		

		while (read(pipefd[0], &buffer, BUFFER_SIZE_BYTES) > 0)
		{
			for (int i = 0; i < BUFFER_SIZE; i++)
				printf("%d, ", buffer[i]);
		
			printf("\n");
		}

		close(pipefd[0]);
	
		exit(EXIT_SUCCESS);
	}
	

	else
	{
		close(pipefd[0]);
	
		for (int i = 0; i < 5; i++)
		{
			for (int j = 0; j < BUFFER_SIZE; j++)
			{
				buffer[j] = i+j;
			}
			
			write(pipefd[1], &buffer, BUFFER_SIZE_BYTES);
		}

		close(pipefd[1]);
		
		wait(NULL);

		exit(EXIT_SUCCESS);
	}
	
}
