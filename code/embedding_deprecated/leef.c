/*-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

  File Name : leef.c

Purpose: embedding learning on a weighted graph 

Creation Date : 15-01-2017

Last Modified : Wed 15 Mar 2017 03:07:53 PM CDT

Created By : Huan Gui (huangui2@illinois.edu) 

_._._._._._._._._._._._._._._._._._._._._.*/

#include <assert.h>
#include <gsl/gsl_rng.h>
#include <math.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h> 
#include <unistd.h>
#include <set>

#include "ransampl.h"

#define MAX_STRING 100
#define MAX_SENTENCE 1000
#define MAX_SIGMOID 8.0
#define MAX_N_NODE_TYPE 10
#define MAX_N_EDGE_TYPE 10      // maximum number of edge types

typedef double real;          // Precision of float numbers

const int mini_batch = 1;
const int sigmoid_table_size = 2000;
const long hash_size = 30000000;     // For each type of nodes, there are 3M nodes
const int node_count_inc = 1000, neighbor_initial_count = 10;
const long neg_table_size = 1e8;
const long edge_table_size = 1e9;
const real sigmoid_coeff = sigmoid_table_size / MAX_SIGMOID / 2.0;
real sample_power = 0.75;  // defined for negative sampling as the power of frequency
real prior_power = 1;  // defined for negative sampling as the power of frequency

real max_sim = 0.5;
real max_iteration = 10;

struct ClassNeighbor {
  long node_id;
  long edge_id;
};

struct ClassNode {
  char * name;        
  real degree;
  real weight;  // for the authority of nodes 
  int *n_neighbor;
  int * max_n_neighbor;
  ClassNeighbor **neighbors;
};

struct ClassEdge {
  long src_id;
  long dst_id;
  real weight;
  real t_weight;
};

int n_node_type, n_edge_type;

// the node type for source node and dest node
int edge_node_type[MAX_N_EDGE_TYPE][2];

char output_folder[MAX_SENTENCE], input_folder[MAX_SENTENCE];
char embed_folder[MAX_SENTENCE], weight_folder[MAX_SENTENCE]; 
char train_network_file[MAX_N_EDGE_TYPE][MAX_SENTENCE];
char input_fix_embedding_file[MAX_SENTENCE];
char input_node_weight_file[MAX_SENTENCE];
char output_embedding[MAX_N_NODE_TYPE][MAX_SENTENCE];
char query_file[MAX_SENTENCE];

struct ClassNode* nodes[MAX_N_NODE_TYPE];
struct ClassEdge* edges[MAX_N_EDGE_TYPE];

set::set<long> query;

int author_type, term_type, paper_type, term_paper_edge_type;
int num_threads = 20, dim = 200;
int negative_k = 5;

// create hash table and negative table for each type of nodes and edges, respectively
long *node_hash_table[MAX_N_NODE_TYPE];
long *neg_table[MAX_N_NODE_TYPE];

ransampl_ws *edge_alias[MAX_N_EDGE_TYPE];
ransampl_ws *topic_edge_alias;

// The maximum size of each types of nodes, and the current count
long max_sz_node[MAX_N_NODE_TYPE], node_cnt[MAX_N_NODE_TYPE];

// total samples of edges to update parameters, and the current samples
long total_samples = 15, current_sample, edge_cnt[MAX_N_EDGE_TYPE];
real init_alpha = 0.025, alpha;

// the embedding of each type of nodes, relative to different types of nodes
real *emb_node[MAX_N_NODE_TYPE];

real *sigmoid_table;

//specify the types of nodes, and edge names
char node_names[MAX_N_NODE_TYPE][MAX_STRING];
char edge_names[MAX_N_EDGE_TYPE][MAX_STRING];

bool output_types[MAX_N_NODE_TYPE];
bool load_types[MAX_N_NODE_TYPE];
bool node_weight[MAX_N_NODE_TYPE];
bool edge_weight[MAX_N_NODE_TYPE];
bool valid_edge[MAX_N_NODE_TYPE][MAX_N_NODE_TYPE];

real beta[MAX_N_NODE_TYPE];
real node_sample_power[MAX_N_NODE_TYPE];

const gsl_rng_type * gsl_T;
gsl_rng * gsl_r;

clock_t start;

// the hash function is the same for all types of nodes
inline unsigned long GetHash(char *input) {
  unsigned long hash = 5381;
  char c;
  while ((c = *input) != '\0') {
    hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
    ++input;
  }
  return hash % hash_size;
}

