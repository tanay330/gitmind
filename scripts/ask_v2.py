import sys

from gitmind.llm.answer import answer_question

repo_id = sys.argv[1]
question = " ".join(sys.argv[2:])

result = answer_question(question, repo_id)
print(result["answer"])
print("\nSources:")
for source in result["sources"]:
    print(f"  [{source['number']}] {source['path']}:{source['lines']}  {source['symbol']}")