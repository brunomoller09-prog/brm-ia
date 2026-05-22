import os
import gradio as gr
from groq import Groq
from fastapi import FastAPI
import uvicorn

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    with open("dados.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
except FileNotFoundError:
    conhecimento = "Nenhuma base de conhecimento carregada."
    print("⚠️ Arquivo dados.txt não encontrado.")

def responder(mensagem: str, historico: list) -> str:
    try:
        mensagens = [
            {
                "role": "system",
                "content": f"Você é a BRM IA.\nUse essas informações:\n{conhecimento}"
            }
        ]

        for humano, assistente in (historico or []):
            mensagens.append({"role": "user", "content": humano})
            mensagens.append({"role": "assistant", "content": assistente})

        mensagens.append({"role": "user", "content": mensagem})

        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens,
            max_tokens=1024,
            temperature=0.7
        )
        return resposta.choices[0].message.content

    except Exception as e:
        return f"Erro: {str(e)}"


with gr.Blocks(title="BRM IA") as demo:
    gr.Markdown("# 🤖 BRM IA")
    gr.Markdown("Assistente virtual da BRM. Tire suas dúvidas abaixo.")

    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(
        placeholder="Digite sua mensagem aqui...",
        show_label=False
    )
    limpar = gr.Button("🗑️ Limpar conversa")

    def interact(mensagem: str, historico: list):
        if not mensagem.strip():
            return "", historico
        if historico is None:
            historico = []
        resposta = responder(mensagem, historico)
        historico.append((mensagem, resposta))
        return "", historico

    msg.submit(interact, [msg, chatbot], [msg, chatbot])
    limpar.click(lambda: ([], ""), outputs=[chatbot, msg])


app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
