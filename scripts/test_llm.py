from gitmind.llm.client import generate_answer

context = """
File: src/main.py
Content: def create_app():
    return FastAPI()
"""

question = "Which framework does this code use?"

answer = generate_answer(question, context)

print("Answer:", answer)