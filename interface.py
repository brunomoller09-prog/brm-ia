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
<html lang="pt-BR" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BRM IA</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@700&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --azul: #1a2f5e;
    --azul-claro: #243f7a;
    --amarelo: #f5a800;
    --amarelo-hover: #e09500;
    --branco: #ffffff;
    --cinza-bg: #f0f2f5;
    --texto: #1a2f5e;
    --texto-claro: #5a6a8a;
    --borda: #d0d8e8;
    --bubble-bot: #ffffff;
    --bubble-user: #1a2f5e;
    --header-bg: #1a2f5e;
    --input-bg: #f0f2f5;
    --shadow: rgba(26,47,94,0.08);
  }

  [data-theme="dark"] {
    --branco: #1e2433;
    --cinza-bg: #151929;
    --texto: #e8edf5;
    --texto-claro: #8896b0;
    --borda: #2a3550;
    --bubble-bot: #1e2a42;
    --bubble-user: #1a4a8a;
    --header-bg: #0f1829;
    --input-bg: #1e2433;
    --shadow: rgba(0,0,0,0.3);
  }

  body {
    font-family: 'Barlow', sans-serif;
    background: var(--cinza-bg);
    height: 100dvh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: background 0.3s, color 0.3s;
  }

  header {
    background: var(--header-bg);
    padding: 0 20px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
    box-shadow: 0 2px 16px var(--shadow);
  }

  .logo-area { display: flex; align-items: center; gap: 12px; }
  .logo-text { font-family: 'Barlow Condensed', sans-serif; font-size: 28px; font-weight: 700; color: #fff; letter-spacing: 1px; }
  .logo-text span { color: var(--amarelo); }

  .header-right { display: flex; align-items: center; gap: 12px; }

  .status { display: flex; align-items: center; gap: 6px; font-size: 13px; color: rgba(255,255,255,0.7); }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .theme-btn {
    width: 36px; height: 36px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.1); color: #fff; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s; font-size: 16px;
  }
  .theme-btn:hover { background: rgba(255,255,255,0.2); }

  .chat-area {
    flex: 1; overflow-y: auto; padding: 24px 20px;
    display: flex; flex-direction: column; gap: 20px;
    scroll-behavior: smooth;
  }
  .chat-area::-webkit-scrollbar { width: 4px; }
  .chat-area::-webkit-scrollbar-thumb { background: var(--borda); border-radius: 4px; }

  .welcome { text-align: center; padding: 48px 20px; }
  .welcome-icon {
    width: 80px; height: 80px; background: var(--azul); border-radius: 24px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 20px;
    box-shadow: 0 8px 32px rgba(26,47,94,0.25);
    animation: float 3s ease-in-out infinite;
  }
  @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
  .welcome h2 { font-size: 22px; font-weight: 700; color: var(--texto); margin-bottom: 8px; }
  .welcome p { font-size: 15px; color: var(--texto-claro); line-height: 1.6; max-width: 340px; margin: 0 auto 24px; }

  .chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
  .chip {
    background: var(--bubble-bot); border: 1.5px solid var(--borda);
    border-radius: 20px; padding: 8px 16px; font-size: 13px;
    color: var(--azul); cursor: pointer; font-family: 'Barlow', sans-serif;
    font-weight: 500; transition: all 0.2s;
  }
  [data-theme="dark"] .chip { color: var(--amarelo); }
  .chip:hover { background: var(--azul); color: #fff; border-color: var(--azul); transform: translateY(-1px); }

  .msg { display: flex; gap: 10px; max-width: 80%; animation: fadeUp 0.25s ease; }
  @keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
  .msg.user { align-self: flex-end; flex-direction: row-reverse; }
  .msg.bot { align-self: flex-start; }

  .avatar {
    width: 34px; height: 34px; border-radius: 11px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700;
  }
  .msg.bot .avatar { background: var(--azul); color: var(--amarelo); font-family: 'Barlow Condensed', sans-serif; font-size: 15px; }
  .msg.user .avatar { background: var(--amarelo); color: var(--azul); }

  .msg-wrapper { display: flex; flex-direction: column; gap: 4px; }
  .msg.user .msg-wrapper { align-items: flex-end; }

  .bubble {
    padding: 12px 16px; border-radius: 18px; font-size: 15px; line-height: 1.7;
    position: relative;
  }
  .msg.bot .bubble {
    background: var(--bubble-bot); color: var(--texto);
    border-bottom-left-radius: 4px; border: 1px solid var(--borda);
    box-shadow: 0 1px 4px var(--shadow);
  }
  .msg.user .bubble {
    background: var(--bubble-user); color: #fff;
    border-bottom-right-radius: 4px;
  }
  .bubble p { margin-bottom: 8px; }
  .bubble p:last-child { margin-bottom: 0; }
  .bubble ul, .bubble ol { padding-left: 20px; margin: 8px 0; }
  .bubble li { margin-bottom: 4px; }
  .bubble strong { font-weight: 600; }
  .bubble h3 { font-size: 15px; font-weight: 600; margin: 12px 0 6px; color: var(--azul); }
  [data-theme="dark"] .bubble h3 { color: var(--amarelo); }
  .bubble h3:first-child { margin-top: 0; }

  .msg-actions {
    display: flex; gap: 6px; opacity: 0; transition: opacity 0.2s;
  }
  .msg:hover .msg-actions { opacity: 1; }
  .action-btn {
    background: var(--bubble-bot); border: 1px solid var(--borda);
    border-radius: 8px; padding: 4px 10px; font-size: 12px;
    color: var(--texto-claro); cursor: pointer; font-family: 'Barlow', sans-serif;
    transition: all 0.15s; display: flex; align-items: center; gap: 4px;
  }
  .action-btn:hover { background: var(--azul); color: #fff; border-color: var(--azul); }
  .action-btn.copied { background: #22c55e; color: #fff; border-color: #22c55e; }

  .timestamp { font-size: 11px; color: var(--texto-claro); padding: 0 4px; }

  .typing { display: flex; gap: 5px; padding: 14px 16px; }
  .typing span { width: 8px; height: 8px; border-radius: 50%; background: var(--texto-claro); animation: bounce 1.2s infinite; }
  .typing span:nth-child(2) { animation-delay: 0.2s; }
  .typing span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-7px)} }

  .input-area {
    background: var(--branco); border-top: 1px solid var(--borda);
    padding: 16px 20px; flex-shrink: 0;
  }
  .input-row { display: flex; gap: 10px; align-items: flex-end; max-width: 800px; margin: 0 auto; }

  textarea {
    flex: 1; border: 1.5px solid var(--borda); border-radius: 14px;
    padding: 12px 16px; font-size: 15px; font-family: 'Barlow', sans-serif;
    color: var(--texto); resize: none; outline: none;
    max-height: 120px; min-height: 48px; line-height: 1.5;
    transition: border-color 0.2s, box-shadow 0.2s;
    background: var(--input-bg);
  }
  textarea:focus { border-color: var(--azul); box-shadow: 0 0 0 3px rgba(26,47,94,0.1); background: var(--branco); }
  textarea::placeholder { color: var(--texto-claro); }

  button#send {
    width: 48px; height: 48px; border-radius: 14px; border: none;
    background: var(--amarelo); color: var(--azul); cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: all 0.2s;
  }
  button#send:hover { background: var(--amarelo-hover); transform: scale(1.06); }
  button#send:active { transform: scale(0.96); }
  button#send:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }
  button#send svg { width: 20px; height: 20px; }

  .input-footer { display: flex; justify-content: space-between; align-items: center; max-width: 800px; margin: 8px auto 0; }
  .disclaimer { font-size: 11px; color: var(--texto-claro); }
  .clear-btn {
    font-size: 12px; color: var(--texto-claro); background: none;
    border: none; cursor: pointer; font-family: 'Barlow', sans-serif;
    padding: 2px 8px; border-radius: 6px; transition: all 0.15s;
  }
  .clear-btn:hover { color: #e53e3e; background: rgba(229,62,62,0.08); }

  .toast {
    position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%) translateY(20px);
    background: #1a2f5e; color: #fff; padding: 10px 20px; border-radius: 12px;
    font-size: 14px; font-family: 'Barlow', sans-serif;
    opacity: 0; transition: all 0.3s; pointer-events: none; z-index: 100;
  }
  .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }

  @media (max-width: 480px) {
    header { padding: 0 14px; }
    .logo-text { font-size: 22px; }
    .chat-area { padding: 16px 12px; }
    .msg { max-width: 92%; }
    .input-area { padding: 12px 14px; }
  }
