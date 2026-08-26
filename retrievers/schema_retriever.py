from sentence_transformers import (
    SentenceTransformer
)

import numpy as np

from retrievers.vector_store import (
    build_vector_store
)


# ===================================
# EMBEDDING MODEL
# ===================================
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ===================================
# LOAD VECTOR STORE
# ===================================
index, documents = build_vector_store()


# ===================================
# RETRIEVE RELEVANT ENTITIES
# ===================================
def retrieve_relevant_entities(

    query,

    top_k=25
):


    # ===================================
    # QUERY EMBEDDING
    # ===================================
    query_embedding = (
        embedding_model.encode([query])
    )

    query_embedding = np.array(
        query_embedding
    ).astype("float32")


    # ===================================
    # VECTOR SEARCH
    # ===================================
    distances, indices = index.search(

        query_embedding,

        top_k
    )


    # ===================================
    # COLLECT RESULTS
    # ===================================
    results = []

    seen_entities = set()


    for idx in indices[0]:

        doc = documents[idx]

        entity = doc["entity"]


        # ===================================
        # REMOVE DUPLICATES
        # ===================================
        if entity in seen_entities:

            continue


        seen_entities.add(entity)


        results.append({

            "entity":
            doc["entity"],

            "table":
            doc["table"],

            "column":
            doc["column"],

            "type":
            doc["type"],

            "text":
            doc["text"]
        })


    return results