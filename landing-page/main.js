import { copy } from './copy.js';
import { icons } from './icons.js';
import { contact } from './config.js';

const langButtons = [...document.querySelectorAll('[data-language]')];
const menuButton = document.querySelector('#menu-button');
const mobileMenu = document.querySelector('#mobile-menu');
let language = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'es';

function setIcon(element, name) {
  element.innerHTML = icons[name] || '';
}
document.querySelectorAll('[data-icon]').forEach(element => setIcon(element, element.dataset.icon));
document.querySelector('#year').textContent = new Date().getFullYear();

function closeMenu(restoreFocus = false) {
  mobileMenu.hidden = true;
  menuButton.setAttribute('aria-expanded', 'false');
  setIcon(menuButton.querySelector('[data-icon]'), 'Menu');
  updateMenuLabel();
  if (restoreFocus) menuButton.focus();
}
function updateMenuLabel() {
  const open = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-label', language === 'en' ? (open ? 'Close menu' : 'Open menu') : (open ? 'Cerrar menú' : 'Abrir menú'));
}

function translate(nextLanguage, updateURL = true) {
  language = nextLanguage;
  const content = copy[language];
  document.documentElement.lang = language;
  document.querySelectorAll('[data-copy]').forEach(element => {
    const value = content[element.dataset.copy];
    if (value !== undefined) element.textContent = value;
  });
  document.querySelector('.skip-link').textContent = language === 'en' ? 'Skip to content' : 'Ir al contenido';
  document.querySelector('.desktop-nav').setAttribute('aria-label', language === 'en' ? 'Main navigation' : 'Navegación principal');
  mobileMenu.setAttribute('aria-label', language === 'en' ? 'Mobile navigation' : 'Navegación móvil');
  document.querySelector('.tools-strip').setAttribute('aria-label', language === 'en' ? 'Tools you already use' : 'Herramientas de tu operación');
  langButtons.forEach(button => {
    button.setAttribute('aria-pressed', String(button.dataset.language === language));
    button.setAttribute('aria-label', button.dataset.language === 'es' ? 'Español' : 'English');
  });
  document.title = language === 'en' ? 'Rumbo · Agents for logistics' : 'Rumbo · Agentes para la logística';
  document.querySelector('meta[name="description"]').content = language === 'en'
    ? 'Rumbo: agents for the logistics industry. Support your freight journeys, driver updates and proof of delivery, with your team in control.'
    : 'Rumbo: agentes para el mercado de la logística. Acompaña tus viajes, las novedades de tus conductores y los documentos de cada entrega.';
  const description = document.querySelector('meta[name="description"]').content;
  document.querySelector('meta[property="og:title"]').content = document.title;
  document.querySelector('meta[property="og:description"]').content = description;
  document.querySelector('meta[property="og:locale"]').content = language === 'en' ? 'en_US' : 'es_CO';
  document.querySelector('meta[property="og:locale:alternate"]').content = language === 'en' ? 'es_CO' : 'en_US';
  document.querySelector('meta[name="twitter:title"]').content = document.title;
  document.querySelector('meta[name="twitter:description"]').content = description;
  updateMenuLabel();
  if (updateURL) {
    const url = new URL(location.href);
    if (language === 'en') url.searchParams.set('lang', 'en');
    else url.searchParams.delete('lang');
    history.replaceState(null, '', url);
  }
}
langButtons.forEach(button => button.addEventListener('click', () => translate(button.dataset.language)));
menuButton.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  mobileMenu.hidden = !open;
  menuButton.setAttribute('aria-expanded', String(open));
  setIcon(menuButton.querySelector('[data-icon]'), open ? 'X' : 'Menu');
  updateMenuLabel();
});
mobileMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
document.querySelector('.site-header .brand').addEventListener('click', () => closeMenu());
document.addEventListener('pointerdown', event => {
  if (!mobileMenu.hidden && !document.querySelector('.site-header').contains(event.target)) closeMenu();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !mobileMenu.hidden) closeMenu(true);
});
window.matchMedia('(min-width:960px)').addEventListener('change', () => closeMenu());

if (contact.href && /^(https:|mailto:|tel:)/i.test(contact.href)) {
  const link = document.querySelector('#contact-link');
  link.href = contact.href;
  link.hidden = false;
  document.querySelector('#contact-pending').hidden = true;
  document.querySelector('#contact-label').textContent = contact.label || '';
  if (contact.href.startsWith('https:')) {
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
  }
}
translate(language, false);

