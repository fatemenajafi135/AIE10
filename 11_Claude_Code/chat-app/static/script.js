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
  return el;
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  messageInput.value = "";

  // A live status bubble that updates as the agent works, then gets
  // replaced by the final answer.
  const status = appendMessage("assistant status", "Thinking…");

  const url =
    "/api/chat/stream?message=" +
    encodeURIComponent(message) +
    "&conversation_id=" +
    encodeURIComponent(conversationId);
  const source = new EventSource(url);

  // Tool events can arrive in a rapid burst (the agent fires several reads
  // in well under a second). Without pacing, the browser only ever paints
  // the last one. This queue shows each label for a brief minimum dwell so
  // the live progress is actually visible.
  const labelQueue = [];
  let draining = false;
  let finalReply = null;

  function drainQueue() {
    if (draining) return;
    draining = true;
    const step = () => {
      if (labelQueue.length > 0) {
        status.textContent = labelQueue.shift();
        history.scrollTop = history.scrollHeight;
        setTimeout(step, 450);
      } else {
        draining = false;
        if (finalReply !== null) {
          status.remove();
          appendMessage("assistant", finalReply);
          source.close();
        }
      }
    };
    step();
  }

  source.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type === "tool") {
      labelQueue.push(data.label || `Using ${data.name}…`);
      drainQueue();
    } else if (data.type === "result" || data.type === "error") {
      finalReply = data.reply;
      // Let any queued tool labels finish showing first, then swap in the
      // answer (drainQueue handles the handoff when the queue empties).
      if (!draining) {
        status.remove();
        appendMessage("assistant", finalReply);
        source.close();
      }
    }
  };

  source.onerror = () => {
    status.className = "message assistant";
    status.textContent = "Sorry, the connection dropped. Please try again.";
    source.close();
  };
});
