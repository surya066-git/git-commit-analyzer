// UI Elements
const form = document.querySelector("#analyze-form");
const submitBtn = document.querySelector("#analyze-btn");
const errorCard = document.getElementById("error-card");
const errorMessage = document.getElementById("error-message");
const viewResultsBtn = document.getElementById("view-results-btn");

// Navigation
const navDashboard = document.getElementById('nav-dashboard');
const navHistory = document.getElementById('nav-history');
const navProfile = document.getElementById('nav-profile');
const viewDashboard = document.getElementById('view-dashboard');
const viewHistory = document.getElementById('view-history');
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mainNav = document.getElementById('main-nav');

// Containers
const sectionHero = document.getElementById('section-hero');
const sectionScore = document.getElementById('section-score');

// Modals
const commitModal = document.getElementById('commit-modal');
const modalCloseBtn = document.getElementById('modal-close');
const aiFixModal = document.getElementById('ai-fix-modal');
const aiModalCloseBtn = document.getElementById('ai-modal-close');
const profileModal = document.getElementById('profile-modal');
const profileCloseBtn = document.getElementById('profile-close');

// Storage Key
const HISTORY_KEY = 'git_analyzer_history';

// State
let currentAnalysisData = null;
let currentFixingCommitIndex = -1;
let currentAiResult = null;

// Table Controls State
let currentSearchText = '';
let currentFilterQuality = 'all';
let currentSortKey = null; // 'score', 'files', 'quality'
let currentSortDesc = true;

// AI Stats State
let aiStats = { improved: 0, scoreDelta: 0, upgrades: 0 };

// Quality Rankings for comparisons
const qualityRank = { 'poor': 1, 'average': 2, 'good': 3 };

// --- Utilities ---
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showError(message) {
  errorCard.hidden = false;
  errorMessage.textContent = message;
}

function clearError() {
  errorCard.hidden = true;
  errorMessage.textContent = '';
}

function getQualityColor(quality) {
  quality = (quality || "").toLowerCase();
  if (quality === 'good') return 'var(--good-color)';
  if (quality === 'average') return 'var(--avg-color)';
  return 'var(--poor-color)';
}

