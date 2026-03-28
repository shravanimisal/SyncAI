from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# example knowledge documents
documents = [

"Company meetings are scheduled between 9 AM and 5 PM",

"Customer support emails must always be polite",

"Meeting confirmation emails must include agenda",

"Support team replies within 24 hours"

]

# embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# create vector database
vector_store = Chroma.from_texts(
    documents,
    embedding_model
)


def retrieve_context(query):

    results = vector_store.similarity_search(query, k=2)

    return [doc.page_content for doc in results]