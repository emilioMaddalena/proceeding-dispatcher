import ollama

response = ollama.chat(
    model="llama2-uncensored",
    messages=[
        {
            "role": "user",
            "content": "Why is the sky blue?",
        },
    ],
)
print(response["message"]["content"])
