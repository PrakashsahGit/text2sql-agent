import os
import json
import hashlib

import faiss
import numpy as np

from sentence_transformers import (
    SentenceTransformer
)

from retrievers.embed_schema import (
    schema_to_documents
)

from database.schema_loader import (
    load_schema
)


# ===================================
# PATHS
# ===================================
INDEX_PATH = (
    "retrievers/entity_index.bin"
)

DOCS_PATH = (
    "retrievers/entity_docs.json"
)

HASH_PATH = (
    "retrievers/entity_hash.txt"
)


# ===================================
# EMBEDDING MODEL
# ===================================
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ===================================
# GENERATE SCHEMA HASH
# ===================================
def generate_schema_hash():

    schema = load_schema()

    schema_json = json.dumps(

        schema,

        sort_keys=True
    )

    schema_hash = hashlib.md5(

        schema_json.encode()

    ).hexdigest()

    return schema_hash


# ===================================
# BUILD / LOAD VECTOR STORE
# ===================================
def build_vector_store():

    current_hash = (
        generate_schema_hash()
    )

    stored_hash = None


    # ===================================
    # LOAD STORED HASH
    # ===================================
    if os.path.exists(HASH_PATH):

        with open(HASH_PATH, "r") as f:

            stored_hash = (
                f.read().strip()
            )


    # ===================================
    # CHECK REBUILD
    # ===================================
    rebuild_required = (

        not os.path.exists(
            INDEX_PATH
        )

        or

        not os.path.exists(
            DOCS_PATH
        )

        or

        current_hash != stored_hash
    )


    # ===================================
    # LOAD EXISTING INDEX
    # ===================================
    if not rebuild_required:

        print(
            "\n⚡ Loading entity FAISS index..."
        )

        index = faiss.read_index(
            INDEX_PATH
        )

        with open(DOCS_PATH, "r") as f:

            documents = json.load(f)


        print(
            "✅ Entity FAISS index loaded"
        )

        return index, documents


    # ===================================
    # REBUILD INDEX
    # ===================================
    print(
        "\n🧠 Schema changed — "
        "rebuilding entity FAISS index..."
    )


    # ===================================
    # ENTITY DOCUMENTS
    # ===================================
    documents = schema_to_documents()


    texts = [

        doc["text"]

        for doc in documents
    ]


    # ===================================
    # CREATE EMBEDDINGS
    # ===================================
    embeddings = embedding_model.encode(
        texts
    )

    embeddings = np.array(
        embeddings
    ).astype("float32")


    # ===================================
    # CREATE FAISS INDEX
    # ===================================
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(embeddings)


    # ===================================
    # SAVE INDEX
    # ===================================
    faiss.write_index(

        index,

        INDEX_PATH
    )


    # ===================================
    # SAVE DOCUMENTS
    # ===================================
    with open(DOCS_PATH, "w") as f:

        json.dump(
            documents,
            f,
            indent=2
        )


    # ===================================
    # SAVE HASH
    # ===================================
    with open(HASH_PATH, "w") as f:

        f.write(current_hash)


    print(
        "✅ Entity FAISS index rebuilt"
    )


    return index, documents