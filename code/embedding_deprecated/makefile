CC = /usr/bin/g++
CFLAGS = -lgsl -lgslcblas -lm -march=native -DHAVE_INLINE -pthread -Wall -O3 -funroll-loops -Wno-unused-result

all: query_search word2vec 

leef : ransampl.o leef.o
	$(CC) -o leef ransampl.o leef.o $(CFLAGS) 
	
leef.o : leef.c ransampl.o ransampl.h 
	$(CC) -c leef.c $(CFLAGS) 
	
ransampl.o : ransampl.c
	$(CC) -c ransampl.c $(CFLAGS)
	
query_search: query_search.c 
	$(CC) query_search.c -o query_search $(CFLAGS)

word2vec : word2vec.c
	$(CC) word2vec.c -o word2vec $(CFLAGS)

clean:
	rm -rf leef *.o query_search word2vec
