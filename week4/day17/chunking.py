from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

# ----------------------------------------------------------------------
# Sample Text (Mystery Story)
# ----------------------------------------------------------------------
text = """The detective entered the abandoned house just before midnight. The rooms were silent, and the windows were covered with dust. On the table, he found a bloody key.

The man who did the crime was John. Nobody in the village trusted him, but he had disappeared three days before the murder. The detective immediately realized this was an inside job.

The next morning, the detective returned to the house. Behind a loose brick, he discovered a photograph of John standing beside the victim. This finally connected all the clues together."""


# =========================================================
# 1. FIXED-SIZE CHUNKING
# Splits strictly at character count boundaries (can split words).
# =========================================================
fixed = CharacterTextSplitter(
    separator="",
    chunk_size=100,
    chunk_overlap=0,
)

print("\n========== 1. FIXED SIZE ==========")
for i, chunk in enumerate(fixed.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("-" * 25)


# =========================================================
# 2. PARAGRAPH CHUNKING
# Splits strictly on empty lines / paragraph breaks (\n\n).
# =========================================================
paragraph = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=50,
    chunk_overlap=0,
)

print("\n========== 2. PARAGRAPH CHUNKING ==========")
for i, chunk in enumerate(paragraph.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("-" * 25)


# =========================================================
# 3. RECURSIVE CHARACTER CHUNKING (Industry Standard)
# Tries "\n\n", then "\n", then " ", then "" to avoid breaking words/sentences.
# =========================================================
recursive = RecursiveCharacterTextSplitter(
    chunk_size=120,
    chunk_overlap=0,
    separators=["\n\n", "\n", " ", ""],
)

print("\n========== 3. RECURSIVE CHUNKING ==========")
for i, chunk in enumerate(recursive.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("-" * 25)


# =========================================================
# 4. RECURSIVE CHUNKING WITH OVERLAP
# Keeps overlapping characters to retain context between cuts.
# =========================================================
recursive_overlap = RecursiveCharacterTextSplitter(
    chunk_size=120,
    chunk_overlap=30,  # 30-character carryover from previous chunk
    separators=["\n\n", "\n", " ", ""],
)

print("\n========== 4. RECURSIVE WITH OVERLAP ==========")
for i, chunk in enumerate(recursive_overlap.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("-" * 25)