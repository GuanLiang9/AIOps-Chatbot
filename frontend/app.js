const API = '';   // same origin — FastAPI serves the frontend
let sessionId = null;
let samples = [];

/* ──────────────────────────────────────────────────────────────
   Tab navigation
────────────────────────────────────────────────────────────── */
document.querySelectorAll('.nav-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
  });
});

/* ──────────────────────────────────────────────────────────────
   Health check + status badge
────────────────────────────────────────────────────────────── */
async function checkHealth() {
  try {
    const res = await fetch(`${API}/health`);
    const data = await res.json();
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');

    if (data.ai_mode === 'ollama') {
      dot.className = 'status-dot';
      text.textContent = `Ollama · ${data.model}`;
    } else {
      dot.className = 'status-dot mock';
      text.textContent = 'Mock mode (Ollama offline)';
    }
  } catch {
    document.getElementById('statusDot').className = 'status-dot offline';
    document.getElementById('statusText').textContent = 'Server offline';
  }
}

/* ──────────────────────────────────────────────────────────────
   Chat
────────────────────────────────────────────────────────────── */
const chatMessages = document.getElementById('chatMessages');
const chatInput    = document.getElementById('chatInput');
const sendBtn      = document.getElementById('sendBtn');
const clearChatBtn = document.getElementById('clearChatBtn');

function appendMessage(role, text) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'user' ? '👤' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.textContent = text;

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chatMessages.appendChild(wrap);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return wrap;
}

function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'msg assistant';
  wrap.id = 'typingIndicator';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble typing-indicator';
  bubble.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chatMessages.appendChild(wrap);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
  document.getElementById('typingIndicator')?.remove();
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = '';
  chatInput.style.height = 'auto';
  sendBtn.disabled = true;

  appendMessage('user', text);
  showTyping();

  try {
    const res = await fetch(`${API}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Request failed');

    sessionId = data.session_id;
    removeTyping();
    appendMessage('assistant', data.response);
  } catch (err) {
    removeTyping();
    appendMessage('assistant', `⚠️ Error: ${err.message}. Please check the server is running.`);
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
chatInput.addEventListener('input', () => {
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
});

clearChatBtn.addEventListener('click', async () => {
  if (sessionId) {
    await fetch(`${API}/api/chat/${sessionId}`, { method: 'DELETE' }).catch(() => {});
    sessionId = null;
  }
  chatMessages.innerHTML = `
    <div class="msg assistant">
      <div class="msg-avatar">🤖</div>
      <div class="msg-bubble">Conversation cleared. How can I help you?</div>
    </div>`;
});

/* ──────────────────────────────────────────────────────────────
   Severity helpers
────────────────────────────────────────────────────────────── */
const SEV_SLA = { P1: '15 min SLA', P2: '2 hr SLA', P3: '8 hr SLA', P4: '3 day SLA' };

function severityBadge(severity, label) {
  return `<span class="severity-badge sev-${severity}">${severity} · ${label}</span>`;
}

/* ──────────────────────────────────────────────────────────────
   Incident analysis result renderer
────────────────────────────────────────────────────────────── */
function renderResult(data) {
  const steps = data.troubleshooting_steps
    .map((s, i) => `<li class="step-item"><div class="step-num">${i + 1}</div><div class="step-text">${escHtml(s)}</div></li>`)
    .join('');

  const confidence = Math.round(data.confidence_score * 100);
  const modeTag = data.ai_mode === 'ollama'
    ? '<span class="ai-mode-tag mode-ollama">⚡ Ollama AI</span>'
    : '<span class="ai-mode-tag mode-mock">🔶 Mock mode</span>';

  return `
    <div class="result-card">
      <div class="result-header">
        <div class="result-title">Incident Analysis</div>
        ${modeTag}
      </div>
      <div class="result-body">

        <div class="result-meta">
          <div class="meta-item">
            <div class="meta-label">Severity</div>
            <div class="meta-value">${severityBadge(data.severity, data.severity_label)}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Category</div>
            <div class="meta-value">${escHtml(data.category)}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Assignment Group</div>
            <div class="meta-value" style="font-size:13px">${escHtml(data.assignment_group)}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Est. Resolution</div>
            <div class="meta-value" style="font-size:13px">${escHtml(data.estimated_resolution_time)}</div>
          </div>
        </div>

        <div>
          <div class="section-label">AI Summary</div>
          <div class="summary-text">${escHtml(data.summary)}</div>
        </div>

        <div>
          <div class="section-label">Troubleshooting Steps</div>
          <ul class="steps-list">${steps}</ul>
        </div>

        <div>
          <div class="section-label">Confidence Score</div>
          <div class="confidence-bar">
            <div class="bar-track">
              <div class="bar-fill" style="width:${confidence}%"></div>
            </div>
            <div class="confidence-label">${confidence}%</div>
          </div>
        </div>

      </div>
    </div>`;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ──────────────────────────────────────────────────────────────
   Incident Analyzer form
────────────────────────────────────────────────────────────── */
const analyzerResult = document.getElementById('analyzerResult');
const analyzeBtn     = document.getElementById('analyzeBtn');

async function runAnalysis(title, description, affectedUsers) {
  analyzerResult.innerHTML = `
    <div class="loading-overlay">
      <div class="spinner"></div>
      <span>Analyzing incident…</span>
    </div>`;

  try {
    const res = await fetch(`${API}/api/incidents/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description, affected_users: Number(affectedUsers) }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Analysis failed');
    analyzerResult.innerHTML = renderResult(data);
  } catch (err) {
    analyzerResult.innerHTML = `<div class="loading-overlay" style="color:var(--p1)">⚠️ ${escHtml(err.message)}</div>`;
  }
}

