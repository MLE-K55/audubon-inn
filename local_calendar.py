"""Current-month calendar with independently sourced community listings."""
import calendar
import json
from datetime import date, datetime, timezone
from html import escape
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def render_calendar(root, today=None):
    if today is None:
        try:
            today = datetime.now(ZoneInfo('America/Chicago')).date()
        except ZoneInfoNotFoundError:
            today = datetime.now(timezone.utc).date()
    data = json.loads((root/'local-events.json').read_text(encoding='utf-8'))
    year, month = today.year, today.month
    events = sorted(data['events'],key=lambda e:e['start'])
    by_day = {}
    for e in events:
        start = datetime.fromisoformat(e['start'])
        if (start.year,start.month)==(year,month) and e.get('status','scheduled')=='scheduled':
            by_day.setdefault(start.day,[]).append(e)
    rows = []
    for week in calendar.Calendar(firstweekday=6).monthdayscalendar(year,month):
        cells = []
        for day in week:
            if not day:
                cells.append('<td class="outside-month"></td>')
                continue
            past = date(year,month,day)<today
            contents = f'<span class="calendar-date"'+(' aria-current="date"' if date(year,month,day)==today else '')+f'>{day}</span>'
            for e in by_day.get(day,[]):
                contents += f'<a class="calendar-event" href="{escape(e["url"],quote=True)}" target="_blank" rel="noopener"><span class="event-dot" aria-hidden="true">●</span><span class="event-name">{escape(e["title"])}</span></a>'
            cells.append(f'<td class="{"past-day" if past else "quiet-day"}">{contents}</td>')
        rows.append('<tr>'+''.join(cells)+'</tr>')
    name = f'{calendar.month_name[month]} {year}'
    headings = ''.join(f'<th scope="col"><abbr title="{d}">{d[:3]}</abbr></th>' for d in ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'])
    table = f'<div class="calendar-paper"><table class="local-calendar"><caption>{name}</caption><thead><tr>{headings}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    upcoming = [e for e in events if datetime.fromisoformat(e['start']).date()>=today and e.get('status','scheduled')=='scheduled']
    agenda = '<div class="event-agenda"><h3>Upcoming community events</h3>'
    for e in upcoming:
        start = datetime.fromisoformat(e['start'])
        agenda += f'<article><div class="event-date-badge"><span>{calendar.month_abbr[start.month].upper()}</span><strong>{start.day:02d}</strong></div><div><span class="tiny">COMMUNITY EVENT · {escape(e["organizer"])}</span><h4>{escape(e["title"])}</h4><p><time datetime="{e["start"]}">{escape(e["time"])}</time> · {escape(e["location"])}</p><p class="small">{escape(e["registration"])}</p><a href="{escape(e["url"],quote=True)}" target="_blank" rel="noopener">Organizer details ↗</a><p class="small">Last checked {escape(e["checked"])} · America/Chicago</p></div></article>'
    if not upcoming:
        agenda += '<p>No upcoming listings are featured here. Find the latest programs on the official community calendars below.</p>'
    agenda += '</div>'
    payload = json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    return f'<div class="calendar-controls"><button class="text-link" type="button" data-calendar-step="-1" aria-label="Previous calendar month">← Previous</button><button class="text-link" type="button" data-calendar-today>This month</button><button class="text-link" type="button" data-calendar-step="1" aria-label="Next calendar month">Next →</button></div><div id="local-calendar-view" data-month="{year}-{month:02d}">{table}</div><div id="local-agenda">{agenda}</div><p id="calendar-status" role="status" class="small">Showing {name}. Event times are local to Wisconsin.</p><script type="application/json" id="local-events-data">{payload}</script>'
