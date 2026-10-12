from gitmind.llm.client import ask_gitmind
from gitmind.retrieval.router import search

question = "How does GitMind fetch, chunk, embed, and store GitHub repository files?"

answer = ask_gitmind(question)

print("Question:", question)
print("Answer:", answer)


"""question = "How does GitMind fetch and process GitHub repository files?"

results = search(question, top_k=3)

for result in results:
    print("Score:", result.score)
    print("File:", result.payload["path"])
    print("Content:", result.payload["text"])
    print("-" * 50)"""