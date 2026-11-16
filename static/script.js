// Chat page: keeps the conversation in memory, streams each answer from Flask.
(function () {
  "use strict";

  const log = document.getElementById("log");
  const empty = document.getElementById("empty");
  const form = document.getElementById("composer");
  const prompt = document.getElementById("prompt");
  const send = document.getElementById("send");
  const stop = document.getElementById("stop");
  const clear = document.getElementById("clear");
  const model = document.getElementById("model");
  const dot = document.getElementById("dot");
  const status = document.getElementById("status");
  const notice = document.getElementById("notice");

  function warn(message) {
    notice.textContent = message;
    notice.hidden = false;
    status.textContent = message;
  }

  let history = [];
  let controller = null;

  // Models installed in Ollama.
  async function loadModels() {
    try {
      const res = await fetch("/api/models");
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      dot.className = "dot ok";
      dot.title = "Ollama is running";
      if (!data.models.length) {
        warn("No models are installed yet. Run `ollama pull llama3`, then reload this page.");
        return;
      }
      const wanted = model.dataset.default;
      model.replaceChildren(...data.models.map((name) => new Option(name, name)));
      const match = data.models.find((name) => name === wanted || name.startsWith(wanted + ":"));
      model.value = match || data.models[0];
    } catch (err) {
      dot.className = "dot bad";
      dot.title = "Ollama isn't reachable";
      warn((err.message || "Can't reach Ollama. Start it with `ollama serve`.") + " Then reload this page.");
    }
  }

  function addTurn(kind, who, text) {
    empty.hidden = true;
    const turn = document.createElement("article");
    turn.className = "turn " + kind;
    const label = document.createElement("p");
    label.className = "who";
    label.textContent = who;
    const body = document.createElement("p");
    body.className = "text";
    body.textContent = text;
    turn.append(label, body);
    log.append(turn);
    turn.scrollIntoView({ block: "end" });
    return turn;
  }

  function setBusy(busy) {
    send.hidden = busy;
    stop.hidden = !busy;
    prompt.disabled = busy;
    model.disabled = busy;
    log.setAttribute("aria-busy", busy ? "true" : "false");
  }

  async function ask(text) {
    history.push({ role: "user", content: text });
    addTurn("you", "You", text);
    const turn = addTurn("model working", model.value, "");
    const body = turn.querySelector(".text");
    setBusy(true);
    controller = new AbortController();

    let answer = "";
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: model.value, messages: history }),
        signal: controller.signal,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "The request failed.");
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        answer += decoder.decode(value, { stream: true });
        body.textContent = answer;
        turn.scrollIntoView({ block: "end" });
      }
      history.push({ role: "assistant", content: answer });
      status.textContent = "Answer complete.";
    } catch (err) {
      if (err.name === "AbortError") {
        if (answer) history.push({ role: "assistant", content: answer });
        else history.pop();
        body.textContent = answer || "Stopped.";
        status.textContent = "Stopped.";
      } else {
        history.pop();
        turn.classList.add("failed");
        body.textContent = err.message;
        status.textContent = err.message;
      }
    } finally {
      turn.classList.remove("working");
      controller = null;
      setBusy(false);
      prompt.focus();
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const text = prompt.value.trim();
    if (!text || controller) return;
    prompt.value = "";
    prompt.style.height = "";
    ask(text);
  });

  prompt.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  // Grow the box with the text, up to the CSS max-height.
  prompt.addEventListener("input", () => {
    prompt.style.height = "auto";
    prompt.style.height = prompt.scrollHeight + "px";
  });

  stop.addEventListener("click", () => controller && controller.abort());

  clear.addEventListener("click", () => {
    if (controller) controller.abort();
    history = [];
    log.querySelectorAll(".turn").forEach((turn) => turn.remove());
    empty.hidden = false;
    status.textContent = "";
    prompt.focus();
  });

  loadModels();
})();
