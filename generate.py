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


