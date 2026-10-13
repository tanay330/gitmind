from groq import Groq
from gitmind.config import settings
from gitmind.llm.prompts import SYSTEM_PROMPT
from gitmind.retrieval.router import search

groq_client=Groq(api_key=settings.groq_api_key)

def generate_answer(question:str,context:str)-> str:
    prompt = f"""
    Answer the question using only the information provided below.
    
    Context:
    {context}
    
    Question:
    {question}
    
    If the answer is not present in the context, say:
    "I don't know based on the provided information."
    """
   
    messages=[ {
        "role": "system",
        "content": SYSTEM_PROMPT
    },
    {
        "role": "user",
        "content": prompt
    }]
    response = groq_client.chat.completions.create(model="openai/gpt-oss-120b",messages=messages) 
    answer = response.choices[0].message.content
    return answer
        
def ask_gitmind(question: str) -> str:
    results = search(question, top_k=8)  
    context="\n\n".join(f"File: {result.payload['path']}\nContent: {result.payload['text']}" for result in results)    
    return generate_answer(question,context)
    
          
    
