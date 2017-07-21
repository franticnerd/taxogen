#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_SIGMOID 6

typedef float real;  				// Precision of float numbers
const long long max_w = 2000;              // max length of vocabulary entries
const int sigmoid_table_size = 2000;
const real sigmoid_coeff = sigmoid_table_size / MAX_SIGMOID / 2.0;
real *sigmoid_table;
int scoring = 1;


/* Fastly compute sigmoid function */
void InitSigmoidTable() {
  real x;
  printf("Initializing sigmoid table ... \n");
  sigmoid_table = (real *)malloc((sigmoid_table_size + 1) * sizeof(real));
  for (int k = 0; k < sigmoid_table_size; ++k) {
    x = 2 * (real)(MAX_SIGMOID * k) / sigmoid_table_size - MAX_SIGMOID;
    sigmoid_table[k] = 1 / (1 + exp(-x));
  }
}

inline real FastSigmoid(real x) {
  if (x > MAX_SIGMOID) return 1;
  else if (x < -MAX_SIGMOID) return 0;
  return sigmoid_table[(int)((x + MAX_SIGMOID) * sigmoid_coeff)];
}
int ArgPos(char *str, int argc, char **argv) {
  int a;
  for (a = 1; a < argc; a++)
    if (!strcmp(str, argv[a])) {
      if (a == argc - 1) {
        printf("Argument missing for %s\n", str);
        exit(1);
      }
      return a;
    }
  return -1;
}

bool readEmbeddings(FILE *f, long long & n_words, long long & size, 
    char * & vocab, float * & embedding, bool normalize) {
  long a, b;
  float len;

  fscanf(f, "%lld", &n_words);
  fscanf(f, "%lld", &size);

  printf("\tobjects: %lld, size, %lld\n", n_words, size);

  vocab = (char *) malloc(
      (long long) n_words * max_w * sizeof(char));

  embedding = (float *) malloc(
      (long long) n_words * (long long) size * sizeof(float));

  if (embedding == NULL) {
    printf("Cannot allocate memory: %lld MB    %lld  %lld\n",
        (long long) n_words * size * sizeof(float) / 1048576, n_words,
        size);
    return -1;
  }
  for (b = 0; b < n_words; b++) {
    fscanf(f, "%s", &vocab[b * max_w]);
    for (a = 0; a < size; a++)
      fscanf(f, "%f", &embedding[a + b * size]);
      len = 0;
      for (a = 0; a < size; a++)
        len += embedding[a + b * size] * embedding[a + b * size];
      len = sqrt(len);
      for (a = 0; a < size; a++)
        embedding[a + b * size] /= len;
  }
  fclose(f);
  return true;
} 

inline int readQuery(bool file, FILE *fin, char *st1, char st[][max_w]) {
  int a, b, c, cn;
  a = 0;
  while (1) {
    if (file) 
      st1[a] = fgetc(fin);
    else 
      st1[a] = fgetc(stdin);
    if (st1[a] == EOF)
      return 0;
    if ((st1[a] == '#') || (st1[a] == '\n') || (a >= max_w - 1)) {
      st1[a] = 0;
      break;
    }
    a++;
  }
  cn = 0;
  b = 0;
  c = 0;
  while (1) {
    st[cn][b] = st1[c];
    b++;
    c++;
    st[cn][b] = 0;
    if (st1[c] == 0) break;
    if (st1[c] == '#') {
      cn++;
      b = 0;
      c++;
    }
  }
  cn++;
  return cn;
}

