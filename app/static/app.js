const chatWindow = document.getElementById("chat-window");
const quickRepliesContainer = document.getElementById("quick-replies");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const resetBtn = document.getElementById("reset-btn");
const demoBtn = document.getElementById("demo-btn");
const demoStatus = document.getElementById("demo-status");
const stateBadge = document.getElementById("state-badge");
const summaryState = document.getElementById("summary-state");
const summaryFluxo = document.getElementById("summary-fluxo");
const summaryGrid = document.getElementById("summary-grid");

let sessionId = localStorage.getItem("vexia_session_id") || null;
let typingNode = null;
let runningDemo = false;

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addMessage(text, sender = "bot") {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.textContent = text;
  chatWindow.appendChild(msg);
  scrollToBottom();
  return msg;
}

function showTyping() {
  removeTyping();
  typingNode = document.createElement("div");
  typingNode.classList.add("typing");
  typingNode.textContent = "Digitando…";
  chatWindow.appendChild(typingNode);
  scrollToBottom();
}

function removeTyping() {
  if (typingNode) {
    typingNode.remove();
    typingNode = null;
  }
}

function renderQuickReplies(options = []) {
  quickRepliesContainer.innerHTML = "";
  options.forEach((opt) => {
    const btn = document.createElement("button");
    btn.className = "pill";
    btn.textContent = opt;
    btn.onclick = () => sendMessage(opt, true);
    quickRepliesContainer.appendChild(btn);
  });
}

function renderSummary(context = {}, state = "MENU") {
  stateBadge.textContent = `Estado: ${state}`;
  summaryState.textContent = state;
  summaryFluxo.textContent = context.fluxo || "-";

  const labels = {
    bairro: "Bairro",
    tipo: "Tipo",
    quantidade: "Quantidade",
    horario: "Quando",
    ong_nome: "ONG",
    necessidade: "Necessidade",
    pessoas: "Pessoas",
    urgencia: "Urgência",
    disponibilidade: "Disponibilidade",
    contato: "Contato",
  };

  summaryGrid.innerHTML = "";
  Object.entries(labels).forEach(([key, label]) => {
    if (context[key]) {
      const tile = document.createElement("div");
      tile.className = "summary-tile";
      tile.innerHTML = `<span class="label">${label}</span><div>${context[key]}</div>`;
      summaryGrid.appendChild(tile);
    }
  });
}

async function callApi(endpoint, payload) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error("Erro ao falar com o servidor");
  }
  return res.json();
}

async function sendMessage(message, fromQuickReply = false, silentUser = false) {
  const text = message || messageInput.value.trim();
  if (!text && !silentUser) return;

  if (!silentUser && text) {
    addMessage(text, "user");
    messageInput.value = "";
  }

  renderQuickReplies([]);
  showTyping();

  try {
    const data = await callApi("/api/chat", {
      session_id: sessionId,
      message: text,
      channel: "web",
    });

    sessionId = data.session_id;
    localStorage.setItem("vexia_session_id", sessionId);

    const delay = Math.random() * 300 + 300; // 300-600ms
    return await new Promise((resolve) => {
      setTimeout(() => {
        removeTyping();
        addMessage(data.reply, "bot");
        renderQuickReplies(data.quick_replies);
        renderSummary(data.context, data.state);
        resolve();
      }, delay);
    });
  } catch (err) {
    removeTyping();
    addMessage("Ops, algo falhou. Tente novamente.", "bot");
    console.error(err);
    return;
  }
}

async function resetConversation() {
  chatWindow.innerHTML = "";
  quickRepliesContainer.innerHTML = "";
  try {
    const data = await callApi("/api/reset", {
      session_id: sessionId,
      message: "",
      channel: "web",
    });
    sessionId = data.session_id;
    localStorage.setItem("vexia_session_id", sessionId);
    addMessage(data.reply, "bot");
    renderQuickReplies(data.quick_replies);
    renderSummary(data.context, data.state);
  } catch (err) {
    addMessage("Erro ao reiniciar. Tente novamente.", "bot");
  }
}

sendBtn.addEventListener("click", () => sendMessage());
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendMessage();
  }
});

resetBtn.addEventListener("click", resetConversation);

function setUiEnabled(enabled) {
  messageInput.disabled = !enabled;
  sendBtn.disabled = !enabled;
}

function showDemoStatus(show) {
  demoStatus.style.display = show ? "inline-flex" : "none";
}

async function runDemo() {
  if (runningDemo) return;
  runningDemo = true;
  setUiEnabled(false);
  demoBtn.disabled = true;
  showDemoStatus(true);
  demoStatus.textContent = "Executando demo…";

  const script = ["Preciso de comida", "rocinha", "4", "Hoje", "Confirmar"];

  try {
    await resetConversation();
    for (const msg of script) {
      await sendMessage(msg);
      await new Promise((res) => setTimeout(res, 500));
    }
  } catch (err) {
    console.error("Demo falhou", err);
  } finally {
    setUiEnabled(true);
    demoBtn.disabled = false;
    showDemoStatus(false);
    runningDemo = false;
  }
}

demoBtn.addEventListener("click", runDemo);

// inicializa com menu
resetConversation();

