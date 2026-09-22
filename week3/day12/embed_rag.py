import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer

#cosine similarity is a measure of similarity between two non-zero vectors of an inner product space that measures the cosine of the angle between them. The cosine of 0° is 1, and it is less than 1 for any other angle. It is thus a judgment of orientation and not magnitude: two vectors with the same orientation have a cosine similarity of 1, two vectors at 90° have a similarity of 0, and two vectors diametrically opposed have a similarity of -1, independent of their magnitude. Range is [-1,1]. It is often used to measure document similarity in text analysis.


#Syntax of cosine similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


model = SentenceTransformer("all-MiniLM-L6-v2") #384-vector model for embedding
#there are other models like "all-MiniLM-L12-v2" (768-vector model) and "all-mpnet-base-v2" (768-vector model) etc which are more accurate but slower
text = "Machine learning is fun."

embedding=model.encode(text)
print(embedding.shape)
print(embedding[:10])

t1="There are 24 paid leaves"
t2="Company is giving 24 paid leaves to employees"

v1=model.encode(t1)
v2=model.encode(t2)
print(cosine_similarity(v1, v2))