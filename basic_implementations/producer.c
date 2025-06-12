#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

#define BUFFER_SIZE (5)
#define BUFFER_SIZE_BYTES (sizeof(int)*BUFFER_SIZE)

void *thread(void *arg)
{
	int *flag = (int*)arg;
	
	while (1)
	{
		if (*flag == 1) break;
	}

	printf("thread encerrada\n");
	
	pthread_exit(NULL);
}

int main()
{
	int pipefd[2];

	pipe(pipefd);

	int buffer[BUFFER_SIZE] = {0};

	int thread_flag = 0;

	pthread_t new_thread;


	if (fork() == 0)
	{
		close(pipefd[1]);		

		dup2(pipefd[0], STDIN_FILENO);

		execl("consumer", "consumer", NULL);
	}
	

	else
	{
		close(pipefd[0]);
	
		if (pthread_create(&new_thread, NULL, thread, (void*)&thread_flag) != 0)
			printf("erro ao criar thread\n");
		

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

		thread_flag = 1;

		pthread_join(new_thread, NULL);
		exit(EXIT_SUCCESS);
	}
	
}
