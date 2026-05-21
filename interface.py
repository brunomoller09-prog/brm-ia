import gradio as gr
from groq import Groq
import os

client = Groq(api_key="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")

with open("dados.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()

def responder(mensagem, historico):
    try:
        mensagens = []

        mensagens.append({
            "role": "system",
            "content": f"""
Você é a BRM IA.

Base:
{conhecimento}
"""
        })

        mensagens.append({
            "role": "user",
            "content": mensagem
        })

        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens
        )

        return resposta.choices[0].message.content

    except Exception as e:
        return str(e)

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 BRM IA")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Digite sua pergunta aqui...")

    def interact(message, history):
        response = responder(message, history)
        history = history + [(message, response)]
        return "", history

    msg.submit(interact, [msg, chatbot], [msg, chatbot])

import os

port = int(os.environ.get("PORT", 8080))

demo.launch(
    server_name="0.0.0.0",
    server_port=port
)

