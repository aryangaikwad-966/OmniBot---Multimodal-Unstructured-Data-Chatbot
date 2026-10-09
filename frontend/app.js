const fileInput = document.querySelector("#file-input");
const fileList = document.querySelector("#file-list");
const messages = document.querySelector("#messages");
const form = document.querySelector("#ask-form");
const question = document.querySelector("#question");
const button = form.querySelector("button");
const omni = document.querySelector("#omni");
let avatarDefinition;
let expressionIndex = 0;
let animationTimer;
let animationStep = 0;
let expressionCycleTimer;
let activeAnimation = "idle";

function applyExpression(name) {
  const expression = avatarDefinition?.expressions?.[name];
  if (!expression) return;
  const left = expression.eyes.left;
  const right = expression.eyes.right;
  const scale = 1.8;
  omni.dataset.expression = name;
  omni.style.background = expression.colors?.body || avatarDefinition.colors.body;
  omni.style.transform = `rotate(${expression.head.z / 8 - 2}deg)`;
  document.querySelector(".eye-left").style.cssText = `width:${left.width * scale}px;height:${left.height * scale}px;left:${83 + left.x * scale}px;top:${112 - left.y * scale}px;transform:rotate(${left.angle}deg)`;
  document.querySelector(".eye-right").style.cssText = `width:${right.width * scale}px;height:${right.height * scale}px;left:${83 + right.x * scale + expression.eyes.spacing}px;top:${112 - right.y * scale}px;transform:rotate(${right.angle}deg)`;
}

async function loadAvatar() {
  const response = await fetch("/api/avatar");
  avatarDefinition = await response.json();
  const names = avatarDefinition.expressionOrder || Object.keys(avatarDefinition.expressions);
  startExpressionCycle();
}

function playAnimation(name) {
  const animation = avatarDefinition?.animations?.[name];
  if (!animation?.steps?.length) return;
  activeAnimation = name;
  window.clearInterval(expressionCycleTimer);
  window.clearTimeout(animationTimer);
  animationStep = 0;
  document.querySelector("#assistant-state").textContent = animation.metadata?.label
    ? `Omni is ${animation.metadata.label}`
    : "Omni is helping";
  const next = () => {
    const step = animation.steps[animationStep % animation.steps.length];
    applyExpression(step.expression);
    animationStep += 1;
    animationTimer = window.setTimeout(next, step.holdMs || 2200);
  };
  next();
}

function startExpressionCycle() {
  const names = avatarDefinition?.expressionOrder || [];
  if (!names.length) return;
  activeAnimation = "idle";
  window.clearTimeout(animationTimer);
  window.clearInterval(expressionCycleTimer);
  document.querySelector("#assistant-state").textContent = "Omni is here to help";
  expressionIndex = 0;
  applyExpression(names[expressionIndex]);
  expressionCycleTimer = window.setInterval(() => {
    expressionIndex = (expressionIndex + 1) % names.length;
    applyExpression(names[expressionIndex]);
  }, 2800);
}

function returnToExpressionCycle(delay = 7000) {
  window.setTimeout(() => {
    if (activeAnimation !== "idle") startExpressionCycle();
  }, delay);
}

loadAvatar().catch(() => {});

question.addEventListener("input", () => {
  if (question.value.trim()) {
    playAnimation("thinking");
    returnToExpressionCycle(4000);
  }
});

question.addEventListener("focus", () => {
  if (!question.value.trim()) {
    playAnimation("listening");
    returnToExpressionCycle(4000);
  }
});

function addMessage(name, text, user = false) {
  const item = document.createElement("div");
  item.className = `message ${user ? "user-message" : "omni-message"}`;
  item.innerHTML = `<b>${name}</b><p>${text}</p>`;
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

function showFiles(files) {
  fileList.innerHTML = [...files].map(file => `<span class="file-pill">${file.name}</span>`).join("");
}

fileInput.addEventListener("change", async () => {
  if (!fileInput.files.length) return;
  showFiles(fileInput.files);
  playAnimation("listening");
  returnToExpressionCycle(5000);
  const data = new FormData();
  [...fileInput.files].forEach(file => data.append("files", file));
  try {
    const response = await fetch("/api/upload", { method: "POST", body: data });
    const result = await response.json();
    if (result.errors?.length) addMessage("Omni", result.errors.join(" "));
    if (result.added?.length) addMessage("Omni", `${result.added.length} file${result.added.length === 1 ? "" : "s"} ready. Ask me anything.`);
  } catch {
    addMessage("Omni", "I couldn’t connect to the local server. Is web_app.py running?");
  } finally {
    startExpressionCycle();
  }
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  const text = question.value.trim();
  if (!text) return;
  addMessage("You", text, true);
  question.value = "";
  button.disabled = true;
  playAnimation("searching");
  try {
    const response = await fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: text }) });
    const result = await response.json();
    addMessage("Omni", result.error || `${result.answer}${result.source ? ` (Source: ${result.source})` : ""}`);
    playAnimation(result.error ? "suspicious" : "excited");
    returnToExpressionCycle();
  } catch {
    addMessage("Omni", "Something went wrong while searching your files.");
    playAnimation("suspicious");
    returnToExpressionCycle();
  } finally {
    button.disabled = false;
  }
});
