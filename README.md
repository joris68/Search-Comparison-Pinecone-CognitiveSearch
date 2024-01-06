# Search-Comparison-Pinecone-CognitiveSearch

This is an attempt to compare the performance between two different Knowledge-Retrieval Systems based on the exactly same Knowledge Base.
Check out the  Knowledge-Retrieval Cheat cheet from Reddis on the basic Architecture of these systems.

1. System: Knowledge Retrieval using a Pinecone Vectordatabase
2. System Azure Cognitive Search
Inboth systems there are the exact same Chunks.
Textsplitting, chunking was done with the 'cl100k_base' tokenizer.
embedding via the "text-embedding-ada-002" and the OpenAI-API.

The Pinecone Knowledge-Retrieval System based on the Pinecone Vectordatabase and the pure Vector-Similarity-Search. Since the embedding API from OpenAI
standardizes the Vector to the lenght 1, Cosine Similarity and Euclidean distance yield the same results given the same query vector.

Azure Congitive Search uses semantic search for their Search results. This is based on vector search as well as keyword search.
https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview, reference Hybrid Search documentation for further details.

Our aim is to compare the performance of these Systems with each other. In terms of how similar their search results are
and which result actually give better information based on the question asked.

The Knowledge base consists of textual podcast Data.
Different textfiles represent different Epsiodes of the Podcast.

Usually textfiles are chunked into 15 to 25 different chunks and are inserted in the Search Indexes.


We will do this in several steps:

1. We will calculate the intersection of episodes between the k results both systems give back
2. We will calculate the intersection between episodes and chunks between the results of both systems, this is a subset of 1.
3. The similarity of the order these are given back, [0, 0.25, 0.5, 0.75, 1] would be possible values for k = 4 chunks.
    0 meaning not the same order at all, 0.25 that there is an equal chunk on any rank , and so on

Performance:
We used ChatGPT as a performance measure. We will ask him whether he thinks if the answer chunks from Pinecone or the answer chunks from Azure cognitive Search hold more information in order to answer the question. He will rank it in on a scale from [1..5].

After asking 100 questions for the Podcast we came to following conclusion:

Same chunks in the aswer:
AVG: 0,9 (chunks)
STD 0,76 (chunks)

Only in 2 out of 100 questions, they ranked chunks similarly.

How chatGPT reviewed performance:

AVG Pinecone: 1,5
AVG Azure Search : 4,05

(This is actually a tremendous difference, is ChatGPT biased towards Microsoft products???? ;) )

So Azure Search is better? Maybe. But also a lot more costly. Check out the pricing overview I made for different scenarios. Unofortunately this is in German :(.

For further notice, and a blog Post from Microsoft on this Issue, please check out:

https://techcommunity.microsoft.com/t5/ai-azure-ai-services-blog/azure-cognitive-search-outperforming-vector-search-with-hybrid/ba-p/3929167