</style>
</head>
<body>

<header>
  <div class="logo-area">
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="10" fill="#243f7a"/>
      <polygon points="20,6 26,18 22,18 28,34 14,20 19,20" fill="#f5a800"/>
    </svg>
    <div class="logo-text">BRM<span>ia</span></div>
  </div>
  <div class="header-right">
    <div class="status"><div class="status-dot"></div>Online</div>
    <button class="theme-btn" onclick="toggleTheme()" title="Alternar tema">🌙</button>
  </div>
</header>

<div class="chat-area" id="chat">
  <div class="welcome" id="welcome">
    <div class="welcome-icon">
      <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
        <polygon points="20,4 27,18 23,18 30,36 10,20 17,20" fill="#f5a800"/>
      </svg>
    </div>
    <h2>Olá! Sou a BRM IA</h2>
    <p>Sua assistente de processos industriais e logísticos. Como posso ajudar hoje?</p>
    <div class="chips">
      <button class="chip" onclick="sendChip(this)">Como fazer recebimento?</button>
      <button class="chip" onclick="sendChip(this)">Como abrir uma ocorrência?</button>
      <button class="chip" onclick="sendChip(this)">Processo de devolução</button>
      <button class="chip" onclick="sendChip(this)">Picking de minuterias</button>
      <button class="chip" onclick="sendChip(this)">Agendamento de materiais</button>
      <button class="chip" onclick="sendChip(this)">Indicadores logísticos</button>
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
  <div class="input-footer">
    <span class="disclaimer">BRM IA · Respostas baseadas nos processos da empresa</span>
    <button class="clear-btn" onclick="clearChat()">🗑 Limpar</button>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
  const chat = document.getElementById('chat');
  const input = document.getElementById('input');
  const sendBtn = document.getElementById('send');
  let history = [];

  // Tema
  const savedTheme = localStorage.getItem('brm-theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  document.querySelector('.theme-btn').textContent = savedTheme === 'dark' ? '☀️' : '🌙';

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('brm-theme', next);
    document.querySelector('.theme-btn').textContent = next === 'dark' ? '☀️' : '🌙';
  }

  // Toast
  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg; t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2000);
  }

  // Input auto-resize
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });

  function sendChip(el) { input.value = el.textContent; send(); }

  function getTime() {
    return new Date().toLocaleTimeString('pt-BR', {hour:'2-digit', minute:'2-digit'});
  }

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

    const wrapper = document.createElement('div');
    wrapper.className = 'msg-wrapper';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = who === 'bot'
      ? parseMarkdown(text)
      : text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

    const footer = document.createElement('div');
    footer.style.display = 'flex';
    footer.style.alignItems = 'center';
    footer.style.gap = '6px';

    const ts = document.createElement('span');
    ts.className = 'timestamp';
    ts.textContent = getTime();
    footer.appendChild(ts);

    if (who === 'bot') {
      const actions = document.createElement('div');
      actions.className = 'msg-actions';

      const copyBtn = document.createElement('button');
      copyBtn.className = 'action-btn';
      copyBtn.innerHTML = '📋 Copiar';
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(text);
        copyBtn.innerHTML = '✅ Copiado';
        copyBtn.classList.add('copied');
        setTimeout(() => { copyBtn.innerHTML = '📋 Copiar'; copyBtn.classList.remove('copied'); }, 2000);
      };
      actions.appendChild(copyBtn);
      footer.appendChild(actions);
    }

    wrapper.appendChild(bubble);
    wrapper.appendChild(footer);
    div.appendChild(avatar);
    div.appendChild(wrapper);
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function addTyping() {
    document.getElementById('welcome')?.remove();
    const div = document.createElement('div');
    div.className = 'msg bot'; div.id = 'typing';
    const avatar = document.createElement('div');
    avatar.className = 'avatar'; avatar.textContent = 'IA';
    const wrapper = document.createElement('div');
    wrapper.className = 'msg-wrapper';
    const bubble = document.createElement('div');
    bubble.className = 'bubble typing';
    bubble.innerHTML = '<span></span><span></span><span></span>';
    wrapper.appendChild(bubble);
    div.appendChild(avatar); div.appendChild(wrapper);
    chat.appendChild(div); chat.scrollTop = chat.scrollHeight;
  }

  function clearChat() {
    history = [];
    chat.innerHTML = '';
    const welcome = document.createElement('div');
    welcome.className = 'welcome'; welcome.id = 'welcome';
    welcome.innerHTML = `
      <div class="welcome-icon">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <polygon points="20,4 27,18 23,18 30,36 10,20 17,20" fill="#f5a800"/>
        </svg>
      </div>
      <h2>Olá! Sou a BRM IA</h2>
      <p>Sua assistente de processos industriais e logísticos. Como posso ajudar hoje?</p>
      <div class="chips">
        <button class="chip" onclick="sendChip(this)">Como fazer recebimento?</button>
        <button class="chip" onclick="sendChip(this)">Como abrir uma ocorrência?</button>
        <button class="chip" onclick="sendChip(this)">Processo de devolução</button>
        <button class="chip" onclick="sendChip(this)">Picking de minuterias</button>
        <button class="chip" onclick="sendChip(this)">Agendamento de materiais</button>
        <button class="chip" onclick="sendChip(this)">Indicadores logísticos</button>
      </div>`;
    chat.appendChild(welcome);
    showToast('Conversa limpa');
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
