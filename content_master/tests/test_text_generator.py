#llama = 'LA-add624d4f1c84c449834f60c77da9262e13319181a7348eb8f288dfc01328ce8'


# from openai import OpenAI

# base_url = "https://api.aimlapi.com/v1"
# api_key = "fe6b86046fbe478aa04354988af815a9 "
# system_prompt = "You are a travel agent. Be descriptive and helpful."
# user_prompt = "Tell me about San Francisco"

# api = OpenAI(api_key=api_key, base_url=base_url)


# def main():
#     completion = api.chat.completions.create(
#         model="mistralai/Mistral-7B-Instruct-v0.2",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#         temperature=0.7,
#         max_tokens=256,
#     )

#     response = completion.choices[0].message.content

#     print("User:", user_prompt)
#     print("AI:", response)

# if __name__ == "__main__":
#     main()
from openai import OpenAI
from os import getenv

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key='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'
)

completion = client.chat.completions.create(
 # model="mattshumer/reflection-70b:free",
 # model="google/gemini-flash-1.5",
 model="nousresearch/hermes-3-llama-3.1-405b",
  
  messages=[
    {
      "role": "user",
      "content": "What do you know about algebraic structure?",
    },
  ],
)
print(completion.choices[0].message.content)