// initialize the hash table for all types of nodes
void InitHashTable() {
  for (int node_type = 0; node_type < n_node_type; ++node_type) {
    node_hash_table[node_type] = (long *) malloc(hash_size * sizeof(long));
    for (long k = 0; k < hash_size; ++k) node_hash_table[node_type][k] = -1;
  }
}

void InsertHashTable(char *key, int value, int type) {
  unsigned long loc = GetHash(key);
  while (node_hash_table[type][loc] != -1) loc = (loc + 1) % hash_size;
  node_hash_table[type][loc] = value;
}

// hashing based on the name string
long SearchHashTable(char *key, int type) {
  unsigned long addr = GetHash(key);
  while (1) {
    if (node_hash_table[type][addr] == -1) return -1;
    if (!strcmp(key, nodes[type][node_hash_table[type][addr]].name))
      return node_hash_table[type][addr];
    addr = (addr + 1) % hash_size;
  }
  return -1;
}

void AddNeighbor(int src_type, int dst_type, long src_id, long dst_id, 
    int edge_type, long edge_id) {
  assert(valid_edge[src_type][dst_type]);
  ClassNode &node = nodes[src_type][src_id]; 
  int n_neighbor = node.n_neighbor[dst_type];

  if (n_neighbor + 2 >= node.max_n_neighbor[dst_type]) {
    node.max_n_neighbor[dst_type] *= 2;
    ClassNeighbor *tmp = (struct ClassNeighbor*) realloc(
        node.neighbors[dst_type], 
        node.max_n_neighbor[dst_type] * sizeof(struct ClassNeighbor)); 
    if (tmp != NULL) {
      node.neighbors[dst_type] = tmp;
    } else {
      printf("Fail to reallocate\n");
      exit(1);
    }
  }
  node.neighbors[dst_type][n_neighbor].node_id = dst_id;
  node.neighbors[dst_type][n_neighbor].edge_id = edge_id;
  node.n_neighbor[dst_type] += 1;
}

// Add a node to the vertex set
int AddNode(char *name, int node_type) {
  int length = strlen(name) + 1;
  if (length > MAX_STRING) length = MAX_STRING;

  ClassNode & node = nodes[node_type][node_cnt[node_type]]; 
  // insert the node, and initial the value of name, node_type, and degree;
  node.name = (char *) calloc(length, sizeof(char));
  node.degree = 0;
  node.weight = 1;

  node.n_neighbor = (int *) calloc(n_node_type, sizeof(int)); 
  node.max_n_neighbor = (int *) calloc(n_node_type, sizeof(int)); 
  node.neighbors = (ClassNeighbor **) calloc(n_node_type, sizeof(ClassNeighbor *));

  for (int i = 0; i < n_node_type; ++i) {
    if (valid_edge[node_type][i]) {
      node.max_n_neighbor[i] = neighbor_initial_count;
      node.neighbors[i] = (ClassNeighbor *) calloc(neighbor_initial_count, 
          sizeof(ClassNeighbor));
    }   
  }  

  if (length < MAX_STRING) {
    strcpy(node.name, name);
  } else {
    strncpy(node.name, name, MAX_STRING - 1);
    node.name[MAX_STRING - 1] = '\0';
  }

  ++node_cnt[node_type];
  if (node_cnt[node_type] + 2 >= max_sz_node[node_type]) {
    max_sz_node[node_type] += node_count_inc;
    struct ClassNode *tmp = (struct ClassNode *) realloc(nodes[node_type],
        max_sz_node[node_type] * sizeof(struct ClassNode));
    if (tmp != NULL) {
      nodes[node_type] = tmp;
    } else {
      printf("fail to reallocate\n");
    }
  }
  InsertHashTable(name, node_cnt[node_type] - 1, node_type);
  return node_cnt[node_type] - 1;
}

void UpdateEdgeWeight(int edge_type) {
  long src_id, dst_id;
  int src_type = edge_node_type[edge_type][0];
  int dst_type = edge_node_type[edge_type][1];

  for (long k = 0; k < edge_cnt[edge_type]; ++k) {
    src_id = edges[edge_type][k].src_id;
    dst_id = edges[edge_type][k].dst_id;

    nodes[src_type][src_id].degree -= edges[edge_type][k].weight;
    nodes[dst_type][dst_id].degree -= edges[edge_type][k].weight; 

    edges[edge_type][k].weight *= 
      nodes[src_type][src_id].weight * nodes[dst_type][dst_id].weight;

    nodes[src_type][src_id].degree += edges[edge_type][k].weight;
    nodes[dst_type][dst_id].degree += edges[edge_type][k].weight; 
  }
  //  printf("Finish updating edge weight of edge %s \n", edge_names[edge_type]);
}

