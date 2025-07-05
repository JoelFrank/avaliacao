#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define TAM 4
#define ESTADOS (TAM * TAM)
#define ACOES 4 

#define EPISODIOS 500
#define ALPHA 0.1
#define GAMMA 0.9
#define EPSILON 0.1

int mundo[TAM][TAM] = {
    {0, -1, 0, -100},  
    {0,  0, 0, 0},
    {-100, 0, -1, 0},  
    {0,  0, 0, 100}    
};

double Q[ESTADOS][ACOES];

int estadoIndex(int x, int y) {
    return x * TAM + y;
}

int escolherAcao(int estado) {
    if ((double) rand() / RAND_MAX < EPSILON) {
        return rand() % ACOES;
    } else {
        double max = Q[estado][0];
        int acao = 0;
        for (int i = 1; i < ACOES; i++) {
            if (Q[estado][i] > max) {
                max = Q[estado][i];
                acao = i;
            }
        }
        return acao;
    }
}

int mover(int *x, int *y, int acao, int *recompensa) {
    int nx = *x, ny = *y;

    switch (acao) {
        case 0: if (*x > 0) nx--; break;         
        case 1: if (*x < TAM - 1) nx++; break;  
        case 2: if (*y > 0) ny--; break;         
        case 3: if (*y < TAM - 1) ny++; break;   
    }

    *recompensa = -1;
    int conteudo = mundo[nx][ny];
    if (conteudo == 100) *recompensa = 100;
    else if (conteudo == -100 || conteudo == -1) *recompensa = -100;

    *x = nx;
    *y = ny;

    return estadoIndex(nx, ny);
}

void treinar() {
    for (int ep = 0; ep < EPISODIOS; ep++) {
        int x = 0, y = 0;
        int estado = estadoIndex(x, y);

        while (1) {
            int acao = escolherAcao(estado);
            int recompensa;
            int novoEstado = mover(&x, &y, acao, &recompensa);

            double maxQ = Q[novoEstado][0];
            for (int i = 1; i < ACOES; i++) {
                if (Q[novoEstado][i] > maxQ) {
                    maxQ = Q[novoEstado][i];
                }
            }

            Q[estado][acao] += ALPHA * (recompensa + GAMMA * maxQ - Q[estado][acao]);

            estado = novoEstado;

            if (recompensa == 100 || recompensa == -100)
                break;
        }
    }
}

void mostrarPolitica() {
    const char* direcoes[] = {"↑", "↓", "←", "→"};
    for (int i = 0; i < TAM; i++) {
        for (int j = 0; j < TAM; j++) {
            if (mundo[i][j] == -100)
                printf(" P ");
            else if (mundo[i][j] == -1)
                printf(" W ");
            else if (mundo[i][j] == 100)
                printf(" G ");
            else {
                int estado = estadoIndex(i, j);
                int melhor = 0;
                for (int a = 1; a < ACOES; a++) {
                    if (Q[estado][a] > Q[estado][melhor])
                        melhor = a;
                }
                printf(" %s ", direcoes[melhor]);
            }
        }
        printf("\n");
    }
}

int main() {
    srand(time(NULL));
    treinar();
    printf("Política aprendida:\n");
    mostrarPolitica();
    return 0;
}
