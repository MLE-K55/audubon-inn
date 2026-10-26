'use strict';
const menu = document.querySelector('.menu-toggle');
const nav = document.getElementById('main-nav');
function closeMenu(returnFocus = false) {
  if (!menu || !nav) return;
  nav.classList.remove('open');
  menu.setAttribute('aria-expanded', 'false');
  menu.setAttribute('aria-label', 'Open navigation');
  if (returnFocus) menu.focus();
}
menu?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && nav?.classList.contains('open')) closeMenu(true);
});
document.addEventListener('click', e => {
  if (!e.target.closest('header') || e.target.closest('nav a')) closeMenu();
});
document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-filter]').forEach(peer => {
    peer.classList.toggle('active', peer === button);
    peer.setAttribute('aria-pressed', String(peer === button));
  });
  let visible = 0;
  document.querySelectorAll('[data-room]').forEach(card => {
    card.hidden = button.dataset.filter !== 'all' && card.dataset.room !== button.dataset.filter && !(button.dataset.filter === 'queen' && card.dataset.room === 'double');
    if (!card.hidden) visible++;
  });
  const status = document.getElementById('room-filter-status');
  if (status) status.textContent = `Showing ${visible} room style${visible === 1 ? '' : 's'}.`;
}));
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());

const settings = JSON.parse(document.getElementById('site-settings')?.textContent || '{}');
const measurementId = /^G-[A-Z0-9]+$/.test(settings.measurementId || '') ? settings.measurementId : '';
let consent = '';
let analyticsLoaded = false;
const choiceKey = 'audubon-analytics-choice';
try { consent = localStorage.getItem(choiceKey) || ''; } catch {}
const banner = document.querySelector('.privacy-banner');
const privacyButton = document.querySelector('[data-privacy-settings]');
const cleanLocation = location.origin + location.pathname;
function cleanReferrer() {
  try { const ref = new URL(document.referrer); return ref.origin + ref.pathname; } catch { return ''; }
}
function enableAnalytics() {
  if (!measurementId || consent !== 'accepted') return;
  window[`ga-disable-${measurementId}`] = false;
  if (analyticsLoaded) return;
  analyticsLoaded = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function() { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId, {send_page_view: false, allow_google_signals: false, allow_ad_personalization_signals: false, page_location: cleanLocation, page_referrer: cleanReferrer()});
  window.gtag('event', 'page_view', {page_location: cleanLocation, page_referrer: cleanReferrer(), page_title: document.title});
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  document.head.append(script);
}
function setConsent(value) {
  consent = value;
  try { localStorage.setItem(choiceKey, value); } catch {}
  banner.hidden = true;
  if (value === 'accepted') enableAnalytics();
  else if (measurementId) window[`ga-disable-${measurementId}`] = true;
}
if (measurementId) {
  privacyButton.hidden = false;
  banner.hidden = Boolean(consent);
  enableAnalytics();
  privacyButton.addEventListener('click', () => { banner.hidden = false; banner.querySelector('button').focus(); });
  document.querySelectorAll('[data-consent]').forEach(button => button.addEventListener('click', () => setConsent(button.dataset.consent)));
}
const allowedEvents = new Set(['availability_click','event_inquiry_start','tour_request','directions_click','phone_click','menu_view','brochure_download']);
document.addEventListener('click', e => {
  const link = e.target.closest('a,button');
  if (!link) return;
  const name = link.dataset.track || (link.getAttribute('href')?.startsWith('tel:') ? 'phone_click' : '');
  if (!allowedEvents.has(name) || !measurementId || consent !== 'accepted' || !window.gtag) return;
  window.gtag('event', name, {page_location: cleanLocation, service_category: name === 'event_inquiry_start' || name === 'tour_request' ? 'events' : name === 'availability_click' ? 'rooms' : 'visit', cta_location: link.closest('header') ? 'header' : link.closest('footer') ? 'footer' : link.closest('.mobile-actions') ? 'mobile_bar' : 'content'});
});

