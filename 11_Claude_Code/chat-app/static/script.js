const conversationId = crypto.randomUUID();

const history = document.getElementById("history");
const composer = document.getElementById("composer");
const messageInput = document.getElementById("message-input");

function appendMessage(role, text) {
  const el = document.createElement("div");
  el.className = `message ${role}`;
  el.textContent = text;
  history.appendChild(el);
  history.scrollTop = history.scrollHeight;
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  messageInput.value = "";

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });

  const data = await response.json();
  appendMessage("assistant", data.reply);
});