void ReadNodeWeight(int node_type) {
  FILE *fin;
  char field[MAX_STRING], str[10000];
  real weight; 
  long node_id, n_lines = 0;

  sprintf(input_node_weight_file, 
      "%s/%s.weights", weight_folder, node_names[node_type]);
  //  printf("%s\n", input_node_weight_file);

  fin = fopen(input_node_weight_file, "rb");
  while (fgets(str, sizeof(str), fin)) ++n_lines;
  fclose(fin);

  fin = fopen(input_node_weight_file, "rb");
  for (long k = 0; k < n_lines; ++k) {
    fscanf(fin, "%s %lf", field, &weight);
    if (prior_power != 1) {
      weight = pow(weight, prior_power);
    }
    node_id = SearchHashTable(field, node_type);
    if (node_id == -1) {
      printf("Invalid node name %s of type %s \n", 
          field, node_names[node_type]);
      exit(1);
    } 
    nodes[node_type][node_id].weight = weight;
  }
  //printf("Finish updating the weight for nodes %s \n", node_names[node_type]);
}

/* Read edges of different types in the network */
void ReadEdgeData(int edge_type) {
  FILE *fin;
  real weight;

  long src_id, dst_id;
  int src_type = edge_node_type[edge_type][0];
  int dst_type = edge_node_type[edge_type][1];
  char str[MAX_SENTENCE], src_name[MAX_STRING], dst_name[MAX_STRING];

  // Get how many number of edges we have
  fin = fopen(train_network_file[edge_type], "rb");

  printf("input: %s \n", train_network_file[edge_type]);
  edge_cnt[edge_type] = 0;
  while (fgets(str, sizeof(str), fin)) ++edge_cnt[edge_type];
  fclose(fin);
  printf("Number of edges (%s): %ld          \n", edge_names[edge_type], edge_cnt[edge_type]);

  edges[edge_type] = (ClassEdge *) malloc(
      edge_cnt[edge_type] * sizeof(ClassEdge));

  fin = fopen(train_network_file[edge_type], "rb");

  for (long k = 0; k < edge_cnt[edge_type]; ++k) {
    fscanf(fin, "%s %s %f", src_name, dst_name, &weight);
    assert(weight > 0);

    src_id = SearchHashTable(src_name, src_type);
    if (src_id == -1) {
      src_id = AddNode(src_name, src_type);
    }
    dst_id = SearchHashTable(dst_name, dst_type);
    if (dst_id == -1) {
      dst_id = AddNode(dst_name, dst_type);
    }
    edges[edge_type][k].src_id = src_id;
    edges[edge_type][k].dst_id = dst_id;
    edges[edge_type][k].weight = weight;

    if (src_type == author_type || src_type == term_type) {
      AddNeighbor(src_type, dst_type, src_id, dst_id, edge_type, edge_id);
      AddNeighbor(dst_type, src_type, dst_id, src_id, edge_type, edge_id);
    }
    // update node degree
    nodes[src_type][src_id].degree += weight;
    nodes[dst_type][dst_id].degree += weight;

    if (k % 50000 == 0) {
      printf("Loading edges : %.3lf%%%c", k / (real)(edge_cnt[edge_type] + 1) * 100, 13);
      fflush(stdout);
    }
  }
  fclose(fin);
}

/* Read the fixed embedding of terms */
void ReadFixEmbedding(int node_type) {
  FILE *fin;
  char str[(dim + 1) * MAX_STRING + 1000];
  long node_id;
  long fix_node_count = node_cnt[node_type], count = 0;
  char *token;

  sprintf(input_fix_embedding_file, 
      "%s/%s.embeddings", embed_folder, node_names[node_type]);

  if (access(input_fix_embedding_file, F_OK) == -1) {
    printf("Can't read the file %s \n", input_fix_embedding_file);
    exit(1);  
  }

  // Get how many number of edges we have
  fin = fopen(input_fix_embedding_file, "rb");

  // printf("debug: finish init\n");
  if (fgets(str, sizeof(str), fin) == NULL) {
    printf("Can't read the file %s \n", input_fix_embedding_file);
    exit(1);  
  }
  while (fgets(str, sizeof(str), fin)) {
    // printf("debug: parse %s\n", str);
    if (count >= fix_node_count) break;
    ++count;

    token = strtok(str, " ");
    node_id = SearchHashTable(token, node_type);
    if (node_id == -1) {
      continue;
    }
    for (int k = 0; k < dim; ++k) {
      token = strtok(NULL, " ");
      if (token == NULL) {
        printf("Error: embedding length dismatch!\n");
        exit(1);
      }
      emb_node[node_type][node_id * dim + k] = atof(token) / 20;
    }
  }
  fclose(fin);
  printf("Embedding of node %s imported!\n", node_names[node_type]);
}

