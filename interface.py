import os
import gradio as gr
from groq import Groq
from fastapi import FastAPI
import uvicorn

# ✅ usa variável do Railway
client = Groq(api_key=os.getenv("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"))

# ✅ lê seu arquivo
with open("dados.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()

def responder(mensagem, historico):
    try:
        mensagens = [
            {
                "role": "system",
                "content": f"""
Você é a BRM IA.

Use apenas essas informações:
{conhecimento}

Se não souber, diga: não tenho essa informação no processo.
"""
            },
            {"role": "user", "content": mensagem}
        ]

        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens
        )

        return resposta.choices[0].message.content

    except Exception as e:
        return f"Erro: {str(e)}"

# ✅ interface
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 BRM IA")
    
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Digite sua pergunta...")
    
    def interact(mensagem, historico):
        resposta = responder(mensagem, historico)
        historico = historico + [(mensagem, resposta)]
        return "", historico
    
    msg.submit(interact, [msg, chatbot], [msg, chatbot])

# ✅ servidor REAL (resolve erro do Railway)
app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")

# ✅ execução
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
