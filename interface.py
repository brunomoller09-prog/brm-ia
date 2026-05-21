import gradio as gr
from groq import Groq
import os

# 🔑 pega a chave do Railway
client = Groq(api_key=os.getenv("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"))

# 📄 carrega sua base
with open("dados.txt", "r", encoding="utf-8") as f:
    conhecimento = f.read()


def responder(mensagem, historico):
    try:
        mensagens = []

        mensagens.append({
            "role": "system",
            "content": f"""
Você é a BRM IA, especialista nos processos da empresa.

Use as informações abaixo:

{conhecimento}

Responda sempre em português, de forma profissional.
Se não souber, diga: "não tenho essa informação no processo".
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
        return f"Erro: {str(e)}"


# ✅ Interface simples e compatível com Railway
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 BRM IA")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Digite sua pergunta aqui...")

    def responder_ui(mensagem, historico):
        resposta = responder(mensagem, historico)
        historico = historico + [(mensagem, resposta)]
        return "", historico

    msg.submit(responder_ui, [msg, chatbot], [msg, chatbot])


# ✅ porta dinâmica (OBRIGATÓRIO pro Railway)
port = int(os.environ.get("PORT", 8080))

demo.launch(
    server_name="0.0.0.0",
    server_port=port,
    share=False,
    show_error=True,
    prevent_thread_lock=True
)