void InitNodeVector(int node_type, real *emb_node) {
  long offset = 0;
  for (long i = 0; i < node_cnt[node_type]; ++i) {
    for (int k = 0; k < dim; ++k) {
      emb_node[offset++] = (gsl_rng_uniform(gsl_r) - 0.5) / dim;
    }
  }
}

/* Initialize the vertex embedding and the context embedding */
void InitVector(){
  printf("Initializing node vector ...                       \n %c", 13);
  fflush(stdout);
  // initialize the target and context embedding of each type of node 
  for (int node_type = 0; node_type < n_node_type; ++node_type) {
    posix_memalign((void **)& emb_node[node_type], 128, 
        node_cnt[node_type] * dim * sizeof(real));
    if (emb_node[node_type] == NULL) {
      printf("Error: memory allocation failed\n");
      exit(1);
    }
    InitNodeVector(node_type, emb_node[node_type]); 
  }
}

// Given a node type, sample a negative node
void InitNegTable(int node_type) {
  real sum = 0, cur_sum = 0, por = 0;
  long vid = 0;
  printf("Initializing negative table for %s ... \t\t\t\t          %c", node_names[node_type], 13);

  fflush(stdout);
  neg_table[node_type] = (long *)malloc(neg_table_size * sizeof(long));

  for (long k = 0; k < node_cnt[node_type]; ++k) {
    sum += pow(nodes[node_type][k].degree, 
        node_sample_power[node_type]);
  }

  for (long k = 0; k < neg_table_size; ++k) {
    if ((real)(k + 1) / neg_table_size > por) {
      cur_sum += pow(nodes[node_type][vid].degree, 
          node_sample_power[node_type]);
      por = cur_sum / sum;
      ++vid;
    }
    neg_table[node_type][k] = vid - 1;
  }
}

void InitEdgeAlias(int edge_type) {
  printf("Initializing alias table for edge %s ...                   %c", 
      edge_names[edge_type], 13);
  real *prob = (real *) calloc(edge_cnt[edge_type], sizeof(real));
  real total_weight = 0;
  for (int i = 0; i < edge_cnt[edge_type]; ++i) {
    total_weight += edges[edge_type][i].weight;
  }
  for (int i = 0; i < edge_cnt[edge_type]; ++i) {
    prob[i] = edges[edge_type][i].weight / total_weight;
  }
  edge_alias[edge_type] = ransampl_alloc(edge_cnt[edge_type]);
  ransampl_set(edge_alias[edge_type], prob);
}