analyzeBtn.addEventListener('click', () => {
  const title = document.getElementById('incTitle').value.trim();
  const description = document.getElementById('incDescription').value.trim();
  const users = document.getElementById('incUsers').value;

  if (!title || title.length < 3) { showToast('Please enter an incident title (min 3 characters)', true); return; }
  if (!description || description.length < 10) { showToast('Please enter a description (min 10 characters)', true); return; }

  runAnalysis(title, description, users);
});

/* ──────────────────────────────────────────────────────────────
   Sample incidents
────────────────────────────────────────────────────────────── */
async function loadSamples() {
  try {
    const res = await fetch(`${API}/api/incidents/samples`);
    samples = await res.json();

    const select = document.getElementById('sampleSelect');
    samples.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = `${s.id} — ${s.title}`;
      select.appendChild(opt);
    });

    renderSamplesGrid();
  } catch {
    console.warn('Could not load samples');
  }
}

function renderSamplesGrid() {
  const grid = document.getElementById('samplesGrid');
  grid.innerHTML = samples.map(s => `
    <div class="sample-card">
      <div class="sample-header">
        <div>
          <div class="sample-id">${escHtml(s.id)}</div>
          <div class="sample-title">${escHtml(s.title)}</div>
        </div>
      </div>
      <div class="sample-desc">${escHtml(s.description)}</div>
      <div class="sample-footer">
        <span class="category-tag">${escHtml(s.category_hint)}</span>
        <span class="users-tag">👥 ${s.affected_users} user${s.affected_users !== 1 ? 's' : ''}</span>
      </div>
      <button class="btn btn-primary" style="margin-top:4px;width:100%;font-size:12px;padding:7px"
        onclick="analyzeFromSample('${escHtml(s.id)}')">
        Analyze →
      </button>
    </div>`).join('');
}

function analyzeFromSample(id) {
  const sample = samples.find(s => s.id === id);
  if (!sample) return;

  // Switch to analyzer tab
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelector('[data-tab="analyzer"]').classList.add('active');
  document.getElementById('tab-analyzer').classList.add('active');

  // Pre-fill form
  document.getElementById('incTitle').value = sample.title;
  document.getElementById('incDescription').value = sample.description;
  document.getElementById('incUsers').value = sample.affected_users;

  runAnalysis(sample.title, sample.description, sample.affected_users);
}

document.getElementById('loadSampleBtn').addEventListener('click', () => {
  const id = document.getElementById('sampleSelect').value;
  if (!id) { showToast('Please select a sample incident first', true); return; }
  analyzeFromSample(id);
});

/* ──────────────────────────────────────────────────────────────
   Toast
────────────────────────────────────────────────────────────── */
function showToast(msg, isError = false) {
  const t = document.createElement('div');
  t.className = `toast${isError ? ' error' : ''}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

/* ──────────────────────────────────────────────────────────────
   Init
────────────────────────────────────────────────────────────── */
checkHealth();
loadSamples();
