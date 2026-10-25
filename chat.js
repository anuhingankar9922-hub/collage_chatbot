const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const quickReplies = document.getElementById("quick-replies");

function addMessage(text, sender, meta) {
  const msg = document.createElement("div");
  msg.className = `msg ${sender}`;
  msg.textContent = text;
  if (meta) {
    const m = document.createElement("div");
    m.className = "meta";
    m.textContent = meta;
    msg.appendChild(m);
  }
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return msg;
}

function addTyping() {
  const msg = document.createElement("div");
  msg.className = "msg typing";
  msg.textContent = "Assistant is typing…";
  msg.id = "typing-indicator";
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

async function sendMessage(text) {
  addMessage(text, "user");
  addTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    removeTyping();

    const metaText = data.intent ? `intent: ${data.intent} · confidence: ${data.confidence}` : "";
    addMessage(data.response, "bot", metaText);
  } catch (err) {
    removeTyping();
    addMessage("Sorry, something went wrong connecting to the server. Please try again.", "bot");
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;
  userInput.value = "";
  sendMessage(text);
});

quickReplies.addEventListener("click", (e) => {
  if (e.target.classList.contains("chip")) {
    sendMessage(e.target.dataset.msg);
  }
});

// Greet on load
window.addEventListener("DOMContentLoaded", () => {
  addMessage(
    "Hello! I'm the campus assistant. Ask me about admissions, courses, fees, hostel, or placements — or tap a quick option below.",
    "bot"
  );
});
