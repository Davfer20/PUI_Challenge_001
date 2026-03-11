# PUI_Challenge_001

Due to time constraints, I did not implement any ui features for this challenge. Instead, the queries that demonstrate the semantic search functionality can be directly added to the queries list in the main script called "queries". When the program runs, these queries are automatically executed and the results are printed in the console.

Since this was my first time working with Elasticsearch in practice, I focused on implementing the core functionality and the todos (generating embeddings, and indexing the resulting chunks into Elasticsearch). More advanced optimizations such as batch indexing and performance tuning were not implemented in this version. These are areas I would explore and improve in a future iteration.

To build the solution, I reviewed several resources and documentation related to Elasticsearch, semantic search, and sentence embeddings. The following references were used during the research and development process.

Stack Overflow. (2013, December 3). How do I remove all non-ASCII characters with regex and notepad? https://stackoverflow.com/questions/20889996/how-do-i-remove-all-non-ascii-characters-with-regex-and-notepad

Logz.io. (2021). Elasticsearch mapping: The definitive guide. https://logz.io/blog/elasticsearch-mapping/

Elastic. (2021). Text embedding and semantic search. Elastic Docs. https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-text-emb-vector-search-example

Vestal, J. (2023, November 17). Vector search & kNN implementation guide - API edition. Elasticsearch Labs. https://www.elastic.co/search-labs/blog/vector-search-implementation-guide-api-edition