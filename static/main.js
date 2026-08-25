// ── Theme (dark / light) ──────────────────────────────────────────────────
const themeToggle = document.querySelector('#color_changer');

function getPreferredTheme() {
  try {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || savedTheme === 'light') {
      return savedTheme;
    }
  } catch (error) {
    console.warn('Theme preference could not be read from localStorage.', error);
  }
  // Fall back to OS/browser preference
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  const isDark = theme === 'dark';
  document.body.classList.toggle('dark', isDark);
  document.documentElement.classList.toggle('dark', isDark);

  if (themeToggle) {
    themeToggle.setAttribute('aria-pressed', String(isDark));
    themeToggle.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
  }
}

// Apply immediately on every page load (reads OS pref if no saved pref)
applyTheme(getPreferredTheme());

// Also react to OS-level theme changes in real time
if (window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    // Only follow OS if user hasn't saved an explicit preference
    try {
      if (!localStorage.getItem('theme')) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    } catch (_) { /* ignore */ }
  });
}

if (themeToggle) {
  themeToggle.addEventListener('click', function () {
    const nextTheme = document.body.classList.contains('dark') ? 'light' : 'dark';
    try {
      localStorage.setItem('theme', nextTheme);
    } catch (error) {
      console.warn('Theme preference could not be saved to localStorage.', error);
    }
    applyTheme(nextTheme);
  });
}