function listItems(items) {
  return (items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

// --- Intersection Observer for Scroll Animations ---
const observerOptions = { root: null, rootMargin: '0px', threshold: 0.15 };
const scrollObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, observerOptions);

function reobserveAnimations() {
  document.querySelectorAll('.reveal').forEach(el => {
    scrollObserver.observe(el);
  });
}

// --- 3D Pointer Parallax (Desktop Only) ---
document.addEventListener('mousemove', (e) => {
  if (window.innerWidth <= 1024 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const wrapper = document.querySelector('.hero-3d-wrapper');
  if (!wrapper) return;
  
  const x = e.clientX / window.innerWidth - 0.5;
  const y = e.clientY / window.innerHeight - 0.5;
  
  // Moderate tilting
  const rotateX = -y * 20 + 5; // Base 5deg
  const rotateY = x * 20 - 15; // Base -15deg
  
  wrapper.style.transform = `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;
});

// --- Navigation ---
function switchView(view) {
  if (view === 'history') {
    viewDashboard.classList.remove('active');
    viewHistory.classList.add('active');
    viewHistory.hidden = false;
    viewDashboard.hidden = true;
    navDashboard.classList.remove('active');
    navHistory.classList.add('active');
    renderHistory();
  } else {
    viewDashboard.classList.add('active');
    viewHistory.classList.remove('active');
    viewHistory.hidden = true;
    viewDashboard.hidden = false;
    navDashboard.classList.add('active');
    navHistory.classList.remove('active');
    reobserveAnimations();
  }
  mainNav.classList.remove('show');
}

navDashboard.addEventListener('click', () => switchView('dashboard'));
navHistory.addEventListener('click', () => switchView('history'));
navProfile.addEventListener('click', openProfileModal);
mobileMenuBtn.addEventListener('click', () => { mainNav.classList.toggle('show'); });

// View Results Button Scroll
viewResultsBtn.addEventListener('click', () => {
  sectionScore.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// --- Results Rendering (Dashboard) ---
function renderDashboard(isInitialRender = false) {
  const data = currentAnalysisData;
  if (!data) return;

  // Cleanup examples
  document.querySelectorAll('.example, .example-label, .example-item, .example-msg').forEach(el => {
    el.classList.remove('example', 'example-label', 'example-item', 'example-msg');
  });

  document.getElementById('repo-name').textContent = data.repository || "Repository";
  document.getElementById('repo-meta').innerHTML = `<span>Analyzed ${data.commit_count} commits</span> • <span>Model: ${escapeHtml(data.model_name || 'Default')}</span>`;

  const results = data.results || [];
  let totalScore = 0;
  let countGood = 0, countAverage = 0, countPoor = 0;
  let validScores = 0;
  let totalWords = 0;

  // Determine an example to put in the Before/After pane if possible
  let firstPoorCommit = null;

  results.forEach((commit, idx) => {
    const q = (commit.quality_category || '').toLowerCase();
    if (q === 'good') countGood++;
    else if (q === 'average') countAverage++;
    else if (q === 'poor') {
      countPoor++;
      if (!firstPoorCommit) {
        firstPoorCommit = commit;
        firstPoorCommit._originalIndex = idx;
      }
    }

    if (typeof commit.review_score === 'number') {
      totalScore += commit.review_score;
      validScores++;
    }
    const words = (commit.commit_message || '').split(/\s+/).length;
    totalWords += words;
  });

  const total = results.length || 1;
  const avgScore = validScores > 0 ? (totalScore / validScores).toFixed(1) : 0;
  
  let overallQuality = 'Good';
  if (countPoor >= countGood && countPoor >= countAverage) overallQuality = 'Poor';
  else if (countAverage >= countGood && countAverage > countPoor) overallQuality = 'Average';

  // Overall Score
  const scoreEl = document.getElementById('overall-score-value');
  animateNumber(scoreEl, parseFloat(scoreEl.textContent) || 0, parseFloat(avgScore), 1000, 1);
  
  const qLabel = document.getElementById('overall-quality-label');
  qLabel.textContent = overallQuality.toUpperCase();
  qLabel.className = `quality-label ${overallQuality.toLowerCase()}`;
  
  const circle = document.getElementById('score-circle-path');
  const percentage = (avgScore / 10) * 100;
  circle.setAttribute('stroke-dasharray', `${percentage}, 100`);
  circle.style.stroke = getQualityColor(overallQuality);

  // Bars
  document.getElementById('count-good').textContent = countGood;
  document.getElementById('count-average').textContent = countAverage;
  document.getElementById('count-poor').textContent = countPoor;
  
  setTimeout(() => {
    document.getElementById('bar-good').style.width = `${(countGood / total) * 100}%`;
    document.getElementById('bar-average').style.width = `${(countAverage / total) * 100}%`;
    document.getElementById('bar-poor').style.width = `${(countPoor / total) * 100}%`;
  }, 100);

  // Insights
  const insightsList = document.getElementById('insights-list');
  insightsList.innerHTML = '';
  const avgWords = Math.round(totalWords / total);
  insightsList.innerHTML += `<li>Average commit message length: <strong>${avgWords} words</strong>.</li>`;
  if (countGood > countPoor && countGood > countAverage) {
    insightsList.innerHTML += `<li>Most commits are rated <strong>Good</strong>. Great job!</li>`;
  } else if (countPoor > countGood) {
    insightsList.innerHTML += `<li>Many commits are rated <strong>Poor</strong>. Consider more descriptive messages.</li>`;
  } else {
    insightsList.innerHTML += `<li>Commit quality is mixed. Check the suggestions to improve.</li>`;
  }

  // Populate decorative Before/After pane if there's a poor commit available to showcase
  if (firstPoorCommit) {
    const bPane = document.querySelector('.ba-visual .before-pane');
    bPane.querySelector('.ba-msg').textContent = firstPoorCommit.commit_message;
    const qb = bPane.querySelector('.badge');
    qb.textContent = firstPoorCommit.quality_category;
    qb.className = `badge badge-${(firstPoorCommit.quality_category || '').toLowerCase()}`;
    bPane.querySelector('strong').textContent = firstPoorCommit.review_score;
    
    const aPane = document.querySelector('.ba-visual .after-pane');
    aPane.querySelector('.ba-msg').textContent = "Click 'Fix with AI' in the Complete Report table below to improve this message.";
    aPane.querySelector('strong').textContent = "-";
  }

  // AI Stats Update
  document.getElementById('ai-stat-count').textContent = aiStats.improved;
  const avgIncrease = aiStats.improved > 0 ? (aiStats.scoreDelta / aiStats.improved).toFixed(1) : "0.0";
  document.getElementById('ai-stat-score').textContent = `+${avgIncrease}`;
  document.getElementById('ai-stat-upgrades').textContent = aiStats.upgrades;

  // Render Table
  renderTable();

  // Show the "View Results ↓" button
  viewResultsBtn.hidden = false;

  // Save to history on initial render or major update
  if (isInitialRender) {
    saveToHistory({
      repository: data.repository,
      date: new Date().toISOString(),
      commit_count: data.commit_count,
      overall_quality: overallQuality,
      avg_score: avgScore
    });
  }
}

function renderTable() {
  if (!currentAnalysisData || !currentAnalysisData.results) return;
  const tbody = document.getElementById('commit-tbody');
  tbody.innerHTML = '';
  
  // 1. Filter
  let filtered = currentAnalysisData.results.map((c, i) => ({...c, _originalIndex: i}));
  
  if (currentFilterQuality !== 'all') {
    filtered = filtered.filter(c => (c.quality_category || '').toLowerCase() === currentFilterQuality);
  }
  
  if (currentSearchText) {
    const text = currentSearchText.toLowerCase();
    filtered = filtered.filter(c => 
      (c.commit_message || '').toLowerCase().includes(text) || 
      (c.author || '').toLowerCase().includes(text)
    );
  }
  
  // 2. Sort
  if (currentSortKey) {
    filtered.sort((a, b) => {
      let valA = a[currentSortKey === 'files' ? 'files_changed' : (currentSortKey === 'quality' ? 'quality_category' : 'review_score')];
      let valB = b[currentSortKey === 'files' ? 'files_changed' : (currentSortKey === 'quality' ? 'quality_category' : 'review_score')];
      
      if (currentSortKey === 'quality') {
        valA = qualityRank[(valA || '').toLowerCase()] || 0;
        valB = qualityRank[(valB || '').toLowerCase()] || 0;
      }
      
      if (valA < valB) return currentSortDesc ? 1 : -1;
      if (valA > valB) return currentSortDesc ? -1 : 1;
      return 0;
    });
  }
  
  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No commits match your filters.</td></tr>';
    return;
  }
  
  filtered.forEach((commit, index) => {
    const qClass = (commit.quality_category || '').toLowerCase();
    const tr = document.createElement('tr');
    tr.className = 'reveal fade-up visible'; // Make it visible instantly when rendering table
    
    let actionBtnHtml = `<button class="btn-secondary" onclick="openCommitModal(${commit._originalIndex}, event)">View</button>`;
    if (qClass === 'poor' || qClass === 'average') {
      actionBtnHtml = `<button class="btn-secondary" style="border-color: var(--secondary-color); color: var(--secondary-color);" onclick="openAiFixModal(${commit._originalIndex}, event)">Fix with AI</button>`;
    }

    tr.innerHTML = `
      <td data-label="Commit">
        <div class="td-truncate">${escapeHtml(commit.commit_message)}</div>
      </td>
      <td data-label="Author" class="hide-mobile">${escapeHtml(commit.author)}</td>
      <td data-label="Files" class="hide-mobile">${escapeHtml(commit.files_changed)}</td>
      <td data-label="Quality"><span class="badge badge-${qClass}">${escapeHtml(commit.quality_category)}</span></td>
      <td data-label="Score"><strong>${escapeHtml(commit.review_score)}</strong></td>
      <td data-label="Action">${actionBtnHtml}</td>
    `;
    tr.addEventListener('click', (e) => {
       if(e.target.tagName !== 'BUTTON') openCommitModal(commit._originalIndex, e);
    });
    tbody.appendChild(tr);
  });
}

// Table Control Event Listeners
document.getElementById('search-input').addEventListener('input', (e) => {
  currentSearchText = e.target.value;
  renderTable();
});
document.getElementById('filter-select').addEventListener('change', (e) => {
  currentFilterQuality = e.target.value;
  renderTable();
});
document.querySelectorAll('.commit-table th.sortable').forEach(th => {
  th.addEventListener('click', () => {
    const sortKey = th.getAttribute('data-sort');
    if (currentSortKey === sortKey) {
      currentSortDesc = !currentSortDesc; // Toggle direction
    } else {
      currentSortKey = sortKey;
      currentSortDesc = true;
    }
    // Update headers text to show direction indicator
    document.querySelectorAll('.commit-table th.sortable').forEach(h => {
      h.innerHTML = h.innerHTML.replace(' ↑', ' ↕').replace(' ↓', ' ↕');
    });
    th.innerHTML = th.innerHTML.replace(' ↕', currentSortDesc ? ' ↓' : ' ↑');
    renderTable();
  });
});

function animateNumber(element, start, end, duration, decimals = 0) {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const val = (progress * (end - start) + start).toFixed(decimals);
    element.textContent = val;
    if (progress < 1) window.requestAnimationFrame(step);
  };
  window.requestAnimationFrame(step);
}

// --- Modals ---
function openCommitModal(index, event) {
  if (event) event.stopPropagation();
  const commit = currentAnalysisData.results[index];
  const sha = String(commit.commit_sha || "").slice(0, 8) || "unknown";
  document.getElementById('modal-sha').textContent = `Commit: ${sha}`;
  document.getElementById('modal-message').textContent = commit.commit_message;
  
  document.getElementById('modal-meta').innerHTML = `
    <span><strong>Author:</strong> ${escapeHtml(commit.author)}</span>
    <span><strong>Date:</strong> ${escapeHtml(commit.date)}</span>
    <span><strong>Files:</strong> ${escapeHtml(commit.files_changed)}</span>
    <span style="color:var(--good-color)">+${escapeHtml(commit.lines_added)}</span>
    <span style="color:var(--poor-color)">-${escapeHtml(commit.lines_deleted)}</span>
  `;
  
  const qClass = (commit.quality_category || '').toLowerCase();
  const qBadge = document.getElementById('modal-quality');
  qBadge.textContent = commit.quality_category;
  qBadge.className = `badge badge-${qClass}`;
  document.getElementById('modal-score-val').textContent = commit.review_score;
  document.getElementById('modal-reasons').innerHTML = listItems(commit.reasons);
  document.getElementById('modal-suggestions').innerHTML = listItems(commit.suggestions);

  commitModal.showModal();
}

modalCloseBtn.addEventListener('click', () => commitModal.close());
commitModal.addEventListener('click', (e) => {
  const rect = commitModal.getBoundingClientRect();
  if (e.clientY < rect.top || e.clientY > rect.bottom || e.clientX < rect.left || e.clientX > rect.right) commitModal.close();
});

// --- Profile Modal ---
function openProfileModal() {
  const history = getHistory();
  let totalRepos = history.length;
  let totalCommits = 0;
  let scoreSum = 0;
  
  history.forEach(h => {
    totalCommits += (h.commit_count || 0);
    scoreSum += parseFloat(h.avg_score || 0);
  });
  
  document.getElementById('profile-repos').textContent = totalRepos;
  document.getElementById('profile-commits').textContent = totalCommits;
  document.getElementById('profile-score').textContent = totalRepos > 0 ? (scoreSum / totalRepos).toFixed(1) : "0.0";
  
  const recentList = document.getElementById('profile-recent-list');
  recentList.innerHTML = history.slice(0, 5).map(h => `
    <li>
      <strong>${escapeHtml(h.repository)}</strong>
      <span class="badge badge-${String(h.overall_quality).toLowerCase()}">${escapeHtml(h.overall_quality)}</span>
    </li>
  `).join('');
  
  if (history.length === 0) {
    recentList.innerHTML = '<li class="empty-state">No recent activity.</li>';
  }
  
  profileModal.showModal();
}

profileCloseBtn.addEventListener('click', () => profileModal.close());
profileModal.addEventListener('click', (e) => {
  const rect = profileModal.getBoundingClientRect();
  if (e.clientY < rect.top || e.clientY > rect.bottom || e.clientX < rect.left || e.clientX > rect.right) profileModal.close();
});

// --- AI Fix Logic ---
async function openAiFixModal(index, event) {
  if (event) event.stopPropagation();
  currentFixingCommitIndex = index;
  currentAiResult = null;
  
  const commit = currentAnalysisData.results[index];
  
  // Setup Before
  document.getElementById('ba-before-msg').textContent = commit.commit_message;
  const qClass = (commit.quality_category || '').toLowerCase();
  const qBadge = document.getElementById('ba-before-badge');
  qBadge.textContent = commit.quality_category;
  qBadge.className = `badge badge-${qClass}`;
  document.getElementById('ba-before-score').textContent = commit.review_score;
  
  // Setup After (Loading state)
  document.getElementById('ai-loading').hidden = false;
  document.getElementById('ai-result').hidden = true;
  document.getElementById('ai-action-footer').hidden = true;
  
  aiFixModal.showModal();
  
  try {
    const genRes = await fetch("/generate-fix", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        commit_message: commit.commit_message,
        reasons: commit.reasons || [],
        suggestions: commit.suggestions || []
      }),
    });
    const genData = await genRes.json();
    if (!genRes.ok) throw new Error(genData.detail || "AI Fix generation failed.");
    
    const scoreRes = await fetch("/score-text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        commit_message: genData.improved_message,
        files_changed: commit.files_changed || 1,
        lines_added: commit.lines_added || 1,
        lines_deleted: commit.lines_deleted || 1,
        has_issue: commit.has_issue || false,
        has_pr: commit.has_pr || false
      }),
    });
    const newCommit = await scoreRes.json();
    if (!scoreRes.ok) throw new Error("Failed to score improved text.");
    
    setTimeout(() => showAiResult(newCommit), 800);
  } catch (error) {
    document.getElementById('ai-loading').innerHTML = `<span style="color:var(--poor-color)">Error: ${escapeHtml(error.message)}</span>`;
  }
}

function showAiResult(newCommit) {
  currentAiResult = newCommit;
  
  document.getElementById('ai-loading').hidden = true;
  document.getElementById('ai-result').hidden = false;
  document.getElementById('ai-action-footer').hidden = false;
  
  document.getElementById('ba-after-msg').textContent = newCommit.commit_message;
  
  const qClass = (newCommit.quality_category || '').toLowerCase();
  const qBadge = document.getElementById('ba-after-badge');
  qBadge.textContent = newCommit.quality_category;
  qBadge.className = `badge badge-${qClass}`;
  
  const afterScoreEl = document.getElementById('ba-after-score');
  const oldScore = parseFloat(document.getElementById('ba-before-score').textContent);
  animateNumber(afterScoreEl, oldScore, newCommit.review_score, 1000, 1);
}

document.getElementById('ai-apply-btn').addEventListener('click', () => {
  if (currentFixingCommitIndex > -1 && currentAiResult) {
    const original = currentAnalysisData.results[currentFixingCommitIndex];
    
    // AI Stats Math
    const oldScore = original.review_score || 0;
    const newScore = currentAiResult.review_score || 0;
    const oldRank = qualityRank[(original.quality_category || '').toLowerCase()] || 0;
    const newRank = qualityRank[(currentAiResult.quality_category || '').toLowerCase()] || 0;
    
    if (newScore > oldScore) {
      aiStats.improved++;
      aiStats.scoreDelta += (newScore - oldScore);
    }
    if (newRank > oldRank) {
      aiStats.upgrades++;
    }

    currentAnalysisData.results[currentFixingCommitIndex] = {
      ...original,
      ...currentAiResult,
      author: original.author,
      date: original.date,
      commit_sha: original.commit_sha
    };
    
    aiFixModal.close();
    
    // Update decorative pane with the new fix
    const aPane = document.querySelector('.ba-visual .after-pane');
    aPane.querySelector('.ba-msg').textContent = currentAiResult.commit_message;
    const aqb = aPane.querySelector('.badge');
    aqb.textContent = currentAiResult.quality_category;
    aqb.className = `badge badge-${(currentAiResult.quality_category || '').toLowerCase()}`;
    aPane.querySelector('strong').textContent = currentAiResult.review_score;

    renderDashboard(false); // Update without overwriting initial history stats purely from this
    sectionScore.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});

aiModalCloseBtn.addEventListener('click', () => aiFixModal.close());
aiFixModal.addEventListener('click', (e) => {
  const rect = aiFixModal.getBoundingClientRect();
  if (e.clientY < rect.top || e.clientY > rect.bottom || e.clientX < rect.left || e.clientX > rect.right) aiFixModal.close();
});

// --- Form Submission ---
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  
  const payload = {
    repository_url: form.repository_url.value,
    max_commits: 15,
  };

  submitBtn.disabled = true;
  submitBtn.textContent = "Analyzing...";
  clearError();
  viewResultsBtn.hidden = true;
  
  // Reset session stats on new run
  aiStats = { improved: 0, scoreDelta: 0, upgrades: 0 };
  currentSearchText = '';
  currentFilterQuality = 'all';
  currentSortKey = null;
  document.getElementById('search-input').value = '';
  document.getElementById('filter-select').value = 'all';

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    
    let data;
    try {
      data = await response.json();
    } catch (e) {
      throw new Error("Received an invalid response from the server.");
    }
    
    if (!response.ok) {
      let detail = "Unable to analyze repository.";
      if (data && data.detail) {
        if (typeof data.detail === "string") {
          detail = data.detail;
        } else if (Array.isArray(data.detail) && data.detail.length > 0 && data.detail[0].msg) {
          detail = data.detail[0].msg;
        } else {
          detail = JSON.stringify(data.detail);
        }
      }
      throw new Error(detail);
    }
    
    currentAnalysisData = data;
    renderDashboard(true);
    
  } catch (error) {
    console.error("Analysis error:", error);
    showError(error.message ? String(error.message) : "A network or server error occurred.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Analyze All Commits";
  }
});

// --- History Storage ---
function getHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveToHistory(entry) {
  const history = getHistory();
  const filtered = history.filter(h => h.repository !== entry.repository);
  filtered.unshift(entry);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered.slice(0, 15)));
}

function renderHistory() {
  const history = getHistory();
  const tbody = document.getElementById('history-tbody');
  
  if (history.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No history found.</td></tr>';
    return;
  }
  
  tbody.innerHTML = history.map(item => {
    const d = new Date(item.date).toLocaleDateString();
    const qClass = (item.overall_quality || '').toLowerCase();
    
    return `
      <tr class="reveal fade-up visible">
        <td data-label="Repository"><strong>${escapeHtml(item.repository)}</strong></td>
        <td data-label="Date">${d}</td>
        <td data-label="Commits">${escapeHtml(item.commit_count)}</td>
        <td data-label="Quality"><span class="badge badge-${qClass}">${escapeHtml(item.overall_quality)}</span></td>
        <td data-label="Score"><strong>${escapeHtml(item.avg_score)}</strong></td>
        <td data-label="Action">
          <button class="btn-secondary" onclick="analyzeRepo('${escapeHtml(item.repository)}')">Analyze Again</button>
        </td>
      </tr>
    `;
  }).join('');
}

window.analyzeRepo = function(repoUrl) {
  document.getElementById('repository-url').value = "https://github.com/" + repoUrl;
  switchView('dashboard');
  form.dispatchEvent(new Event('submit'));
};

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  reobserveAnimations();
});
