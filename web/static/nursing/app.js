(function () {
  'use strict';

  const STRINGS = {
    te: {
      heroTitle: 'Telangana Staff Nurse',
      heroSubtitle: 'రోజుకి 5 questions — app install అవసరం లేదు',
      introText: 'ఒక రోజుకి కేవలం 5 ప్రశ్నలతో మీ exam preparation మొదలుపెట్టండి. ఫోన్‌లో చోటు తక్కువ ఉన్నవారికి కూడా సులభం.',
      startBtn: 'Start 5 Questions',
      nextBtn: 'Next →',
      resultTitle: 'Great effort!',
      resultMessage: 'రోజుకి కొద్దిగా practice చేస్తే results వస్తాయి.',
      retryBtn: 'Try Again',
      installBtn: 'Add to Home Screen',
      shareBtn: 'Share Score',
      offlineText: 'You are offline. The daily practice will load from your phone.',
      correct: 'Correct!',
      wrong: 'Wrong. Correct answer:',
      shareText: (score, total) => `I scored ${score}/${total} in today's Telangana Staff Nurse practice on MathWise. Can you beat me?`,
    },
    en: {
      heroTitle: 'Telangana Staff Nurse',
      heroSubtitle: '5 questions a day — no app install needed',
      introText: 'Start your exam preparation with just 5 questions a day. Easy even if your phone has low storage.',
      startBtn: 'Start 5 Questions',
      nextBtn: 'Next →',
      resultTitle: 'Great effort!',
      resultMessage: 'A little practice every day brings results.',
      retryBtn: 'Try Again',
      installBtn: 'Add to Home Screen',
      shareBtn: 'Share Score',
      offlineText: 'You are offline. The daily practice will load from your phone.',
      correct: 'Correct!',
      wrong: 'Wrong. Correct answer:',
      shareText: (score, total) => `I scored ${score}/${total} in today's Telangana Staff Nurse practice on MathWise. Can you beat me?`,
    },
  };

  let lang = 'te';
  let questions = [];
  let currentIndex = 0;
  let selectedAnswer = null;
  let score = 0;
  let answered = false;
  let deferredPrompt = null;

  const $ = (id) => document.getElementById(id);

  function t(key, ...args) {
    const s = STRINGS[lang][key];
    return typeof s === 'function' ? s(...args) : s;
  }

  function setLang(next) {
    lang = next;
    $('btnTe').classList.toggle('active', lang === 'te');
    $('btnTe').setAttribute('aria-pressed', lang === 'te');
    $('btnEn').classList.toggle('active', lang === 'en');
    $('btnEn').setAttribute('aria-pressed', lang === 'en');
    $('heroTitle').textContent = t('heroTitle');
    $('heroSubtitle').textContent = t('heroSubtitle');
    $('introText').textContent = t('introText');
    $('startBtn').textContent = t('startBtn');
    $('nextBtn').textContent = t('nextBtn');
    $('resultTitle').textContent = t('resultTitle');
    $('resultMessage').textContent = t('resultMessage');
    $('retryBtn').textContent = t('retryBtn');
    $('installBtn').textContent = t('installBtn');
    $('shareBtn').textContent = t('shareBtn');
    $('offlineText').textContent = t('offlineText');
  }

  async function loadQuestions() {
    try {
      const response = await fetch('/api/nursing/questions?limit=5');
      if (!response.ok) throw new Error('API error');
      const data = await response.json();
      if (Array.isArray(data) && data.length) return data;
      throw new Error('Empty API response');
    } catch (err) {
      console.warn('API failed, using fallback', err);
      try {
        const response = await fetch('daily.json');
        const data = await response.json();
        return data.questions || [];
      } catch (err2) {
        console.error('Fallback failed', err2);
        return [];
      }
    }
  }

  function shuffleOptions(question) {
    const options = question.options.map((opt, idx) => ({ text: opt, key: String.fromCharCode(65 + idx) }));
    // Keep original order for v1 to avoid answer-key mismatch; in v2 shuffle with mapped keys.
    return options;
  }

  function renderQuestion() {
    answered = false;
    selectedAnswer = null;
    const q = questions[currentIndex];
    $('questionBox').textContent = q.question;
    $('progressText').textContent = `${currentIndex + 1} / ${questions.length}`;
    $('progressBar').style.width = `${((currentIndex + 1) / questions.length) * 100}%`;

    const optionsBox = $('optionsBox');
    optionsBox.innerHTML = '';
    const options = shuffleOptions(q);
    options.forEach((opt) => {
      const btn = document.createElement('button');
      btn.className = 'option';
      btn.textContent = opt.text;
      btn.setAttribute('aria-label', `Option ${opt.key}`);
      btn.addEventListener('click', () => selectOption(opt.key, btn));
      optionsBox.appendChild(btn);
    });

    $('feedbackBox').classList.add('hidden');
    $('nextBtn').classList.add('hidden');
  }

  function selectOption(key, btn) {
    if (answered) return;
    answered = true;
    selectedAnswer = key;
    const q = questions[currentIndex];
    const correct = q.correct_answer;
    const isCorrect = key === correct;
    if (isCorrect) score += 1;

    document.querySelectorAll('.option').forEach((b) => {
      b.disabled = true;
      const optKey = b.getAttribute('aria-label').replace('Option ', '');
      if (optKey === correct) b.classList.add('correct');
      if (optKey === key && !isCorrect) {
        b.classList.add('wrong');
        btn.classList.add('selected');
      }
    });

    $('feedbackBox').innerHTML = isCorrect
      ? `<strong>${t('correct')}</strong> ${q.explanation}`
      : `<strong>${t('wrong')} ${correct}</strong>. ${q.explanation}`;
    $('feedbackBox').classList.remove('hidden');
    $('nextBtn').classList.remove('hidden');
  }

  function showResult() {
    $('quiz').classList.add('hidden');
    $('result').classList.remove('hidden');
    $('resultScore').textContent = `${score} / ${questions.length}`;
    $('resultMessage').textContent = t('resultMessage');
  }

  function startQuiz() {
    loadQuestions().then((data) => {
      if (!data.length) {
        $('intro').classList.add('hidden');
        $('offline').classList.remove('hidden');
        return;
      }
      questions = data;
      currentIndex = 0;
      score = 0;
      $('intro').classList.add('hidden');
      $('result').classList.add('hidden');
      $('quiz').classList.remove('hidden');
      renderQuestion();
    });
  }

  function shareScore() {
    const text = t('shareText', score, questions.length) + ' ' + window.location.href;
    if (navigator.share) {
      navigator.share({ title: 'MathWise Nursing', text, url: window.location.href }).catch(() => {});
    } else {
      const waUrl = 'https://wa.me/?text=' + encodeURIComponent(text);
      window.open(waUrl, '_blank');
    }
  }

  function installPWA() {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then(() => { deferredPrompt = null; });
    }
  }

  // Event bindings
  $('btnTe').addEventListener('click', () => setLang('te'));
  $('btnEn').addEventListener('click', () => setLang('en'));
  $('startBtn').addEventListener('click', startQuiz);
  $('retryBtn').addEventListener('click', startQuiz);
  $('shareBtn').addEventListener('click', shareScore);
  $('installBtn').addEventListener('click', installPWA);
  $('nextBtn').addEventListener('click', () => {
    currentIndex += 1;
    if (currentIndex >= questions.length) {
      showResult();
    } else {
      renderQuestion();
    }
  });

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    $('installBtn').classList.remove('hidden');
  });

  // Register service worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('sw.js', { scope: '/nursing/' })
        .then((reg) => console.log('SW registered', reg.scope))
        .catch((err) => console.warn('SW registration failed', err));
    });
  }

  setLang('te');
})();
