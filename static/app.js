// ============================================================================
// DOM Elements
// ============================================================================

const form = document.getElementById('search-form');
const queryInput = document.getElementById('movie-query');
const titlesList = document.getElementById('movie-titles');
const quickPicks = document.getElementById('quick-picks');
const quickPicksContainer = document.getElementById('quick-picks-container');
const results = document.getElementById('results');
const status = document.getElementById('status');
const matchedTitle = document.getElementById('matched-title');
const submitBtn = form.querySelector('button[type="submit"]');
const featuredSection = document.getElementById('featured-section');
const featuredCard = document.getElementById('featured-card');

// ============================================================================
// SVG Icons
// ============================================================================

const ICONS = {
  star: `<svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
  </svg>`,
  play: `<svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
    <polygon points="5 3 19 12 5 21 5 3"/>
  </svg>`,
  search: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" style="display: inline-block; vertical-align: middle;">
    <circle cx="11" cy="11" r="8"></circle>
    <path d="m21 21-4.35-4.35"></path>
  </svg>`,
  target: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
    <circle cx="12" cy="12" r="1"></circle>
    <circle cx="12" cy="12" r="5"></circle>
    <circle cx="12" cy="12" r="9"></circle>
  </svg>`,
  spinner: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" style="display: inline-block; animation: spin 0.8s linear infinite;">
    <circle cx="12" cy="12" r="10"></circle>
    <path d="M12 2a10 10 0 0 1 10 10"></path>
  </svg>`,
  error: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
    <circle cx="12" cy="12" r="10"></circle>
    <path d="M12 8v4M12 16h.01"></path>
  </svg>`,
  alert: `<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
  </svg>`,
};

function getSvgIcon(name) {
  return ICONS[name] || '';
}

// ============================================================================
// Constants
// ============================================================================

const EMPTY_STATES = {
  initial: {
    icon: ICONS.target,
    title: 'Ready to discover?',
    description: 'Search for a movie you like and we\'ll find similar ones based on plot, genre, cast, and more.',
  },
  loading: {
    icon: ICONS.spinner,
    title: 'Finding recommendations...',
    description: 'Hold on while we analyze your selection.',
  },
  empty: {
    icon: ICONS.error,
    title: 'No recommendations found',
    description: 'Try searching for a different movie title.',
  },
  error: {
    icon: ICONS.alert,
    title: 'Something went wrong',
    description: 'We couldn\'t process your request. Please try again.',
  },
};

// ============================================================================
// Utility Functions
// ============================================================================

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function truncate(text, length = 160) {
  if (!text) return '';
  return text.length > length ? `${text.slice(0, length).trim()}...` : text;
}

function submitQuery(title) {
  queryInput.value = title;
  form.requestSubmit();
}

function setButtonLoading(isLoading) {
  submitBtn.disabled = isLoading;
  if (isLoading) {
    submitBtn.innerHTML = `${ICONS.spinner}<span>Searching...</span>`;
  } else {
    submitBtn.innerHTML = '<span>Find Similar</span>';
  }
}

function hideQuickPicks() {
  quickPicksContainer.classList.add('hidden');
}

function showQuickPicks() {
  quickPicksContainer.classList.remove('hidden');
}

// ============================================================================
// Featured Matched Movie Card
// ============================================================================

function renderFeaturedCard(movie) {
  if (!movie) {
    featuredSection.style.display = 'none';
    return;
  }

  const poster = movie.poster_url
    ? `<img src="${escapeHtml(movie.poster_url)}" alt="Poster for ${escapeHtml(movie.title)}" />`
    : `<div class="featured-poster-fallback">No poster available</div>`;

  const year = movie.release_date ? String(movie.release_date).slice(0, 4) : 'N/A';
  const rating = movie.vote_average ? Number(movie.vote_average).toFixed(1) : 'N/A';

  const genres = (movie.genres || [])
    .slice(0, 3)
    .map((genre) => `<span class="featured-badge">${escapeHtml(genre)}</span>`)
    .join('');

  const trailerButton = movie.trailer_url
    ? `<a class="card-action" href="${escapeHtml(movie.trailer_url)}" target="_blank" rel="noopener noreferrer">${ICONS.play} Watch Trailer</a>`
    : `<span class="card-action card-action-disabled">No trailer</span>`;

  featuredCard.innerHTML = `
    <div class="featured-poster">
      ${poster}
    </div>
    <div class="featured-content">
      <h3 class="featured-title">${escapeHtml(movie.title)}</h3>
      <div class="featured-meta">
        <span class="featured-rating">${ICONS.star} ${rating}</span>
        <span class="featured-badge">${year}</span>
        ${genres}
      </div>
      <p class="featured-description">${escapeHtml(truncate(movie.overview || '', 200))}</p>
      <div class="featured-actions">
        ${trailerButton}
      </div>
    </div>
  `;

  featuredSection.style.display = 'block';
}

// ============================================================================
// Rendering Functions
// ============================================================================

