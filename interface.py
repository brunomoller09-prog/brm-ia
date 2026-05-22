import os
import gradio as gr
from groq import Groq
from fastapi import FastAPI
import uvicorn

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SENHA = os.getenv("SENHA_BRM", "brm2024")

try:
    with open("dados.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
except FileNotFoundError:
    conhecimento = "Nenhuma base de conhecimento carregada."

def responder(mensagem, historico):
    # Verifica senha na primeira mensagem
    if len(historico) == 0:
        if mensagem.strip().lower() != SENHA.lower():
            return "Senha incorreta. Digite a senha para acessar a BRM IA."
        return "✅ Acesso liberado! Como posso ajudar?"

    # Bloqueia se primeira resposta foi de senha incorreta
    if historico[0][1] == "Senha incorreta. Digite a senha para acessar a BRM IA.":
        if mensagem.strip().lower() != SENHA.lower():
            return "Senha incorreta. Digite a senha para acessar a BRM IA."
        return "✅ Acesso liberado! Como posso ajudar?"

    try:
        mensagens = [
            {
                "role": "system",
                "content": f"Você é a BRM IA.\nUse essas informações:\n{conhecimento}"
            }
        ]

        # Limita histórico às últimas 5 trocas
        historico_limitado = historico[-5:]
        for humano, assistente in historico_limitado:
            mensagens.append({"role": "user", "content": humano})
            mensagens.append({"role": "assistant", "content": assistente})

        mensagens.append({"role": "user", "content": mensagem})

        resposta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensagens,
            max_tokens=1024,
            temperature=0.7
        )
        return resposta.choices[0].message.content

    except Exception as e:
        return f"Erro: {str(e)}"

demo = gr.ChatInterface(
    fn=responder,
    title="🤖 BRM IA",
    description="Digite a senha para acessar."
)

app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
