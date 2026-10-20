const toggle = document.querySelector('.nav-toggle');
const links = document.querySelector('.nav-links');

toggle.addEventListener('click', () => {
  const open = links.classList.toggle('open');
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});

links.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  links.classList.remove('open');
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', 'Open navigation');
}));

const themeButtons = document.querySelectorAll('[data-theme-toggle]');

function applyTheme(theme, persist = true) {
  document.documentElement.dataset.theme = theme;
  if (persist) {
    try { localStorage.setItem('quantease-theme', theme); } catch (_) { /* The current page still uses the selected theme. */ }
  }

  themeButtons.forEach((button) => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    const label = nextTheme === 'dark' ? 'Dark mode' : 'Light mode';
    button.setAttribute('aria-label', `Switch to ${label.toLowerCase()}`);
    button.title = `Switch to ${label.toLowerCase()}`;
    const icon = button.querySelector('.theme-icon');
    const text = button.querySelector('.theme-label');
    if (icon) icon.textContent = theme === 'dark' ? '☼' : '◐';
    if (text) text.textContent = label;
  });
}

applyTheme(document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light', false);
themeButtons.forEach((button) => button.addEventListener('click', () => {
  applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
}));
