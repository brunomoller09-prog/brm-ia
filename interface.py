import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from groq import Groq
import uvicorn

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    with open("dados.txt", "r", encoding="utf-8") as f:
        conhecimento = f.read()
except FileNotFoundError:
    conhecimento = "Nenhuma base de conhecimento carregada."

SYSTEM_PROMPT = f"""Você é a BRM IA, assistente virtual da BRM.
Responda sempre em português, de forma clara e bem formatada.
Use marcadores, listas numeradas e negrito quando ajudar na clareza.
Use apenas as informações abaixo. Se não souber, diga: 'Não tenho essa informação no processo.'

{conhecimento}"""

app = FastAPI()

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BRM IA</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@700&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  :root {
    --azul: #1a2f5e;
    --amarelo: #f5a800;
    --amarelo-hover: #e09500;
    --branco: #ffffff;
    --cinza-bg: #f0f2f5;
    --texto: #1a2f5e;
    --texto-claro: #5a6a8a;
    --borda: #d0d8e8;
  }
  body { font-family: 'Barlow', sans-serif; background: var(--cinza-bg); height: 100dvh; display: flex; flex-direction: column; overflow: hidden; }
  header { background: var(--azul); padding: 0 20px; height: 64px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
  .logo-text { font-family: 'Barlow Condensed', sans-serif; font-size: 28px; font-weight: 700; color: var(--branco); }
  .logo-text span { color: var(--amarelo); }
  .status { display: flex; align-items: center; gap: 6px; font-size: 13px; color: rgba(255,255,255,0.7); }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
  .chat-area { flex: 1; overflow-y: auto; padding: 24px 20px; display: flex; flex-direction: column; gap: 16px; scroll-behavior: smooth; }
  .chat-area::-webkit-scrollbar { width: 4px; }
  .chat-area::-webkit-scrollbar-thumb { background: var(--borda); border-radius: 4px; }
  .welcome { text-align: center; padding: 40px 20px; }
  .welcome-icon { width: 72px; height: 72px; background: var(--azul); border-radius: 20px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
  .welcome h2 { font-size: 20px; font-weight: 600; color: var(--texto); margin-bottom: 8px; }
  .welcome p { font-size: 14px; color: var(--texto-claro); line-height: 1.6; max-width: 320px; margin: 0 auto; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 20px; }
  .chip { background: var(--branco); border: 1.5px solid var(--borda); border-radius: 20px; padding: 8px 16px; font-size: 13px; color: var(--azul); cursor: pointer; font-family: 'Barlow', sans-serif; font-weight: 500; transition: all 0.15s; }
  .chip:hover { background: var(--azul); color: var(--branco); border-color: var(--azul); }
  .msg { display: flex; gap: 10px; max-width: 85%; animation: fadeIn 0.2s ease; }
  @keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
  .msg.user { align-self: flex-end; flex-direction: row-reverse; }
  .msg.bot { align-self: flex-start; }
  .avatar { width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; }
  .msg.bot .avatar { background: var(--azul); color: var(--amarelo); font-family: 'Barlow Condensed', sans-serif; }
  .msg.user .avatar { background: var(--amarelo); color: var(--azul); }
  .bubble { padding: 12px 16px; border-radius: 16px; font-size: 15px; line-height: 1.7; }
  .msg.bot .bubble { background: var(--branco); color: var(--texto); border-bottom-left-radius: 4px; border: 1px solid var(--borda); }
  .msg.user .bubble { background: var(--azul); color: var(--branco); border-bottom-right-radius: 4px; }
  .bubble p { margin-bottom: 8px; }
  .bubble p:last-child { margin-bottom: 0; }
  .bubble ul, .bubble ol { padding-left: 20px; margin: 8px 0; }
  .bubble li { margin-bottom: 4px; }
  .bubble strong { font-weight: 600; }
  .bubble h3 { font-size: 15px; font-weight: 600; margin: 12px 0 6px; }
  .bubble h3:first-child { margin-top: 0; }
  .typing { display: flex; gap: 4px; padding: 14px 16px; }
  .typing span { width: 7px; height: 7px; border-radius: 50%; background: var(--texto-claro); animation: bounce 1.2s infinite; }
  .typing span:nth-child(2) { animation-delay: 0.2s; }
  .typing span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }
  .input-area { background: var(--branco); border-top: 1px solid var(--borda); padding: 16px 20px; flex-shrink: 0; }
  .input-row { display: flex; gap: 10px; align-items: flex-end; max-width: 800px; margin: 0 auto; }
  textarea { flex: 1; border: 1.5px solid var(--borda); border-radius: 14px; padding: 12px 16px; font-size: 15px; font-family: 'Barlow', sans-serif; color: var(--texto); resize: none; outline: none; max-height: 120px; min-height: 48px; line-height: 1.5; transition: border-color 0.15s; background: var(--cinza-bg); }
  textarea:focus { border-color: var(--azul); background: var(--branco); }
  textarea::placeholder { color: var(--texto-claro); }
  button#send { width: 48px; height: 48px; border-radius: 14px; border: none; background: var(--amarelo); color: var(--azul); cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.15s; }
  button#send:hover { background: var(--amarelo-hover); transform: scale(1.04); }
  button#send:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
  button#send svg { width: 20px; height: 20px; }
  .disclaimer { text-align: center; font-size: 11px; color: var(--texto-claro); margin-top: 8px; }
  @media (max-width: 480px) { .chat-area { padding: 16px 12px; } .msg { max-width: 92%; } .input-area { padding: 12px 16px; } }
</style>
</head>
<body>
<header>
  <div style="display:flex;align-items:center;gap:12px">
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="10" fill="#243f7a"/>
      <polygon points="20,6 26,18 22,18 28,34 14,20 19,20" fill="#f5a800"/>
    </svg>
    <div class="logo-text">BRM<span>ia</span></div>
  </div>
  <div class="status"><div class="status-dot"></div>Online</div>
</header>

<div class="chat-area" id="chat">
  <div class="welcome" id="welcome">
    <div class="welcome-icon">
      <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
        <polygon points="18,4 24,16 20,16 26,32 10,18 16,18" fill="#f5a800"/>
      </svg>
    </div>
    <h2>Olá! Sou a BRM IA</h2>
    <p>Sua assistente de processos industriais e logísticos.</p>
    <div class="chips">
      <button class="chip" onclick="sendChip(this)">Como fazer recebimento?</button>
      <button class="chip" onclick="sendChip(this)">Como abrir uma ocorrência?</button>
      <button class="chip" onclick="sendChip(this)">Processo de devolução</button>
      <button class="chip" onclick="sendChip(this)">Picking de minuterias</button>
    </div>
  </div>
</div>

<div class="input-area">
  <div class="input-row">
    <textarea id="input" placeholder="Digite sua dúvida..." rows="1"></textarea>
    <button id="send" onclick="send()">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>
  </div>
  <div class="disclaimer">BRM IA · Respostas baseadas nos processos da empresa</div>
</div>

<script>
  const chat = document.getElementById('chat');
  const input = document.getElementById('input');
  const sendBtn = document.getElementById('send');
  let history = [];

  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });

  function sendChip(el) { input.value = el.textContent; send(); }

  function parseMarkdown(text) {
    let html = text
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
      .replace(/\*(.*?)\*/g,'<em>$1</em>')
      .replace(/###\s(.+)/g,'<h3>$1</h3>')
      .replace(/##\s(.+)/g,'<h3>$1</h3>');
    const lines = html.split('\n');
    const result = [];
    let inUl = false, inOl = false;
    for (let line of lines) {
      const ul = line.match(/^[-•*]\s(.+)/);
      const ol = line.match(/^\d+\.\s(.+)/);
      if (ul) {
        if (!inUl) { result.push('<ul>'); inUl = true; }
        result.push('<li>' + ul[1] + '</li>');
      } else if (ol) {
        if (!inOl) { result.push('<ol>'); inOl = true; }
        result.push('<li>' + ol[1] + '</li>');
      } else {
        if (inUl) { result.push('</ul>'); inUl = false; }
        if (inOl) { result.push('</ol>'); inOl = false; }
        if (line.trim() === '') result.push('');
        else if (line.startsWith('<h3>')) result.push(line);
        else result.push('<p>' + line + '</p>');
      }
    }
    if (inUl) result.push('</ul>');
    if (inOl) result.push('</ol>');
    return result.join('');
  }

  function addMsg(text, who) {
    document.getElementById('welcome')?.remove();
    const div = document.createElement('div');
    div.className = 'msg ' + who;
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = who === 'bot' ? 'IA' : 'EU';
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = who === 'bot' ? parseMarkdown(text) : text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    div.appendChild(avatar);
    div.appendChild(bubble);
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function addTyping() {
    document.getElementById('welcome')?.remove();
    const div = document.createElement('div');
    div.className = 'msg bot'; div.id = 'typing';
    const avatar = document.createElement('div');
    avatar.className = 'avatar'; avatar.textContent = 'IA';
    const bubble = document.createElement('div');
    bubble.className = 'bubble typing';
    bubble.innerHTML = '<span></span><span></span><span></span>';
    div.appendChild(avatar); div.appendChild(bubble);
    chat.appendChild(div); chat.scrollTop = chat.scrollHeight;
  }

  async function send() {
    const text = input.value.trim();
    if (!text) return;
    addMsg(text, 'user');
    input.value = ''; input.style.height = 'auto';
    sendBtn.disabled = true;
    addTyping();
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({message: text, history})
      });
      const data = await res.json();
      document.getElementById('typing')?.remove();
      addMsg(data.response, 'bot');
      history.push([text, data.response]);
      if (history.length > 5) history = history.slice(-5);
    } catch(e) {
      document.getElementById('typing')?.remove();
      addMsg('Erro de conexão. Tente novamente.', 'bot');
    }
    sendBtn.disabled = false;
    input.focus();
  }
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML

@app.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    mensagem = body.get("message", "")
    historico = body.get("history", [])
    try:
        mensagens = [{"role": "system", "content": SYSTEM_PROMPT}]
        for par in historico[-5:]:
            mensagens.append({"role": "user", "content": par[0]})
            mensagens.append({"role": "assistant", "content": par[1]})
        mensagens.append({"role": "user", "content": mensagem})
        resposta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensagens,
            max_tokens=1024,
            temperature=0.7
        )
        return JSONResponse({"response": resposta.choices[0].message.content})
    except Exception as e:
        return JSONResponse({"response": f"Erro: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
