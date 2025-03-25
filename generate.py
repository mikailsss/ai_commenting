from openai import OpenAI
api_key = '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'# апи кей можете юзать, он мне не нужен
from config import prompt


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)
async def create_request(context_message):
    completion = client.chat.completions.create(
    model="deepseek/deepseek-chat",
    messages=[
        {
        "role": "user",
        "content": f"{prompt}\n\nСообщение поста (для контекста):\n{context_message}"
        }
    ]
    )
    return completion.choices[0].message.content


