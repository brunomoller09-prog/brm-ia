import os
import gradio as gr
from groq import Groq
from fastapi import FastAPI
import uvicorn

# ✅ CORRETO AQUI
client = Groq(api_key=os.getenv("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"))

with open("dados.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()

def responder(mensagem, historico):
    try:
        mensagens = [
            {
                "role": "system",
                "content": f"""Você é a BRM IA.

Use essas informações:
{conhecimento}
"""
            },
            {
                "role": "user",
                "content": mensagem
            }
        ]

        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens
        )

        return resposta.choices[0].message.content

    except Exception as e:
        return f"Erro: {str(e)}"


with gr.Blocks() as demo:
    gr.Markdown("# 🤖 BRM IA")

    chatbot = gr.Chatbot()
    msg = gr.Textbox()

    def interact(mensagem, historico):
        if historico is None:
            historico = []

        resposta = responder(mensagem, historico)

        historico.append((mensagem, resposta))
        return "", historico

    msg.submit(interact, [msg, chatbot], [msg, chatbot])


app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
