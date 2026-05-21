import gradio as gr
from groq import Groq
import os

# ✅ pega a chave do Railway (Variables)
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
Você é a BRM IA, especialista nos processos da empresa.

Base:
{conhecimento}

Responda profissionalmente, em português.
Se não souber, diga que não tem a informação.
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
        return f"Erro na aplicação: {str(e)}"


# ✅ interface
demo = gr.ChatInterface(
    fn=responder,
    title="🤖 BRM IA",
    description="Assistente de Processos"
)


# ✅ porta dinâmica do Railway
port = int(os.environ.get("PORT", 7860))

demo.launch(
    server_name="0.0.0.0",
    server_port=port,
    show_error=True
)