/* Fastly compute sigmoid function */
void InitSigmoidTable() {
  real x;
  printf("Initializing sigmoid table ...                     %c", 13);
  fflush(stdout);
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

inline long SampleNegativeNode(int node_type, gsl_rng * & gsl_r_local) {
  //  return gsl_rng_uniform_int(gsl_r_local, node_cnt[node_type]);
  return neg_table[node_type][
    gsl_rng_uniform_int(gsl_r_local, neg_table_size)];
}

inline long SampleEdge(int edge_type, gsl_rng * & gsl_r_local) {
  return ransampl_draw(edge_alias[edge_type], 
      gsl_rng_uniform(gsl_r_local),
      gsl_rng_uniform(gsl_r_local)); 
}

inline void Update(int src_type, int dst_type, long src_id, 
    long end_id, long *neg_node_ids, real *context_update) {
  long target_id, target_offset, context_offset;
  real f = 0, g = 0, label = 1;
  real decay_target = alpha * beta[dst_type];
  real decay_context = alpha * beta[src_type];

  memset(context_update, 0, dim * sizeof(real));

  context_offset = src_id * dim;
  for (int i = 0; i <= negative_k; ++i) {
    if (i == negative_k) {
      target_id = end_id;
      label = 1; 
    } else {
      target_id = neg_node_ids[i];
      if (target_id == end_id) continue;
      label = 0;
    }
    target_offset = target_id * dim;
    f = 0;
    for (int j = 0; j < dim; j ++) {
      f += emb_node[dst_type][target_offset + j] *
        emb_node[src_type][context_offset + j];
    }
    g = (label - FastSigmoid(f)) * alpha;
    for (int j = 0; j < dim; ++j) {
      context_update[j] += g * emb_node[dst_type][target_offset + j] 
        - decay_context * emb_node[src_type][context_offset + j]; 
      emb_node[dst_type][target_offset + j] += 
        g * emb_node[src_type][context_offset + j] 
        - decay_target * emb_node[dst_type][target_offset + j];
    }
  }

  for (int j = 0; j < dim; ++j) {
    emb_node[src_type][context_offset + j] += context_update[j];
  }

}

void *TrainThread(void *id) {
  long count = 0, last_count = 0;
  long limit = total_samples / num_threads + 2;
  int src_type, dst_type;
  long edge_id, src_id, dst_id;
  long  *neg_node_ids;

  neg_node_ids = (long *) malloc(negative_k * sizeof(long)); 

  gsl_rng * gsl_r_local = gsl_rng_alloc(gsl_T);
  gsl_rng_set(gsl_r_local, (unsigned long int) id); 

  real *err_update = (real *) malloc(dim * sizeof(real));

  real ratio;
  clock_t now;

  while (1)
  {
    // decide when to exist the learning 
    if (count > limit) {
      current_sample += count - last_count; 
      break ;
    }

    // update output information
    if (count - last_count == 10000) {
      current_sample += count - last_count;
      last_count = count;
      ratio = current_sample / (real)(total_samples + 1);
      if (count % 100000 == 0) {
        now=clock();
        printf("%cAlpha: %f  Progress: %.2lf%%  Events/thread/sec: %.2fk",
            13, alpha, ratio * 100,
            current_sample / ((real)(now - start + 1) / (real)CLOCKS_PER_SEC * 1000));
        fflush(stdout);
      }
      alpha = init_alpha * (1 - ratio);
    }
    ++count;

    for (int edge_type = 0; edge_type < n_edge_type; ++edge_type) {
      src_type = edge_node_type[edge_type][0];
      dst_type = edge_node_type[edge_type][1];

      edge_id = SampleEdge(edge_type, gsl_r_local);
      src_id = edges[edge_type][edge_id].src_id; 
      dst_id = edges[edge_type][edge_id].dst_id;

      //printf("%d %d %d %s %s \n", edge_type, src_type, dst_type, nodes[src_type][src_id].name, nodes[dst_type][dst_id].name);

      for (int i = 0; i < negative_k; ++i) {
        neg_node_ids[i] = SampleNegativeNode(dst_type, gsl_r_local);
      }
      Update(src_type, dst_type, src_id, dst_id, neg_node_ids, err_update);
    }
  }
  free(neg_node_ids);
  free(err_update);
  pthread_exit(NULL);
}

// output the embeddings of nodes and the context embedding
void Output() {
  // for each type of nodes, output the embeddings
  char file_name[MAX_STRING];
  FILE *fo;
  long offset;

  // output the embeddings of nodes
  for (int node_type = 0; node_type < n_node_type; ++node_type) {
    if (!output_types[node_type]) continue;
    printf("storing the embedding of nodes %s\n", node_names[node_type]);
    sprintf(file_name, "%s/%s.embeddings", output_folder, node_names[node_type]);
    fo = fopen(file_name, "wb");
    fprintf(fo, "%ld %d\n", node_cnt[node_type], dim);
    offset = 0;
    for (long i = 0; i < node_cnt[node_type]; ++i) {
      fprintf(fo, "%s ", nodes[node_type][i].name);
      for (int k = 0; k < dim; ++k) {
        fprintf(fo, "%lf ", emb_node[node_type][offset++]);
      }
      fprintf(fo, "\n");
    }
    fclose(fo);
  }
}

// query string is delimited by #
void readQuery(char *qString, set::set<long> query) {
  query.clear();
  char delim[] = "#";
  char *token = strtok(name, delim);
  long node_id;
  while (token != NULL) {
    node_id = SearchHashTable(token, term_type);
    if (node_id == -1) {
      node_id = AddNode(token, map_node_type);
    }
    query.insert(node_id);
    token = strtok(NULL, delim);
  }
}

void hitPapers(set::set<long> &query, set::set<long> &paper_set) {
  paper_set.clear();
  for (set::set<long>::iterator it = query.begin(); it != query.end(); ++it) {  
    long term_id = *it;
    ClassNode &node = nodes[term_type][term_id];
    for (int j = 0; j < node.n_neighbor[paper_type]; ++j) {
      paper_set.insert(node.neighbors[paper_type][j]);
    }
  }
}

void nodeExpansion(int src_type, int dst_type, set::set<long> &src_set, set::set<long> &dst_set) {
  dst_set.clear();
  for (set::set<long>::iterator it = src_set.begin(); it != src_set.end(); ++it) {
    long src_id = *it;
    ClassNode &node = nodes[src_type][src_id];
    for (int j = 0; j < node.n_neighbor[dst_type]; ++j) {
      dst_set.insert(node.neighbors[dst_type][j]);
    }
  }
}

void queryExpansion(set::set<long> &paper_set, set::set<long> &query, set::set<long> &new_query) {
  new_query.clear();
  long t_n_edges = 0;
  std::map<long, real> topic_edges;
  for (set::set<long>::iterator it = paper_set.begin(), it != paper_set.end(); ++it) {
    long paper_id = *it;
    class &node = *it;
    for (int j = 0; j < node.n_neighbor[term_type]; ++j) {
      long edge_id = node.neighbors[term_type][j].edge_id;
      real weight = edges[term_paper_edge_type][edge_id].weight;
      topic_edges[edge_id] = weight;
    }
  }

  long * sample_topic_edges = (long *) malloc(topic_edges.size() * sizeof(long));
  real * sample_prob = (real *) malloc(topic_edges.size() * sizeof(real));

  real sum_weight = 0;
  int k = 0;
  for (std::map<long, real>::iterator it = topic_edges.begin(); it != topic_edges.end(); ++it) {
    sample_topic_edges[k] = it->first;
    sample_prob[k] = it->second;
    sum_weight += sample_prob[k];
    k ++;
  }
  topic_edge_alias = ransampl_alloc(topic_edges.size());
  ransampl_set(topic_edge_alias, sample_prob);  
} 

set::set<long> expandDocument(set::set<long> query) {
  long * new_query;
  set::set<long> author_set, paper_set;
  set::set<long> new_query; 
  while (true) {
    hitPapers(query, paper_set);
    nodeExpansion(paper_type, author_type, paper_set, author_set);
    nodeExpansion(author_type, paper_type, author_set, paper_set);
    queryExpansion(paper_set, query, new_query); 
  }
  hitPapers(query, paper_set);
  return paper_set;
}

void TrainModel() {
  gsl_rng_env_setup();
  gsl_T = gsl_rng_rand48;
  gsl_r = gsl_rng_alloc(gsl_T);
  gsl_rng_set(gsl_r, 314159265);


  InitHashTable();
  printf("HashTable Initialized! \n");

  for (int edge_type = 0; edge_type < n_edge_type; ++edge_type) {
    printf("Start to read edges of %s\n", edge_names[edge_type]);  
    ReadEdgeData(edge_type);
  }


  printf("Node types: %d \n", n_node_type);
  for (int i = 0; i < n_node_type; i ++) {
    printf("%s ", node_names[i]);
  }
  printf("\n");

  for (int node_type = 0; node_type < n_node_type; ++node_type) {
    if (node_weight[node_type]) {
      ReadNodeWeight(node_type);
    }
  }

  printf("Edge types: %d \n", n_edge_type);
  for (int i = 0; i < n_edge_type; i ++) {
    printf("%s ", edge_names[i]);
  }
  printf("\n");


  printf("--------------------------------                            \n");
  for (int k = 0; k < n_node_type; ++k) {
    printf("Number of nodes (%s): %ld          \n", node_names[k], node_cnt[k]);
  }
  // map each ege into corresponding
  total_samples = (long) (1000000 * total_samples);
  printf("--------------------------------\n");
  printf("Dimension: %d\n", dim);
  printf("Initial alpha: %.3lf\n", alpha);
  printf("Thread : %d \n", num_threads); 
  printf("--------------------------------\n");

  printf("Load node weight : \n");
  for (int node_type = 0; node_type < n_node_type; ++node_type) {
    printf("\t%s : %s \n", node_names[node_type], 
        node_weight[node_type] ? "Yes":"No");
  }
  printf("\n"); 

  printf("Prior power : %f \n\n", prior_power);

  printf("Update edge weight : \n");
  for (int edge_type = 0; edge_type < n_edge_type; ++edge_type) {
    if (edge_weight[edge_type] && (node_weight[edge_node_type[edge_type][0]] 
          || node_weight[edge_node_type[edge_type][1]])) {
      printf("\t%s : %s \n", edge_names[edge_type], "Yes");
      UpdateEdgeWeight(edge_type);
    } 
    else {
      printf("\t%s : %s \n", edge_names[edge_type], "No");
    }
  }
  printf("\n");

  printf("Output node types:");
  for (int m = 0; m < n_node_type; ++m){
    if (output_types[m]) {
      printf(" %s", node_names[m]);
    }
  }
  printf("\n\n"); 

  InitVector();

  InitSigmoidTable();
  printf("Finish initialization!                \n");

  FILE *fin = fopen(query_file, "rb");
  char c;
  int nQuery = 0;
  while (fgets(str, sizeof(str), fin)) ++nQuery;
  fclose();

  fin = fopen(query_file, "rb");
  set::set<long> papers, query;
  char query_string[MAX_SENTENCE];
  for (int q = 0; q < nQuery; q++) {
    int pos = 0;
    do {
      c = fgetc(fin);
      if (c == EOF || c == '\n') break;
      else if (pos < MAX_SENTENCE - 1) query_string[pos++] = (char) c; 
    }
    query_string[pos] = 0;
    readQuery(query_string, query); 
    papers.clear();
    papers = expandDocument(query);

  }


  struct timeval t1, t2;
  gettimeofday(&t1, NULL);
  start = clock();
  pthread_t *pt = (pthread_t *)malloc((num_threads) * sizeof(pthread_t));

  for (long a = 0; a < num_threads; ++a) {
    pthread_create(&pt[a], NULL, TrainThread, (void *)a);
  }
  for (int a = 0; a < num_threads; ++a) { 
    pthread_join(pt[a], NULL);
  }

  gettimeofday(&t2, NULL);
  printf("\nTotal optimization time: %.2lf minitues\n", (real)(t2.tv_sec - t1.tv_sec) / 60);
  Output();
}


int ArgPos(char *str, int argc, char **argv) {
  for (int a = 0; a < argc; ++a) {
    if (!strcmp(str, argv[a])) {
      if (a == argc - 1) {
        printf("Argument missing for %s\n", str);
        exit(1);
      }
      return a;
    }
  }
  return -1;
}

int main(int argc, char **argv) {
  int i, j, k;
  char str[MAX_SENTENCE], source[MAX_SENTENCE], dest[MAX_SENTENCE];
  strcpy(output_folder, "output");
  strcpy(input_folder, "data");
  InitSigmoidTable();

  if (argc == 1) {
    printf("\t leef: Local Embedding for Expert Finding\n");
    printf("Options:"); 
    printf("\tPlease specify the parameter file!\n");
    printf("\t-para <file> \n");
    printf("\t\tProvide the parameter file on edges\n");
    printf("\t-size <int>\n");
    printf("\t\tSet dimension of vertex embeddings; default is 200\n");
    printf("\t-scoring <int>\n");
    printf("\t\tScoring function, 0: complete element-wise product,"
        "1: complete pairwise inner product, 2: pairwise inner product with central type\n");
    printf("\t-iter <int>\n");
    printf("\t\tSet the number of training samples as the number of iterations of number of edges\n");
    printf("\t-tthread <int>\n");
    printf("\t\tUse <int> threads for tensor updating(default 1)\n");
    printf("\t-wthread <int>\n");
    printf("\t\tUse <int> threads for word2vec updating(default 1)\n");
    printf("\t-negative <int>\n");
    printf("\t\tSample <int> negative samples for word2vec updating(default 1)\n");
    printf("\t-alpha <float>\n");
    printf("\t\tSet the starting learning rate; default is 0.025\n");
    printf("\t-input input folder ...\n");
    printf("\t\tSet the folder data which read data\n");
    printf("\t-output output folder ...\n");
    printf("\t\tSet the folder to which output data\n");
    return 0;
  }

  // global parameters shared across all the edges
  if ((i = ArgPos((char *) "-size", argc, argv)) > 0)
    dim = atoi(argv[i + 1]);
  if ((i = ArgPos((char *) "-iter", argc, argv)) > 0)
    total_samples = atoi(argv[i + 1]);
  if ((i = ArgPos((char *) "-alpha", argc, argv)) > 0)
    init_alpha = atof(argv[i + 1]);
  if ((i = ArgPos((char *) "-thread", argc, argv)) > 0) {
    num_threads = atoi(argv[i + 1]);
  }
  if ((i = ArgPos((char *) "-negative", argc, argv)) > 0) {
    negative_k = atoi(argv[i + 1]);
  }

  for (i = 0; i < n_node_type; ++i) {
    for (j = 0; j < n_node_type; ++j) {
      valid_edge[i][j] = false;
    } 
  }

  if ((i = ArgPos((char *) "-n_node", argc, argv)) > 0) {
    n_node_type = atoi(argv[i + 1]);
  }

  for (int i = 0; i < n_node_type; ++i) {
    nodes[i] =(struct ClassNode *) calloc(node_count_inc, 
        sizeof(struct ClassNode));
    max_sz_node[i] = node_count_inc;
    node_sample_power[i] = sample_power;
  }

  if ((i = ArgPos((char *) "-nodes", argc, argv)) > 0) {
    for (j = 0; j < n_node_type; ++j) {
      strcpy(node_names[j], argv[i + j + 1]);
      if (!strcmp(node_names[j], "author")) {
        author_type = j;
      } else if (!strcmp(node_names[j], "term")) {
        term_type = j;
      } else if (!strcmp(node_names[j], "paper")) {
        paper_type = j;
      }
    }
  }

  if ((i = ArgPos((char *) "-n_edge", argc, argv)) > 0) {
    n_edge_type = atoi(argv[i + 1]);
  }

  if ((i = ArgPos((char *) "-output_folder", argc, argv)) > 0)
    strcpy(output_folder, argv[i + 1]);
  if ((i = ArgPos((char *) "-input_folder", argc, argv)) > 0)
    strcpy(input_folder, argv[i + 1]);
  if ((i = ArgPos((char *) "-embed_folder", argc, argv)) > 0)
    strcpy(embed_folder, argv[i + 1]);
  if ((i = ArgPos((char *) "-weight_folder", argc, argv)) > 0)
    strcpy(weight_folder, argv[i + 1]);

  if ((i = ArgPos((char *) "-edges", argc, argv)) > 0) {
    for (j = 0; j < n_edge_type; ++j) {
      strcpy(edge_names[j], argv[i + j + 1]);
      sprintf(train_network_file[j], "%s/%s.net", input_folder, edge_names[j]);
      printf("Input %d: %s\n", j, train_network_file[j]); 
      strcpy(edge_names[j], argv[i + 1 + j]); 
      strcpy(str, edge_names[j]);  
      int pch = strchr(str, '_') - str;
      str[pch] = '\0';
      strcpy(source, str);
      strcpy(dest, &str[pch + 1]);
      for (k = 0; k < n_node_type; ++k) {
        if (strcmp(source, node_names[k]) == 0) {
          edge_node_type[j][0] = k;
        } else if (strcmp(dest, node_names[k]) == 0) {
          edge_node_type[j][1] = k;
        }       
      }
      if (edge_node_type[j][0] == term_type && edge_node_type[j][1] == paper_type) {
        term_paper_edge_type = j;
      }
      valid_edge[edge_node_type[j][0]][edge_node_type[j][1]] = true;
      valid_edge[edge_node_type[j][1]][edge_node_type[j][0]] = true;
    }
  }


  // the regularization parameter for the embeddings 
  if ((i = ArgPos((char *) "-beta", argc, argv)) >= 0) {
    for (int j = 0; j < n_node_type; ++j) {
      beta[j] = atof(argv[i + 1 + j]);
    }
  }

  if ((i = ArgPos((char *) "-prior_power", argc, argv)) >= 0) {
    prior_power = atof(argv[i + 1]);
  }

  if ((i = ArgPos((char *) "-sample_power", argc, argv)) >= 0) {
    for (int j = 0; j < n_node_type; ++j) {
      node_sample_power[j] = atof(argv[i + 1 + j]);
    }
  }

  if ((i = ArgPos((char *) "-choose_output", argc, argv)) >= 0) {
    for (int j = 0; j < n_node_type; ++j) {
      output_types[j] = (argv[i + 1][j] == '1');
    }
  }

  if ((i = ArgPos((char *) "-load_embed", argc, argv)) >= 0) {
    printf("Loading embeddings is disabled..\n");
    for (int j = 0; j < n_node_type; ++j) {
      if (argv[i + 1][j] == '1') {
        load_types[j] = true; 
      }
    }
  }

  if ((i = ArgPos((char *) "-load_weight", argc, argv)) >= 0) {
    for (int j = 0; j < n_node_type; ++j) {
      if (argv[i + 1][j] == '1') {
        node_weight[j] = true; 
      }
    }
  }

  if ((i = ArgPos((char *) "-edge_weight", argc, argv)) >= 0) {
    for (int j = 0; j < n_node_type; ++j) {
      if (argv[i + 1][j] == '1') {
        edge_weight[j] = true; 
      } else {
        edge_weight[j] = false;
      }
    }
  }

  if ((i = ArgPos((char *) "-query_file", argc, argv)) >= 0) {
    strcpy(query_file, argv[i + 1]);
  }

  alpha = init_alpha;
  TrainModel();
  return 0;
}
