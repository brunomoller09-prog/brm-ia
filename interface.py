import os
import gradio as gr
from groq import Groq
from fastapi import FastAPI
import uvicorn

# ✅ cliente Groq (usa variável do Railway)
client = Groq(api_key=os.getenv("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"))

# ✅ carregar base de dados
with open("dados.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()


# ✅ função que conversa com a IA
def responder(mensagem, historico):
    try:
        mensagens = [
            {
                "role": "system",
                "content": f"""
Você é a BRM IA, especialista nos processos da empresa.

Use apenas essas informações:

{conhecimento}

Se não souber, diga:
"não tenho essa informação no processo"
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


# ✅ INTERFACE (VERSÃO COMPATÍVEL COM GRADIO)
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 BRM IA")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Digite sua pergunta...")

    def interact(mensagem, historico):
        if historico is None:
            historico = []

        resposta = responder(mensagem, historico)

        # ✅ formato correto (tupla) → evita erro
        historico.append((mensagem, resposta))

        return "", historico

    msg.submit(interact, [msg, chatbot], [msg, chatbot])


# ✅ SERVIDOR (OBRIGATÓRIO pro Railway)
app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")


# ✅ RODAR APP
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
``
