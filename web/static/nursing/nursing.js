/* Dr. Math Nursing — frontend logic for diagnostic, practice, and mock tests. */
(function () {
  'use strict';

  const STORAGE_ATTEMPTS = 'nursing_attempts';
  const STORAGE_CAPABILITY = 'nursing_capability_map';
  const STORAGE_LANG = 'nursing_language';

  let glossary = {};
  let currentQuestions = [];
  let currentMode = 'practice';
  let startTime = null;

  // -------------------------------------------------------------------------
  // Utilities
  // -------------------------------------------------------------------------

  function $(sel) { return document.querySelector(sel); }
  function $$ (sel) { return Array.from(document.querySelectorAll(sel)); }

  function getUrlParams() {
    return new URLSearchParams(window.location.search);
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  function shuffle(array) {
    const a = array.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  // -------------------------------------------------------------------------
  // Glossary tooltips
  // -------------------------------------------------------------------------

  function loadGlossary() {
    fetch('/static/nursing/glossary.json')
      .then(r => r.json())
      .then(data => { glossary = data; applyTooltips(); })
      .catch(() => { glossary = {}; });
  }

  function applyTooltips() {
    const terms = Object.keys(glossary).sort((a, b) => b.length - a.length);
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
    const nodes = [];
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement && node.parentElement.classList.contains('tooltip')) continue;
      nodes.push(node);
    }
    nodes.forEach(textNode => {
      let text = textNode.textContent;
      let changed = false;
      terms.forEach(term => {
        const re = new RegExp(`\\b${term}\\b`, 'gi');
        if (re.test(text)) {
          changed = true;
          text = text.replace(re, match => `<span class="tooltip" data-te="${glossary[term.toLowerCase()]}">${match}</span>`);
        }
      });
      if (changed) {
        const span = document.createElement('span');
        span.innerHTML = text;
        textNode.parentNode.replaceChild(span, textNode);
      }
    });

    $$('.tooltip').forEach(el => {
      el.addEventListener('mouseenter', showGlossaryPopup);
      el.addEventListener('mouseleave', hideGlossaryPopup);
    });
  }

  function showGlossaryPopup(e) {
    const term = e.target.textContent.toLowerCase();
    const te = glossary[term];
    if (!te) return;
    const popup = document.createElement('div');
    popup.className = 'glossary-popup';
    popup.textContent = te;
    popup.id = 'active-glossary-popup';
    document.body.appendChild(popup);
    const rect = e.target.getBoundingClientRect();
    popup.style.left = `${rect.left + window.scrollX}px`;
    popup.style.top = `${rect.top + window.scrollY - popup.offsetHeight - 4}px`;
  }

  function hideGlossaryPopup() {
    const popup = $('#active-glossary-popup');
    if (popup) popup.remove();
  }

  // -------------------------------------------------------------------------
  // Language toggle
  // -------------------------------------------------------------------------

  function initLanguage() {
    const saved = localStorage.getItem(STORAGE_LANG) || 'en';
    applyLanguage(saved);
    const btn = $('#lang-toggle');
    if (btn) {
      btn.textContent = saved === 'te' ? 'English' : 'తెలుగు';
      btn.addEventListener('click', () => {
        const next = localStorage.getItem(STORAGE_LANG) === 'te' ? 'en' : 'te';
        localStorage.setItem(STORAGE_LANG, next);
        applyLanguage(next);
        btn.textContent = next === 'te' ? 'English' : 'తెలుగు';
      });
    }
  }

  function applyLanguage(lang) {
    $$('[data-te]').forEach(el => {
      if (!el.dataset.en) el.dataset.en = el.textContent;
      el.textContent = lang === 'te' && el.dataset.te ? el.dataset.te : el.dataset.en;
    });
  }

  // -------------------------------------------------------------------------
  // Quiz rendering
  // -------------------------------------------------------------------------

  function renderQuestion(q, index, total, showFeedback) {
    const container = document.createElement('div');
    container.className = 'card question-card';
    container.dataset.questionId = q.id;
    container.dataset.subjectId = q.subject_id;
    container.dataset.topicId = q.topic_id;
    container.dataset.cognitiveLevel = q.cognitive_level;
    container.dataset.correctAnswer = q.correct_answer;

    const meta = document.createElement('p');
    meta.style.fontSize = '0.85rem';
    meta.style.color = 'var(--color-muted)';
    meta.textContent = `Q${index + 1}/${total} • ${q.cognitive_level} • ${q.context}`;
    container.appendChild(meta);

    const stem = document.createElement('p');
    stem.innerHTML = `<strong>Q${index + 1}.</strong> ${escapeHtml(q.question)}`;
    container.appendChild(stem);

    const opts = document.createElement('div');
    q.options.forEach(opt => {
      const btn = document.createElement('button');
      btn.className = 'option';
      btn.textContent = opt;
      btn.dataset.value = opt.charAt(0);
      if (!showFeedback) {
        btn.addEventListener('click', () => selectOption(container, btn));
      }
      opts.appendChild(btn);
    });
    container.appendChild(opts);

    if (showFeedback) {
      markFeedback(container, q.correct_answer);
    }

    return container;
  }

  function selectOption(card, btn) {
    card.querySelectorAll('.option').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
  }

  function markFeedback(card, correctAnswer) {
    card.querySelectorAll('.option').forEach(btn => {
      const val = btn.dataset.value;
      btn.disabled = true;
      if (val === correctAnswer) btn.classList.add('correct');
      else if (btn.classList.contains('selected')) btn.classList.add('wrong');
    });
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function collectAttempts(questions) {
    const attempts = [];
    const now = Date.now();
    const elapsed = startTime ? Math.max(1, Math.floor((now - startTime) / 1000)) : 30;
    const perQuestion = Math.floor(elapsed / Math.max(1, questions.length));
    const globalConfidence = $('#confidence') ? parseInt($('#confidence').value, 10) : 3;

    $$('.question-card').forEach((card, idx) => {
      const selected = card.querySelector('.option.selected');
      const selectedOption = selected ? selected.dataset.value : '';
      const correct = selectedOption === card.dataset.correctAnswer;
      const confidenceInput = card.querySelector('input[type="range"]');
      const confidence = confidenceInput ? parseInt(confidenceInput.value, 10) : globalConfidence;

      attempts.push({
        question_id: parseInt(card.dataset.questionId, 10),
        selected_option: selectedOption,
        is_correct: correct,
        time_seconds: perQuestion,
        confidence: confidence,
        subject_id: card.dataset.subjectId,
        topic_id: card.dataset.topicId,
        cognitive_level: card.dataset.cognitiveLevel,
      });
    });
    return attempts;
  }

  // -------------------------------------------------------------------------
  // Results rendering
  // -------------------------------------------------------------------------

  function renderResults(attempts, containerId, summaryId) {
    const correct = attempts.filter(a => a.is_correct).length;
    const total = attempts.length;
    const pct = total ? Math.round((correct / total) * 100) : 0;

    const summary = $(summaryId);
    summary.innerHTML = `
      <p><strong>Score:</strong> ${correct}/${total} (${pct}%)</p>
      <p><strong>Time:</strong> ${formatTime(startTime ? Math.floor((Date.now() - startTime) / 1000) : 0)}</p>
    `;

    fetch('/api/nursing/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(attempts),
    })
      .then(r => r.json())
      .then(data => {
        saveAttempts(attempts);
        localStorage.setItem(STORAGE_CAPABILITY, JSON.stringify(data));
        renderWeakAreas(data);
      })
      .catch(err => {
        console.error('Analyze failed', err);
        saveAttempts(attempts);
      });
  }

  function renderWeakAreas(data) {
    const el = $('#weak-areas');
    if (!el || !data.topic_capabilities) return;
    const weak = data.topic_capabilities.slice(0, 3);
    const list = weak.map(t => `<li>${t.topic_id} (priority ${t.priority_score.toFixed(2)})</li>`).join('');
    el.innerHTML = `<h3>Top weak areas</h3><ul>${list}</ul>`;
  }

  function saveAttempts(attempts) {
    const existing = JSON.parse(localStorage.getItem(STORAGE_ATTEMPTS) || '[]');
    existing.push(...attempts);
    localStorage.setItem(STORAGE_ATTEMPTS, JSON.stringify(existing.slice(-200)));
  }

  // -------------------------------------------------------------------------
  // Page initializers
  // -------------------------------------------------------------------------

  function initIndex() {
    fetch('/api/nursing/topics')
      .then(r => r.json())
      .then(data => {
        renderSubjectGrid(data);
        populateSubjectSelect(data);
      });

    const subjectSelect = $('#subject-select');
    const topicSelect = $('#topic-select');
    const practiceLink = $('#practice-link');

    subjectSelect.addEventListener('change', () => {
      topicSelect.innerHTML = '<option value="">-- Select topic --</option>';
      topicSelect.disabled = !subjectSelect.value;
      if (!subjectSelect.value) return;
      fetch('/api/nursing/topics')
        .then(r => r.json())
        .then(data => {
          const topics = data.topics_by_subject[subjectSelect.value] || [];
          topics.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.textContent = t;
            topicSelect.appendChild(opt);
          });
          updatePracticeLink();
        });
    });

    topicSelect.addEventListener('change', updatePracticeLink);
    $('#cognitive-select').addEventListener('change', updatePracticeLink);
    $('#context-select').addEventListener('change', updatePracticeLink);

    function updatePracticeLink() {
      const params = new URLSearchParams();
      if (subjectSelect.value) params.set('subject_id', subjectSelect.value);
      if (topicSelect.value) params.set('topic_id', topicSelect.value);
      const cog = $('#cognitive-select').value;
      const ctx = $('#context-select').value;
      if (cog) params.set('cognitive_level', cog);
      if (ctx) params.set('context', ctx);
      practiceLink.href = '/nursing/practice?' + params.toString();
    }
  }

  function renderSubjectGrid(data) {
    const grid = $('#subject-grid');
    grid.innerHTML = '';
    data.subjects.forEach(subjectId => {
      const count = data.counts[subjectId] || 0;
      const div = document.createElement('div');
      div.className = 'subject-card';
      div.innerHTML = `<h3>${subjectId.replace(/_/g, ' ')}</h3><p>${count} questions</p>`;
      grid.appendChild(div);
    });
  }

  function populateSubjectSelect(data) {
    const select = $('#subject-select');
    if (!select) return;
    data.subjects.forEach(subjectId => {
      const opt = document.createElement('option');
      opt.value = subjectId;
      opt.textContent = subjectId.replace(/_/g, ' ');
      select.appendChild(opt);
    });
  }

  function initDiagnostic() {
    currentMode = 'diagnostic';
    fetch('/api/nursing/diagnostic/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ num_questions: 20 }) })
      .then(r => r.json())
      .then(data => {
        currentQuestions = data.questions;
        renderQuiz(currentQuestions, 'quiz-container', true);
        $('#confidence-card').style.display = 'block';
        $('#submit-btn').style.display = 'inline-block';
        startTime = Date.now();
      });

    $('#submit-btn').addEventListener('click', () => {
      const attempts = collectAttempts(currentQuestions);
      renderResults(attempts, 'quiz-container', '#result-summary');
      $('#submit-btn').style.display = 'none';
      $('#confidence-card').style.display = 'none';
      $('#result-card').style.display = 'block';
    });
  }

  function initPractice() {
    currentMode = 'practice';
    const params = getUrlParams();
    const info = $('#practice-info');
    const parts = [];
    if (params.get('subject_id')) parts.push(params.get('subject_id').replace(/_/g, ' '));
    if (params.get('topic_id')) parts.push(params.get('topic_id').replace(/_/g, ' '));
    if (params.get('cognitive_level')) parts.push(params.get('cognitive_level'));
    if (params.get('context')) parts.push(params.get('context'));
    info.textContent = parts.length ? 'Practice: ' + parts.join(' / ') : 'Mixed practice';
    info.dataset.en = info.textContent;

    const query = new URLSearchParams(params);
    fetch('/api/nursing/questions?' + query.toString())
      .then(r => r.json())
      .then(data => {
        currentQuestions = data;
        renderQuiz(currentQuestions, 'quiz-container', true);
        startTime = Date.now();
      });

    $('#pdf-btn').addEventListener('click', () => {
      const attempts = collectAttempts(currentQuestions);
      fetch('/api/nursing/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ attempts, top_n: 3 }),
      })
        .then(r => r.blob())
        .then(blob => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'weak-area-practice.html';
          a.click();
          window.URL.revokeObjectURL(url);
        });
    });
  }

  function initMock() {
    currentMode = 'mock';
    fetch('/api/nursing/mock/start', { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        currentQuestions = data.questions;
        renderQuiz(currentQuestions, 'quiz-container', false);
        $('#submit-btn').style.display = 'inline-block';
        startTime = Date.now();
        startMockTimer(60 * 60);
      });

    $('#submit-btn').addEventListener('click', () => {
      const attempts = collectAttempts(currentQuestions);
      renderResults(attempts, 'quiz-container', '#result-summary');
      $('#submit-btn').style.display = 'none';
      $('#result-card').style.display = 'block';
    });
  }

  function startMockTimer(seconds) {
    const el = $('#timer');
    let remaining = seconds;
    const interval = setInterval(() => {
      remaining--;
      el.textContent = formatTime(remaining);
      if (remaining <= 0) {
        clearInterval(interval);
        alert('Time is up. Your mock test will be submitted.');
        $('#submit-btn').click();
      }
    }, 1000);
  }

  function renderQuiz(questions, containerId, showFeedback) {
    const container = $('#' + containerId);
    container.innerHTML = '';
    questions.forEach((q, idx) => {
      const card = renderQuestion(q, idx, questions.length, showFeedback);
      container.appendChild(card);
    });
    applyTooltips();
  }

  // -------------------------------------------------------------------------
  // Boot
  // -------------------------------------------------------------------------

  document.addEventListener('DOMContentLoaded', () => {
    loadGlossary();
    initLanguage();

    const path = window.location.pathname;
    if (path === '/nursing' || path === '/nursing/') initIndex();
    else if (path.startsWith('/nursing/diagnostic')) initDiagnostic();
    else if (path.startsWith('/nursing/practice')) initPractice();
    else if (path.startsWith('/nursing/mock')) initMock();
  });
})();
