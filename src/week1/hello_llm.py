import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Load environment variables from .env file

client = OpenAI()

def ask(question: str) -> str:
  """Send one question to LLM and return the answer text."""
  resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {"role": "system", "content": "You are concise."},
      {"role": "user", "content": question}
    ],
    temperature=0.3,
  )
  return resp.choices[0].message.content

if __name__ == "__main__":
  q = " ".join(sys.argv[1:]) or "Say hello in one sentence"
  print(ask(q))