const eventsData = document.getElementById('local-events-data');
if (eventsData) {
  const data = JSON.parse(eventsData.textContent);
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeUrl = value => {
    try { const u = new URL(value); return u.protocol === 'https:' ? esc(u.href) : '#'; } catch { return '#'; }
  };
  const now = new Date();
  const parts = new Intl.DateTimeFormat('en-US', {timeZone:'America/Chicago',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
  const part = type => parts.find(p => p.type === type).value;
  const today = `${part('year')}-${part('month')}-${part('day')}`;
  let year = Number(part('year')), month = Number(part('month')) - 1;
  const weekdayNames = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const monthName = (y,m) => new Date(Date.UTC(y,m,1)).toLocaleDateString('en-US',{month:'long',year:'numeric',timeZone:'UTC'});
  const dateKey = (y,m,d) => `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
  const events = data.events.filter(e => e.status === 'scheduled').sort((a,b) => a.start.localeCompare(b.start));
  function renderCalendar() {
    const first = new Date(Date.UTC(year,month,1)).getUTCDay();
    const count = new Date(Date.UTC(year,month+1,0)).getUTCDate();
    let cells = '';
    for (let index = 0; index < Math.ceil((first+count)/7)*7; index++) {
      if (index % 7 === 0) cells += '<tr>';
      const day = index-first+1;
      if (day < 1 || day > count) cells += '<td class="outside-month"></td>';
      else {
        const key = dateKey(year,month,day);
        const listed = events.filter(e => e.start.slice(0,10) === key);
        cells += `<td class="${key < today ? 'past-day' : 'quiet-day'}"><span class="calendar-date"${key === today ? ' aria-current="date"' : ''}>${day}</span>`;
        for (const event of listed) cells += `<a class="calendar-event" href="${safeUrl(event.url)}" target="_blank" rel="noopener"><span class="event-dot" aria-hidden="true">●</span><span class="event-name">${esc(event.title)}</span></a>`;
        cells += '</td>';
      }
      if (index % 7 === 6) cells += '</tr>';
    }
    document.getElementById('local-calendar-view').innerHTML = `<div class="calendar-paper"><table class="local-calendar"><caption>${monthName(year,month)}</caption><thead><tr>${weekdayNames.map(d=>`<th scope="col"><abbr title="${d}">${d.slice(0,3)}</abbr></th>`).join('')}</tr></thead><tbody>${cells}</tbody></table></div>`;
    document.getElementById('calendar-status').textContent = `Showing ${monthName(year,month)}. All event times are America/Chicago. Blank dates have no featured listing.`;
  }
  function eventCard(e) {
    const date = new Date(e.start);
    const mon = date.toLocaleDateString('en-US',{month:'short',timeZone:'America/Chicago'}).toUpperCase();
    const day = date.toLocaleDateString('en-US',{day:'2-digit',timeZone:'America/Chicago'});
    return `<article><div class="event-date-badge"><span>${mon}</span><strong>${day}</strong></div><div><span class="tiny">COMMUNITY EVENT · ${esc(e.organizer)}</span><h4>${esc(e.title)}</h4><p><time datetime="${esc(e.start)}">${esc(e.time)}</time> · ${esc(e.location)}</p><p class="small">${esc(e.registration)}</p><a href="${safeUrl(e.url)}" target="_blank" rel="noopener">Organizer details ↗</a><p class="small">Last checked ${esc(e.checked)} · America/Chicago</p></div></article>`;
  }
  const future = events.filter(e => new Date(e.end).getTime() > now.getTime());
  const past = events.filter(e => new Date(e.end).getTime() <= now.getTime());
  document.getElementById('local-agenda').innerHTML = `<div class="event-agenda"><h3>Upcoming community events</h3>${future.length ? future.map(eventCard).join('') : '<p>No upcoming listings are featured here. Find the latest programs on the official community calendars below.</p>'}${past.length ? `<details class="past-events"><summary>Past featured events</summary>${past.map(eventCard).join('')}</details>` : ''}</div>`;
  document.querySelectorAll('[data-calendar-step]').forEach(button => button.addEventListener('click', () => {
    month += Number(button.dataset.calendarStep);
    if (month < 0) { month = 11; year--; }
    if (month > 11) { month = 0; year++; }
    renderCalendar();
  }));
  document.querySelector('[data-calendar-today]').addEventListener('click', () => {year=Number(part('year'));month=Number(part('month'))-1;renderCalendar();});
  renderCalendar();
}

const inquiryForm = document.getElementById('event-inquiry-form');
if (inquiryForm) {
  inquiryForm.addEventListener('submit', e => {
    e.preventDefault();
    const nameInput = inquiryForm.elements.namedItem('name');
    nameInput.setCustomValidity(nameInput.value.trim() ? '' : 'Please enter your name.');
    if (!inquiryForm.reportValidity()) return;
    const values = new FormData(inquiryForm);
    const draft = `Hello Audubon Inn team,\n\nI would like to discuss ${values.get('occasion').toLowerCase()}.\n\nPreferred date: ${values.get('date') || 'Flexible / to discuss'}\nEstimated guests: ${values.get('guests') || 'To discuss'}\nGuest rooms: ${values.get('rooms')}\n\n${String(values.get('message')).trim()}\n\nThank you,\n${String(values.get('name')).trim()}\n${String(values.get('email')).trim()}`;
    document.getElementById('inquiry-draft').value = draft;
    document.getElementById('inquiry-mailto').href = `mailto:hotelonthemarsh@gmail.com?subject=${encodeURIComponent('Event inquiry — '+values.get('occasion'))}&body=${encodeURIComponent(draft)}`;
    document.getElementById('inquiry-result').hidden = false;
    document.getElementById('inquiry-mailto').focus();
  });
  inquiryForm.elements.namedItem('name').addEventListener('input', e => e.target.setCustomValidity(''));
  document.getElementById('copy-inquiry').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(document.getElementById('inquiry-draft').value);
      document.getElementById('inquiry-status').textContent = 'Message copied. Paste it into your email app and send it to the inn.';
    } catch {
      document.getElementById('inquiry-draft').focus();
      document.getElementById('inquiry-draft').select();
      document.getElementById('inquiry-status').textContent = 'Select and copy the message, then send it through your email app.';
    }
  });
}
