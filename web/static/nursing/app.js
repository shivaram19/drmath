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
      consentTitle: 'We only collect anonymous data if you agree.',
      consentPrivacy: 'Read privacy notice',
      consentAgree: 'I agree',
      consentDecline: 'Not now',
      consentManage: 'Manage consent',
      surveyBannerText: 'మీకు 30 సెకన్ల సర్వే సహాయం చేయండి.',
      surveyOpenBtn: 'సర్వే తీసుకోండి',
      surveyTitle: 'త్వరిత సర్వే',
      surveyInterestedLabel: 'ఉచిత రోజువారీ 5 ప్రశ్నల నర్సింగ్ క్విజ్ ఉపయోగిస్తారా?',
      surveyChannelLabel: 'ఏ చానెల్ ఇష్టం?',
      surveyCadenceLabel: 'ఎంత తరచుగా?',
      surveyChallengeLabel: 'పెద్ద సమస్య ఏమిటి?',
      surveyOtherLabel: 'మరేదైనా (ఐచ్ఛికం)',
      surveySubmit: 'Submit చేయండి',
      surveyCancel: 'రద్దు చేయండి',
      surveyNote: 'ఫోన్ నంబర్ లేదా వ్యక్తిగత వివరాలు సేకరించబడవు.',
      surveyThanks: 'సహాయానికి ధన్యవాదాలు!',
      apkPromptTitle: 'Full app download చేసుకోండి',
      apkPromptBody: 'మరిన్ని mock tests, PDFs, daily reminders కోసం MathWise app install చేసుకోండి.',
      apkPromptBtn: 'Android app download',
      apkPromptDismiss: 'తర్వాత చూద్దాం',
      syncSaved: 'సేవ్ చేయబడింది',
      syncPending: 'సింక్ కావలసి ఉంది',
      syncError: 'సింక్ విఫలమైంది',
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
      consentTitle: 'We only collect anonymous data if you agree.',
      consentPrivacy: 'Read privacy notice',
      consentAgree: 'I agree',
      consentDecline: 'Not now',
      consentManage: 'Manage consent',
      surveyBannerText: 'Help us improve — 30 sec survey.',
      surveyOpenBtn: 'Take survey',
      surveyTitle: 'Quick survey',
      surveyInterestedLabel: 'Would you use a free daily 5-question nursing quiz?',
      surveyChannelLabel: 'Preferred channel',
      surveyCadenceLabel: 'How often?',
      surveyChallengeLabel: 'Biggest exam-prep challenge',
      surveyOtherLabel: 'Anything else? (optional)',
      surveySubmit: 'Submit',
      surveyCancel: 'Cancel',
      surveyNote: 'No phone number or personal details are collected.',
      surveyThanks: 'Thank you for helping us improve MathWise Nursing!',
      apkPromptTitle: 'Get the full app',
      apkPromptBody: 'Install MathWise for full mock tests, PDFs, and daily reminders.',
      apkPromptBtn: 'Download Android app',
      apkPromptDismiss: 'Maybe later',
      syncSaved: 'Saved',
      syncPending: 'Pending sync',
      syncError: 'Sync failed',
    },
  };

  const CONSENT_KEY = 'mw_privacy_consent';
  const CONSENT_VERSION = '2026-06-28';
  const COMPLETED_KEY = 'mw_nursing_completed';
  const BANNER_DISMISSED_KEY = 'mw_nursing_apk_banner_dismissed';
  const UTM_KEY = 'mw_utm';
  const SURVEY_COMPLETED_KEY = 'mw_nursing_survey_completed';
  const SURVEY_DISMISSED_AT_KEY = 'mw_nursing_survey_dismissed_at';
  const SURVEY_DISMISS_DAYS = 7;

  const DB_NAME = 'drmath_nursing';
  const DB_VERSION = 3;
  const ATTEMPTS_STORE = 'attempts';
  const SYNC_QUEUE_STORE = 'sync_queue';
  const QUESTION_STATS_STORE = 'question_stats';
  const CONCEPT_CACHE_STORE = 'concept_cache';
  const SESSION_ID_KEY = 'mw_nursing_session_id';
  const DAY_MS = 24 * 60 * 60 * 1000;
  const UTM_FIELDS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
  const DEFAULT_UTM = {
    utm_source: 'web_nursing',
    utm_medium: 'result_cta',
    utm_campaign: 'nursing_full_app_install',
    utm_content: 'v1',
  };

  let lang = 'te';
  let questions = [];
  let currentIndex = 0;
  let selectedAnswer = null;
  let score = 0;
  let answered = false;
  let deferredPrompt = null;
  let quizAttempts = [];

  const $ = (id) => document.getElementById(id);

  function t(key, ...args) {
    const s = STRINGS[lang][key];
    return typeof s === 'function' ? s(...args) : s;
  }

  function getConsent() {
    try {
      return JSON.parse(localStorage.getItem(CONSENT_KEY));
    } catch {
      return null;
    }
  }

  function hasConsent() {
    const c = getConsent();
    return c && c.version === CONSENT_VERSION && c.accepted === true;
  }

  function recordConsent(accepted) {
    const record = {
      version: CONSENT_VERSION,
      accepted: accepted === true,
      timestamp: new Date().toISOString(),
    };
    try {
      localStorage.setItem(CONSENT_KEY, JSON.stringify(record));
    } catch {
      // Private mode or storage disabled — ignore.
    }
    updateConsentUI();
  }

  function withdrawConsent() {
    recordConsent(false);
    showConsentBanner();
  }

  function updateConsentUI() {
    const banner = $('consentBanner');
    if (hasConsent()) {
      banner.classList.add('hidden');
    }
  }

  function showConsentBanner() {
    const banner = $('consentBanner');
    $('consentText').innerHTML = `${t('consentTitle')} <a href="privacy">${t('consentPrivacy')}</a>.`;
    $('consentAgree').textContent = t('consentAgree');
    $('consentDecline').textContent = t('consentDecline');
    $('manageConsentLink').textContent = t('consentManage');
    banner.classList.remove('hidden');
  }

  // ---------------------------------------------------------------------------
  // UTM / campaign helpers
  // ---------------------------------------------------------------------------

  function parseUtmFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const parsed = {};
    let hasAny = false;
    UTM_FIELDS.forEach((field) => {
      const value = params.get(field);
      if (value) {
        parsed[field] = value;
        hasAny = true;
      }
    });
    return hasAny ? parsed : null;
  }

  function getStoredUtm() {
    try {
      const raw = sessionStorage.getItem(UTM_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function storeUtm(utm) {
    try {
      sessionStorage.setItem(UTM_KEY, JSON.stringify(utm));
    } catch {
      // Storage disabled — ignore.
    }
  }

  function getUtmParams() {
    const fromUrl = parseUtmFromUrl();
    if (fromUrl) {
      storeUtm(fromUrl);
      return { ...DEFAULT_UTM, ...fromUrl };
    }
    const stored = getStoredUtm();
    return { ...DEFAULT_UTM, ...(stored || {}) };
  }

  function buildApkUrl(overrides = {}) {
    const utm = { ...getUtmParams(), ...overrides };
    const qs = new URLSearchParams();
    UTM_FIELDS.forEach((field) => {
      const value = utm[field];
      if (value && typeof value === 'string') {
        qs.set(field, value);
      }
    });
    const query = qs.toString();
    return '/mathwise.apk' + (query ? `?${query}` : '');
  }

  // ---------------------------------------------------------------------------
  // APK conversion prompt
  // ---------------------------------------------------------------------------

  const PHONE_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12" y2="18.01"></line></svg>`;

  function renderPromptContent(dismissible) {
    return `
      <div class="apk-prompt-icon" aria-hidden="true">${PHONE_ICON}</div>
      <div class="apk-prompt-text">
        <strong data-key="apkPromptTitle">${t('apkPromptTitle')}</strong>
        <span data-key="apkPromptBody">${t('apkPromptBody')}</span>
      </div>
      <a id="apkPromptBtn" class="primary-btn" href="#" data-key="apkPromptBtn">${t('apkPromptBtn')}</a>
      ${dismissible ? `<button id="apkPromptDismiss" class="secondary-btn small" data-key="apkPromptDismiss">${t('apkPromptDismiss')}</button>` : ''}
    `;
  }

  function bindPromptEvents(container, placement, overrides, dismissible) {
    const btn = container.querySelector('#apkPromptBtn');
    const url = buildApkUrl(overrides);
    btn.setAttribute('href', url);
    btn.setAttribute('download', 'mathwise.apk');
    btn.addEventListener('click', () => {
      trackEvent('apk_download_clicked', {
        placement,
        ...getUtmParams(),
        ...overrides,
      });
    });

    if (dismissible) {
      const dismiss = container.querySelector('#apkPromptDismiss');
      dismiss.addEventListener('click', () => {
        try {
          localStorage.setItem(BANNER_DISMISSED_KEY, '1');
        } catch {}
        container.classList.add('hidden');
      });
    }
  }

  function showApkPrompt(containerId, placement, overrides = {}, dismissible = false) {
    const container = $(containerId);
    if (!container) return;
    container.innerHTML = renderPromptContent(dismissible);
    container.classList.remove('hidden');
    bindPromptEvents(container, placement, overrides, dismissible);
    trackEvent('apk_prompt_shown', {
      placement,
      ...getUtmParams(),
      ...overrides,
    });
  }

  function tryShowLandingBanner() {
    try {
      if (!localStorage.getItem(COMPLETED_KEY)) return;
      if (localStorage.getItem(BANNER_DISMISSED_KEY)) return;
    } catch {
      return;
    }
    showApkPrompt('apkPromptBanner', 'landing_banner', { utm_medium: 'landing_banner', utm_content: 'returning_user' }, true);
  }

  function tryShowResultPrompt() {
    showApkPrompt('apkPromptResult', 'result_cta', { utm_medium: 'result_cta', utm_content: 'after_quiz' }, false);
  }

  // ---------------------------------------------------------------------------
  // Discovery survey (Phase 10.9a)
  // ---------------------------------------------------------------------------

  function shouldShowSurveyBanner() {
    try {
      if (localStorage.getItem(SURVEY_COMPLETED_KEY)) return false;
      const dismissedAt = localStorage.getItem(SURVEY_DISMISSED_AT_KEY);
      if (dismissedAt) {
        const elapsed = Date.now() - parseInt(dismissedAt, 10);
        if (elapsed < SURVEY_DISMISS_DAYS * 24 * 60 * 60 * 1000) return false;
      }
    } catch {
      return false;
    }
    return true;
  }

  function showSurveyBanner() {
    const banner = $('surveyBanner');
    if (!banner || !shouldShowSurveyBanner()) return;
    $('surveyBannerText').textContent = t('surveyBannerText');
    $('surveyOpenBtn').textContent = t('surveySubmit').replace('Submit చేయండి', 'Take survey').replace('Submit', 'Take survey');
    $('surveyDismissBtn').textContent = t('surveyCancel');
    banner.classList.remove('hidden');
  }

  function hideSurveyBanner() {
    const banner = $('surveyBanner');
    if (banner) banner.classList.add('hidden');
  }

  function openSurveyModal() {
    $('surveyModal').classList.remove('hidden');
    hideSurveyBanner();
  }

  function closeSurveyModal() {
    $('surveyModal').classList.add('hidden');
    $('surveyForm').classList.remove('hidden');
    $('surveyThanks').classList.add('hidden');
    $('surveyForm').reset();
  }

  function markSurveyCompleted() {
    try {
      localStorage.setItem(SURVEY_COMPLETED_KEY, '1');
    } catch {}
  }

  function markSurveyDismissed() {
    try {
      localStorage.setItem(SURVEY_DISMISSED_AT_KEY, String(Date.now()));
    } catch {}
  }

  async function submitSurvey(e) {
    e.preventDefault();
    const form = $('surveyForm');
    const data = {
      interested: form.interested.value,
      preferred_channel: form.preferred_channel.value,
      cadence: form.cadence.value,
      biggest_challenge: form.biggest_challenge.value,
      other_challenge: form.other_challenge.value.trim() || null,
      language: lang,
    };

    try {
      const response = await fetch('/api/nursing/discovery-survey', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Survey save failed');
    } catch (err) {
      console.error(err);
    }

    trackEvent('discovery_survey_submitted', data);
    markSurveyCompleted();
    form.classList.add('hidden');
    $('surveyThanks').textContent = t('surveyThanks');
    $('surveyThanks').classList.remove('hidden');
    setTimeout(closeSurveyModal, 2000);
  }

  function initSurvey() {
    const banner = $('surveyBanner');
    if (!banner) return;

    $('surveyOpenBtn').addEventListener('click', openSurveyModal);
    $('surveyDismissBtn').addEventListener('click', () => {
      markSurveyDismissed();
      hideSurveyBanner();
    });
    $('surveyCancelBtn').addEventListener('click', closeSurveyModal);
    $('surveyForm').addEventListener('submit', submitSurvey);

    // Show banner after a short delay so the landing page renders first.
    setTimeout(showSurveyBanner, 1500);
  }

  // ---------------------------------------------------------------------------
  // Language / UI
  // ---------------------------------------------------------------------------

  function updateDataKeyLabels() {
    document.querySelectorAll('[data-key]').forEach((el) => {
      const key = el.dataset.key;
      if (STRINGS[lang][key]) {
        el.textContent = t(key);
      }
    });
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
    updateDataKeyLabels();
    if (!$('consentBanner').classList.contains('hidden')) {
      showConsentBanner();
    }
  }

  // ---------------------------------------------------------------------------
  // Local-first attempt store + sync queue (M1)
  // ---------------------------------------------------------------------------

  function generateId() {
    if ('crypto' in window && 'randomUUID' in crypto) return crypto.randomUUID();
    return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  }

  function getSessionId() {
    let id = null;
    try {
      id = localStorage.getItem(SESSION_ID_KEY);
    } catch {}
    if (!id) {
      id = generateId();
      try {
        localStorage.setItem(SESSION_ID_KEY, id);
      } catch {}
    }
    return id;
  }

  function openDb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(ATTEMPTS_STORE)) {
          db.createObjectStore(ATTEMPTS_STORE, { keyPath: 'client_attempt_id' });
        }
        if (!db.objectStoreNames.contains(SYNC_QUEUE_STORE)) {
          db.createObjectStore(SYNC_QUEUE_STORE, { keyPath: 'client_attempt_id' });
        }
        if (!db.objectStoreNames.contains(QUESTION_STATS_STORE)) {
          db.createObjectStore(QUESTION_STATS_STORE, { keyPath: 'question_id' });
        }
        if (!db.objectStoreNames.contains(CONCEPT_CACHE_STORE)) {
          db.createObjectStore(CONCEPT_CACHE_STORE, { keyPath: 'topic_id' });
        }
      };
      req.onsuccess = (e) => resolve(e.target.result);
      req.onerror = (e) => reject(e.target.error);
    });
  }

  function dbTx(storeName, mode) {
    return openDb().then((db) => {
      const tx = db.transaction(storeName, mode);
      return { tx, store: tx.objectStore(storeName) };
    });
  }

  function dbPut(storeName, record) {
    return dbTx(storeName, 'readwrite').then(({ store }) => new Promise((resolve, reject) => {
      const req = store.put(record);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    }));
  }

  function dbGetAll(storeName) {
    return dbTx(storeName, 'readonly').then(({ store }) => new Promise((resolve, reject) => {
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    }));
  }

  function dbDelete(storeName, key) {
    return dbTx(storeName, 'readwrite').then(({ store }) => new Promise((resolve, reject) => {
      const req = store.delete(key);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    }));
  }

  function dbGet(storeName, key) {
    return dbTx(storeName, 'readonly').then(({ store }) => new Promise((resolve, reject) => {
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    }));
  }

  function updateSyncStatus(state) {
    const el = $('syncStatus');
    if (!el) return;
    el.classList.remove('hidden', 'pending', 'error', 'saved');
    if (state === 'saved') {
      el.textContent = t('syncSaved');
      el.classList.add('saved');
    } else if (state === 'pending') {
      el.textContent = t('syncPending');
      el.classList.add('pending');
    } else if (state === 'error') {
      el.textContent = t('syncError');
      el.classList.add('error');
    }
    el.classList.remove('hidden');
  }

  async function flushSyncQueue() {
    let pending = [];
    try {
      pending = await dbGetAll(SYNC_QUEUE_STORE);
    } catch (err) {
      console.error('read sync queue failed', err);
      updateSyncStatus('error');
      return;
    }
    if (!pending.length) {
      updateSyncStatus('saved');
      return;
    }
    updateSyncStatus('pending');
    try {
      const response = await fetch('/api/nursing/attempts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ attempts: pending }),
      });
      if (!response.ok) throw new Error('sync failed');
      await response.json();
      for (const item of pending) {
        await dbDelete(SYNC_QUEUE_STORE, item.client_attempt_id);
      }
      updateSyncStatus('saved');
    } catch (err) {
      console.error('flushSyncQueue failed', err);
      updateSyncStatus('error');
    }
  }

  async function recordAttempt(attempt) {
    try {
      await dbPut(ATTEMPTS_STORE, attempt);
      await dbPut(SYNC_QUEUE_STORE, attempt);
      if (navigator.onLine) {
        await flushSyncQueue();
      } else {
        updateSyncStatus('pending');
      }
    } catch (err) {
      console.error('recordAttempt failed', err);
      updateSyncStatus('error');
    }
  }

  function computeNextDue(stat, isCorrect) {
    const now = Date.now();
    let intervalDays = 1;
    if (stat && stat.next_due_at && stat.last_seen_at) {
      const previousInterval = new Date(stat.next_due_at).getTime() - new Date(stat.last_seen_at).getTime();
      intervalDays = Math.max(1, Math.round(previousInterval / DAY_MS));
    }
    if (isCorrect) intervalDays *= 2;
    else intervalDays = 1;
    return new Date(now + intervalDays * DAY_MS).toISOString();
  }

  async function recordQuestionStat(questionId, isCorrect, meta = {}) {
    let stat = await dbGet(QUESTION_STATS_STORE, questionId);
    const now = new Date().toISOString();
    if (!stat) {
      stat = {
        question_id: questionId,
        subject_id: meta.subject_id || null,
        topic_id: meta.topic_id || null,
        correct_count: 0,
        incorrect_count: 0,
        last_seen_at: now,
        next_due_at: now,
      };
    }
    stat.last_seen_at = now;
    if (isCorrect) stat.correct_count += 1;
    else stat.incorrect_count += 1;
    stat.next_due_at = computeNextDue(stat, isCorrect);
    stat.subject_id = meta.subject_id || stat.subject_id;
    stat.topic_id = meta.topic_id || stat.topic_id;
    await dbPut(QUESTION_STATS_STORE, stat);
  }

  function weaknessScore(stat) {
    if (!stat) return 0;
    const seen = stat.correct_count + stat.incorrect_count;
    if (seen === 0) return 0;
    const accuracy = stat.correct_count / seen;
    return (1 - accuracy) * 100 + seen;
  }

  async function selectDailyQuestions(candidatePool, count = 5) {
    const stats = await dbGetAll(QUESTION_STATS_STORE);
    const statMap = new Map(stats.map((s) => [s.question_id, s]));
    const now = new Date().toISOString();

    const withMeta = candidatePool.map((q) => ({
      question: q,
      stat: statMap.get(q.id) || null,
      isDue: statMap.get(q.id) && statMap.get(q.id).next_due_at <= now,
    }));

    const due = withMeta
      .filter((item) => item.isDue)
      .sort((a, b) => weaknessScore(b.stat) - weaknessScore(a.stat) || new Date(a.stat.last_seen_at) - new Date(b.stat.last_seen_at));

    const seenIds = new Set(stats.map((s) => s.question_id));
    const unseen = withMeta
      .filter((item) => !seenIds.has(item.question.id))
      .sort(() => Math.random() - 0.5);

    const nonDueSeen = withMeta
      .filter((item) => item.stat && !item.isDue)
      .sort((a, b) => weaknessScore(b.stat) - weaknessScore(a.stat) || new Date(a.stat.last_seen_at) - new Date(b.stat.last_seen_at));

    let selected = due.map((item) => item.question);
    const needWeakMinimum = Math.ceil(count * 0.3);
    const weakPool = due.concat(nonDueSeen).map((item) => item.question);
    if (selected.length < needWeakMinimum) {
      selected = weakPool.slice(0, Math.max(needWeakMinimum, count));
    } else if (selected.length > count) {
      selected = selected.slice(0, count);
    }

    const usedIds = new Set(selected.map((q) => q.id));
    const fillers = [];
    [...unseen, ...nonDueSeen, ...due].forEach((item) => {
      if (!usedIds.has(item.question.id)) fillers.push(item.question);
    });
    fillers.sort(() => Math.random() - 0.5);

    while (selected.length < count && fillers.length) {
      selected.push(fillers.shift());
    }

    return selected.slice(0, count);
  }

  async function loadQuestions() {
    try {
      const response = await fetch('/api/nursing/questions?limit=50');
      if (!response.ok) throw new Error('API error');
      const data = await response.json();
      if (Array.isArray(data) && data.length) {
        return selectDailyQuestions(data, 5);
      }
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
    quizAttempts.push({
      question_id: q.id,
      topic_id: q.topic_id || null,
      subject_id: q.subject_id || null,
      is_correct: isCorrect,
    });

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

    const attempt = {
      client_attempt_id: generateId(),
      session_id: getSessionId(),
      question_id: q.id,
      subject_id: q.subject_id || null,
      topic_id: q.topic_id || null,
      cognitive_level: q.cognitive_level || null,
      selected_option: key,
      correct_option: correct,
      is_correct: isCorrect,
      answered_at: new Date().toISOString(),
      time_seconds: null,
      confidence: null,
    };
    recordAttempt(attempt);
    recordQuestionStat(q.id, isCorrect, {
      subject_id: q.subject_id || null,
      topic_id: q.topic_id || null,
    }).catch((err) => console.error('recordQuestionStat failed', err));

    trackEvent('question_answered', {
      question_index: currentIndex,
      total: questions.length,
      selected: key,
      correct,
      is_correct: isCorrect,
      topic_id: q.topic_id || null,
    });

    $('feedbackBox').classList.remove('hidden');
    $('nextBtn').classList.remove('hidden');
  }

  function computeWeakestTopic() {
    const byTopic = {};
    quizAttempts.forEach((a) => {
      if (!a.topic_id) return;
      if (!byTopic[a.topic_id]) {
        byTopic[a.topic_id] = { correct: 0, total: 0, subject_id: a.subject_id };
      }
      byTopic[a.topic_id].total += 1;
      if (a.is_correct) byTopic[a.topic_id].correct += 1;
    });
    let weakest = null;
    let lowestAccuracy = Infinity;
    Object.entries(byTopic).forEach(([topic_id, stats]) => {
      const accuracy = stats.correct / stats.total;
      if (
        accuracy < lowestAccuracy ||
        (accuracy === lowestAccuracy && stats.total > (byTopic[weakest]?.total || 0))
      ) {
        lowestAccuracy = accuracy;
        weakest = topic_id;
      }
    });
    if (!weakest) return null;
    return { topic_id: weakest, accuracy: lowestAccuracy, ...byTopic[weakest] };
  }

  async function loadConcept(topicId) {
    const cached = await dbGet(CONCEPT_CACHE_STORE, topicId).catch(() => null);
    if (cached) return cached;
    if (!navigator.onLine) return null;
    try {
      const response = await fetch(`/api/nursing/concept?topic_id=${encodeURIComponent(topicId)}`);
      if (!response.ok) throw new Error('concept fetch failed');
      const data = await response.json();
      await dbPut(CONCEPT_CACHE_STORE, {
        topic_id: data.topic_id,
        explanation: data.explanation,
        cached_at: new Date().toISOString(),
      });
      return data;
    } catch (err) {
      console.error('loadConcept failed', err);
      return null;
    }
  }

  function renderWeakArea() {
    const box = $('weakAreaBox');
    if (!box) return;
    const weakest = computeWeakestTopic();
    if (!weakest) {
      box.classList.add('hidden');
      return;
    }
    const accuracyPct = Math.round(weakest.accuracy * 100);
    box.innerHTML = `
      <div class="weak-area">
        <p class="weak-area-title">Focus area: ${weakest.topic_id.replace(/_/g, ' ')}</p>
        <p class="weak-area-stats">Accuracy: ${accuracyPct}% (${weakest.correct}/${weakest.total})</p>
        <button id="reviewConceptBtn" class="secondary-btn small">Review concept</button>
      </div>
    `;
    box.classList.remove('hidden');
    $('reviewConceptBtn').addEventListener('click', () => showConceptModal(weakest.topic_id));
  }

  async function showConceptModal(topicId) {
    const modal = $('conceptModal');
    const content = $('conceptContent');
    const title = $('conceptTitle');
    title.textContent = topicId.replace(/_/g, ' ');
    content.textContent = 'Loading concept...';
    modal.classList.remove('hidden');
    const data = await loadConcept(topicId);
    if (data && data.explanation) {
      content.textContent = data.explanation;
    } else {
      content.textContent = 'Concept explanation not available offline. Connect to the internet and try again.';
    }
  }

  function closeConceptModal() {
    $('conceptModal').classList.add('hidden');
  }

  function showResult() {
    $('quiz').classList.add('hidden');
    $('result').classList.remove('hidden');
    $('resultScore').textContent = `${score} / ${questions.length}`;
    $('resultMessage').textContent = t('resultMessage');
    renderWeakArea();
    trackEvent('quiz_completed', { score, total: questions.length });
    try {
      localStorage.setItem(COMPLETED_KEY, '1');
    } catch {}
    tryShowResultPrompt();
  }

  function startQuiz() {
    trackEvent('landing_quiz_started');
    loadQuestions().then((data) => {
      if (!data.length) {
        $('intro').classList.add('hidden');
        $('offline').classList.remove('hidden');
        return;
      }
      questions = data;
      currentIndex = 0;
      score = 0;
      quizAttempts = [];
      $('intro').classList.add('hidden');
      $('apkPromptBanner').classList.add('hidden');
      $('result').classList.add('hidden');
      $('quiz').classList.remove('hidden');
      renderQuestion();
      if (navigator.onLine) flushSyncQueue();
      else updateSyncStatus('pending');
    });
  }

  function trackEvent(event, metadata = {}) {
    if (!hasConsent()) return;
    const payload = {
      event,
      timestamp: new Date().toISOString(),
      consent_version: CONSENT_VERSION,
      metadata,
    };
    if ('sendBeacon' in navigator) {
      navigator.sendBeacon(
        '/api/nursing/analytics',
        new Blob([JSON.stringify(payload)], { type: 'application/json' })
      );
    } else {
      fetch('/api/nursing/analytics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true,
      }).catch(() => {});
    }
  }

  function shareScore() {
    if (!hasConsent()) {
      showConsentBanner();
      // Re-bind agree button to continue sharing after consent.
      $('consentAgree').onclick = () => {
        recordConsent(true);
        shareScore();
      };
      return;
    }
    const appLink = buildApkUrl({
      utm_source: 'whatsapp_share',
      utm_medium: 'share_text',
      utm_content: 'score_share',
    });
    const text = `${t('shareText', score, questions.length)} ${window.location.href} ${appLink}`;
    trackEvent('score_shared', {
      score,
      total: questions.length,
      includes_app_link: true,
      utm_source: 'whatsapp_share',
      utm_medium: 'share_text',
      utm_campaign: getUtmParams().utm_campaign,
      utm_content: 'score_share',
    });
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
  $('consentAgree').addEventListener('click', () => recordConsent(true));
  $('consentDecline').addEventListener('click', () => {
    recordConsent(false);
    $('consentBanner').classList.add('hidden');
  });
  $('manageConsentLink').addEventListener('click', (e) => {
    e.preventDefault();
    withdrawConsent();
  });
  $('nextBtn').addEventListener('click', () => {
    currentIndex += 1;
    if (currentIndex >= questions.length) {
      showResult();
    } else {
      renderQuestion();
    }
  });
  const conceptCloseBtn = $('conceptCloseBtn');
  if (conceptCloseBtn) conceptCloseBtn.addEventListener('click', closeConceptModal);

  window.addEventListener('online', () => {
    flushSyncQueue();
  });

  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && navigator.onLine) {
      flushSyncQueue();
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
  tryShowLandingBanner();
  initSurvey();

  if (navigator.onLine) {
    flushSyncQueue();
  }

  if (!getConsent()) {
    showConsentBanner();
  }
})();
