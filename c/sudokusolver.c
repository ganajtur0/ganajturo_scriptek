#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define DIE(x) do { \
            fprintf(stderr, "%s\n", x); \
            exit(1); \
       } while(0);

bool
possible(int s[9][9], int i, int j, int x) {

    int tmp;

    for (tmp = 0; tmp<9; ++tmp)
        if (s[i][tmp] == x)
            return false;

    for (tmp = 0; tmp<9; ++tmp)
        if (s[tmp][j] == x)
            return false;
    
    int origin_i = (i / 3) * 3,
        origin_j = (j / 3) * 3;

    for (int i_off = 0; i_off < 3; ++i_off) {
        for (int j_off = 0; j_off < 3; ++j_off) {

            int ni = origin_i + i_off,
                nj = origin_j + j_off;

            if (s[ni][nj] == x)
                return false;
        }
    }

    return true;
}

void
display(int sudoku[9][9]){
    putc('\n', stdout);
    for (int i = 0; i<9; ++i){
        for (int j = 0; j<9; ++j){
            putc(sudoku[i][j] + '0', stdout);
            putc(' ', stdout);
        }
        putc('\n', stdout);
    }
}

void
solve(int s[9][9]){

    for (int i = 0; i < 9; ++i){
        for (int j = 0; j < 9; ++j){
            if ( s[i][j] == 0) {
                for (int x = 1; x <= 9; ++x) {
                    if (possible(s, i, j, x)){
                        s[i][j] = x;
                        solve(s);
                        s[i][j] = 0;
                    }
                }
                return;
            }
        }
    }
    display(s);
}

void
readfile (int s[9][9], const char *filepath){
    FILE *f = fopen(filepath, "r");

    if (f == NULL)
        DIE("Nem sikerült megnyitni a beolvasandó fájlt!");

    for (int i = 0; i<9; ++i){
        if ( fscanf(f, "%d %d %d %d %d %d %d %d %d\n",
            &(s[i][0]), &(s[i][1]), &(s[i][2]), &(s[i][3]), &(s[i][4]), &(s[i][5]), &(s[i][6]), &(s[i][7]), &(s[i][8])) != 9 )
            DIE("A megadott fájl nem megfelelő formátumú!");
    }

}

int
main(int argc, char *argv[]){

    int sudoku[9][9] = {0};

    if (argc < 2)
        DIE("Kérlek, add meg a beolvasandó fájl lelőhelyét!");

    readfile(sudoku, argv[1]);

    display(sudoku);

    solve(sudoku);

    return 0;

}
