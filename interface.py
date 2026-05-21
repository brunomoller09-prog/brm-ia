import os
import gradio as gr
from groq import Groq
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

# ✅ cliente Groq
client = Groq(api_key=os.getenv("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"))

# ✅ carregar base
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


# ✅ interface gradio
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 BRM IA")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Digite sua pergunta...")

    def interact(mensagem, historico):
        resposta = responder(mensagem, historico)
        historico = historico + [(mensagem, resposta)]
        return "", historico

    msg.submit(interact, [msg, chatbot], [msg, chatbot])


# ✅ servidor FastAPI (ESSA PARTE RESOLVE O BUG)
app = FastAPI()

@app.get("/")
def read_root():
    return RedirectResponse(url="/gradio")


app = gr.mount_gradio_app(app, demo, path="/gradio")


# ✅ iniciar servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
