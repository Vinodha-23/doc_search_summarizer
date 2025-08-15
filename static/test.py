import pickle
with open("docs.pkl", "rb") as f:
    docs = pickle.load(f)
print(docs[:2])