function renderEmptyState(state = 'initial') {
  const config = EMPTY_STATES[state] || EMPTY_STATES.initial;
  results.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">${config.icon}</div>
      <h3 class="empty-title">${config.title}</h3>
      <p class="empty-description">${config.description}</p>
    </div>
  `;
}

function renderLoadingSkeletons() {
  const skeletons = Array(5)
    .fill()
    .map(
      () => `
    <div class="skeleton-card">
      <div class="skeleton-poster"></div>
      <div class="skeleton-content">
        <div class="skeleton-text large"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text" style="width: 60%;"></div>
      </div>
    </div>
  `,
    )
    .join('');

  results.innerHTML = skeletons;
}

function renderResults(payload) {
  // Hide quick picks when results are displayed
  hideQuickPicks();

  if (!payload.results || payload.results.length === 0) {
    renderEmptyState('empty');
    status.textContent = 'No similar movies found. Try another title!';
    featuredSection.style.display = 'none';
    matchedTitle.textContent = '';
    showQuickPicks(); // Show quick picks if no results
    return;
  }

  // Find matched movie (first result or highest similarity)
  const matchedMovie = payload.results[0];
  renderFeaturedCard(matchedMovie);

  // Hide the matched title in header since it's displayed prominently
  matchedTitle.textContent = '';

  // Build recommendation cards (excluding the featured one)
  const otherResults = payload.results.slice(1);
  const resultsHtml = otherResults
    .map((movie) => {
      const poster = movie.poster_url
        ? `<img src="${escapeHtml(movie.poster_url)}" alt="Poster for ${escapeHtml(movie.title)}" loading="lazy" />`
        : `<div class="card-poster-fallback">No poster available</div>`;

      const year = movie.release_date ? String(movie.release_date).slice(0, 4) : 'N/A';
      const rating = movie.vote_average ? Number(movie.vote_average).toFixed(1) : 'N/A';

      const trailerButton = movie.trailer_url
        ? `<a class="card-action" href="${escapeHtml(movie.trailer_url)}" target="_blank" rel="noopener noreferrer">${ICONS.play} Trailer</a>`
        : `<span class="card-action card-action-disabled">No trailer</span>`;

      const genres = (movie.genres || [])
        .slice(0, 2)
        .map((genre) => `<span class="card-badge">${escapeHtml(genre)}</span>`)
        .join('');

      return `
        <article class="card" data-title="${escapeHtml(movie.title)}">
          <div class="card-poster">
            ${poster}
          </div>
          <div class="card-content">
            <div class="card-header">
              <h3 class="card-title">${escapeHtml(movie.title)}</h3>
              <div class="card-rating">${ICONS.star} ${rating}</div>
            </div>
            <div class="card-meta">
              <span class="card-badge">${year}</span>
              ${genres}
            </div>
            <p class="card-description">${escapeHtml(truncate(movie.overview || ''))}</p>
            <div class="card-actions">
              ${trailerButton}
              <button class="card-action card-action-secondary" type="button" title="Search for this movie">${ICONS.search}</button>
            </div>
          </div>
        </article>
      `;
    })
    .join('');

  results.innerHTML = resultsHtml;

  // Update status
  const totalCount = payload.results.length;
  const otherCount = otherResults.length;
  status.textContent = `Found ${totalCount} similar movie${totalCount !== 1 ? 's' : ''}`;
}

// ============================================================================
// Event Listeners
// ============================================================================

// Load quick picks on page load
async function loadQuickPicks() {
  try {
    const response = await fetch('/api/titles');
    if (!response.ok) throw new Error('Failed to load titles');

    const payload = await response.json();
    const titles = (payload.titles || []).slice(0, 8);

    // Update datalist
    titlesList.innerHTML = titles.map((title) => `<option value="${escapeHtml(title)}"></option>`).join('');

    // Update quick picks
    quickPicks.innerHTML = titles
      .map((title) => `<button class="chip" type="button" data-title="${escapeHtml(title)}">${escapeHtml(title)}</button>`)
      .join('');
  } catch (error) {
    console.error('Error loading quick picks:', error);
    quickPicks.innerHTML = '';
  }
}

// Quick pick button clicks
quickPicks.addEventListener('click', (event) => {
  const button = event.target.closest('button[data-title]');
  if (!button) return;
  submitQuery(button.dataset.title);
});

// Search result card secondary buttons
results.addEventListener('click', (event) => {
  const button = event.target.closest('button.card-action-secondary');
  if (!button) return;
  const card = button.closest('article[data-title]');
  if (!card) return;
  submitQuery(card.dataset.title);
});

// Featured card secondary button
featuredCard.addEventListener('click', (event) => {
  const button = event.target.closest('button.card-action-secondary');
  if (!button) return;
  const card = button.closest('.featured-card');
  if (!card) return;
  // Get title from featured title text
  const titleEl = card.querySelector('.featured-title');
  if (titleEl) {
    submitQuery(titleEl.textContent);
  }
});

// Form submission
form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();

  // Validation
  if (!query) {
    status.textContent = 'Please enter a movie title';
    renderEmptyState('empty');
    featuredSection.style.display = 'none';
    showQuickPicks();
    return;
  }

  // Loading state
  setButtonLoading(true);
  status.textContent = 'Searching...';
  renderLoadingSkeletons();
  matchedTitle.textContent = '';
  featuredSection.style.display = 'none';

  try {
    const response = await fetch('/api/recommendations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, limit: 5 }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const payload = await response.json();
    renderResults(payload);
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    status.textContent = 'Unable to fetch recommendations. Please try again.';
    renderEmptyState('error');
    featuredSection.style.display = 'none';
    showQuickPicks();
  } finally {
    setButtonLoading(false);
  }
});

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  renderEmptyState('initial');
  loadQuickPicks();
});
