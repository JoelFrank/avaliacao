#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <math.h>

#define TAM 4
#define ACOES 4
#define EPISODIOS 1000
#define ALPHA 0.1
#define GAMMA 0.9
#define EPSILON 0.1

int Q[TAM][TAM][ACOES];
int pontos;

int recompensa(int x, int y, int ouro_x, int ouro_y, int wumpus_x, int wumpus_y, int buraco_x, int buraco_y) {
	if (x == ouro_x && y == ouro_y) return 100;
	if (x == wumpus_x && y == wumpus_y) return -100;
	if (x == buraco_x && y == buraco_y) return -100;
	return -1;
}

int escolher_acao(int x, int y) {
	if ((rand() / (float)RAND_MAX) < EPSILON) return rand() % ACOES;
	int melhor = 0;
	for (int a = 1; a < ACOES; a++) {
		if (Q[x][y][a] > Q[x][y][melhor]) melhor = a;
	}
	return melhor;
}

void mover(int *x, int *y, int acao) {
	if (acao == 0 && *x > 0) (*x)--;
	if (acao == 1 && *x < TAM - 1) (*x)++;
	if (acao == 2 && *y > 0) (*y)--;
	if (acao == 3 && *y < TAM - 1) (*y)++;
}

void treinar() {
	for (int ep = 0; ep < EPISODIOS; ep++) {
		int x = 0, y = 0;
		int ouro_x = rand() % TAM, ouro_y = rand() % TAM;
		while (ouro_x == 0 && ouro_y == 0) {
			ouro_x = rand() % TAM; ouro_y = rand() % TAM;
		}
		int wumpus_x = rand() % TAM, wumpus_y = rand() % TAM;
		while ((wumpus_x == 0 && wumpus_y == 0) || (wumpus_x == ouro_x && wumpus_y == ouro_y)) {
			wumpus_x = rand() % TAM; wumpus_y = rand() % TAM;
		}
		int buraco_x = rand() % TAM, buraco_y = rand() % TAM;
		while ((buraco_x == 0 && buraco_y == 0) || (buraco_x == ouro_x && buraco_y == ouro_y) || (buraco_x == wumpus_x && buraco_y == wumpus_y)) {
			buraco_x = rand() % TAM; buraco_y = rand() % TAM;
		}
		int fim = 0;
		while (!fim) {
			int acao = escolher_acao(x, y);
			int nx = x, ny = y;
			mover(&nx, &ny, acao);
			int r = recompensa(nx, ny, ouro_x, ouro_y, wumpus_x, wumpus_y, buraco_x, buraco_y);
			int maxQ = Q[nx][ny][0];
			for (int a = 1; a < ACOES; a++) {
				if (Q[nx][ny][a] > maxQ) maxQ = Q[nx][ny][a];
			}
			Q[x][y][acao] += ALPHA * (r + GAMMA * maxQ - Q[x][y][acao]);
			x = nx; y = ny;
			if (r == 100 || r == -100) fim = 1;
		}
	}
}

void jogar() {
	int x = 0, y = 0;
	int ouro_x = rand() % TAM, ouro_y = rand() % TAM;
	while (ouro_x == 0 && ouro_y == 0) {
		ouro_x = rand() % TAM; ouro_y = rand() % TAM;
	}
	int wumpus_x = rand() % TAM, wumpus_y = rand() % TAM;
	while ((wumpus_x == 0 && wumpus_y == 0) || (wumpus_x == ouro_x && wumpus_y == ouro_y)) {
		wumpus_x = rand() % TAM; wumpus_y = rand() % TAM;
	}
	int buraco_x = rand() % TAM, buraco_y = rand() % TAM;
	while ((buraco_x == 0 && buraco_y == 0) || (buraco_x == ouro_x && buraco_y == ouro_y) || (buraco_x == wumpus_x && buraco_y == wumpus_y)) {
		buraco_x = rand() % TAM; buraco_y = rand() % TAM;
	}
	int fim = 0;
	pontos = 0;
	while (!fim) {
		system("clear");
		printf("Agente está em (%d, %d)\n", x, y);
		for (int j = 0; j < TAM; j++) {
			for (int i = 0; i < TAM; i++) {
				if (i == x && j == y) printf("#\t");
				else printf("*\t");
			}
			printf("\n");
		}
		printf("\n");

		int acao = escolher_acao(x, y);
		int nx = x, ny = y;
		mover(&nx, &ny, acao);
		int r = recompensa(nx, ny, ouro_x, ouro_y, wumpus_x, wumpus_y, buraco_x, buraco_y);
		pontos += r;
		x = nx; y = ny;
		if (r == 100) { printf("Achou o OURO!\n"); fim = 1; }
		else if (r == -100) { printf("GAME OVER!\n"); fim = 1; }
		sleep(1);
	}
	printf("Pontuação final: %d\n", pontos);
}

int main() {
	srand(time(NULL));
	treinar();
	jogar();
	return 0;
}
