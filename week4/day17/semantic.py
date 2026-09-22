import warnings
# Suppress the deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

# ---------------------------------------------------------
# 1. Sample text: 3 distinct topics with no line breaks
# ---------------------------------------------------------
text = (
    "Jupiter is the largest planet in our solar system. "
    "It has a massive persistent storm known as the Great Red Spot. "
    "Europa, one of its moons, may hold a liquid ocean beneath its icy crust. "
    "Baking authentic Neapolitan pizza requires flour with high protein content. "
    "The oven must reach temperatures of at least 450 degrees Celsius. "
    "San Marzano tomatoes provide the ideal acidity for the sauce. "
    "In professional tennis, a player must win six games to take a set. "
    "Grand Slam tournaments are played across grass, clay, and hard court surfaces. "
    "Serving at high speeds gives players a significant tactical advantage."
)

# ---------------------------------------------------------
# 2. Free local embedding model (runs completely offline)
# ---------------------------------------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=85,
)

chunks = splitter.split_text(text)

# ---------------------------------------------------------
# 3. Print Results
# ---------------------------------------------------------
print(f"\nTotal Semantic Chunks Created: {len(chunks)}")
for i, chunk in enumerate(chunks, 1):
    print(f"\n--- Chunk {i} ---")
    print(chunk.strip())