bool searchQuery(char query[][max_w], int n_q, long long N, long long size, 
    long long *bi, long long contexts, long long targets, 
    float * M_context, char *vocab_context, float * M_target, 
    char * vocab_target, float * vec, float *bestd, char* bestw[max_w]) {
  long long a, b, c, d;
  float dist, length;
  
  for (a = 0; a < n_q; a++) {
    for (b = 0; b < contexts; b++) {
      if (!strcmp(&vocab_context[b * max_w], query[a])) break;
    }
    if (b == contexts) b = -1;
    bi[a] = b;
    if (b == -1) {
      printf("Query : %s (Out of dictionary word!)\n", query);
      continue; 
    } else {
      printf("Found Query : %s \n", query);
    }      
  }
  
  for (a = 0; a < size; a++) vec[a] = 0;
  for (b = 0; b < n_q; b++) {
    if (bi[b] == -1) continue;
    for (a = 0; a < size; a++) vec[a] += M_context[a + bi[b] * size];
  }
  
  length = 0;
  for (a = 0; a < size; a++) {
    length += vec[a] * vec[a];
  }
  length = sqrt(length); 
  for (a = 0; a < size; a++) {
    vec[a] /= length;
  }

  // initialize  
  for (a = 0; a < N; a++)
    bestd[a] = -100000;
  for (a = 0; a < N; a++)
    bestw[a][0] = 0;

  for (c = 0; c < targets; c++) {
    a = 0;
    dist = 0;
    for (a = 0; a < size; a++) {
      dist += vec[a] * M_target[a + c * size];
    }
    for (a = 0; a < N; a++) {
      if (dist > bestd[a]) {
        for (d = N - 1; d > a; d--) {
          bestd[d] = bestd[d - 1];
          strcpy(bestw[d], bestw[d - 1]);
        }
        bestd[a] = dist;
        strcpy(bestw[a], &vocab_target[c * max_w]);
        break;
      }
    }
  }
  return true;
}

int main(int argc, char **argv) {
  FILE *f;
  long long N = 1000;            // number of closest words that will be shown
  char file_context[max_w], file_target[max_w];
  char st[100][max_w], st1[max_w], *bestw[max_w];
  
  char output_folder[max_w], file_name[max_w], query_input[max_w];
  float bestd[max_w], vec[max_w];
  long long contexts, targets, size, a, cn, bi[100];
  
  float *M_context, *M_target;
  char *vocab_context, *vocab_target;
  int i;
  
  memset(file_context, 0, max_w * sizeof(char));
  memset(file_target, 0, max_w * sizeof(char));
  
  InitSigmoidTable();

  if (argc < 2) {
    printf("%s%s","Usage: ./query_search -context <FILE> ", 
        " -input <FILE> -output <FOLDER>\n");
    return 0;
  }

  if ((i = ArgPos((char *) "-context", argc, argv)) > 0) {
    strcpy(file_context, argv[i + 1]);
  }   

  if ((i = ArgPos((char *) "-input", argc, argv)) > 0) {
    strcpy(query_input, argv[i + 1]);
  }  

  if ((i = ArgPos((char *) "-output", argc, argv)) > 0) {
    strcpy(output_folder, argv[i + 1]);
  }

  N = 1000;  

  for (i = 0; i < N; i ++) bestw[i] = (char *)malloc(max_w * sizeof(char));

  // read contexts
  f = fopen(file_context, "rb");
  if (f == NULL) {
    printf("Context input file not found.\n");
    return -1;
  }
  printf("Read context embeddings: \n");
  if (!readEmbeddings(f, contexts, size, vocab_context, M_context, true))
    exit(1); 
  
  targets = contexts;
  vocab_target = vocab_context;
  M_target = M_context;
  
  // read queries from the file
  int n_queries = 0;
  FILE *fin = fopen(query_input, "rb");
  while (true) {
    cn = readQuery(true, fin, st1, st);
    if (cn == 0)
      break;
    if (searchQuery(st, cn, N, size, bi, contexts, targets, M_context, 
          vocab_context, M_target, vocab_target, vec, bestd, bestw)) {
      a = 0;
      while (a < max_w - 1 && st1[a]) {
        ++a;
        if (st1[a] == '#') st1[a] = '_';
      }
      st1[a] = '\0';
      sprintf(file_name, "%s/%s", output_folder, st1);
      FILE * fo = fopen(file_name, "wb"); 
      for (a = 0; a < N; a++)
        fprintf(fo, "%s %f\n", bestw[a], bestd[a]);
    }
  }
  return 0;
}
