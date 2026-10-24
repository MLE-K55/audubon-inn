"""Local events calendar."""
import calendar
import json
from datetime import date
from html import escape

def render_calendar(root):
    data = json.loads((root / 'local-events.json').read_text(encoding='utf-8'))
    year, month = data['year'], data['month']
    events = sorted(data['events'], key=lambda event: event['day'])
    name = f'{calendar.month_name[month]} {year}'
    by_day = {}
    for index, event in enumerate(events):
        date(year, month, event['day'])
        by_day.setdefault(event['day'], []).append((index, event))
    rows = []
    for week in calendar.Calendar(firstweekday=6).monthdayscalendar(year, month):
        cells = []
        for day in week:
            if not day:
                cells.append('<td class="outside-month"></td>')
                continue
            items = by_day.get(day, [])
            content = f'<span class="calendar-date">{day}</span>'
            for index, event in items:
                content += f'<a class="calendar-event" href="#local-event-{index}" aria-label="{escape(name)} {day}: {escape(event["title"])}"><span class="event-dot" aria-hidden="true">●</span><span class="event-name">{escape(event["title"])}</span></a>'
            cells.append(f'<td class="{"event-day" if items else "quiet-day"}">{content}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    headings = ''.join(f'<th scope="col"><abbr title="{d}">{d[:3]}</abbr></th>' for d in ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'])
    table = f'<div class="calendar-paper"><table class="local-calendar"><caption><span class="tiny">THE LOCAL CALENDAR</span>{name}</caption><thead><tr>{headings}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    agenda = '<div class="event-agenda"><h3>The month at a glance.</h3>'
    for index, event in enumerate(events):
        agenda += f'<article id="local-event-{index}" tabindex="-1"><div class="event-date-badge"><span>{calendar.month_abbr[month].upper()}</span><strong>{event["day"]:02d}</strong></div><div><h4>{escape(event["title"])}</h4><p>{escape(event["time"])} · {escape(event["location"])}</p><a href="{escape(event["url"], quote=True)}" target="_blank" rel="noopener">Organizer details ↗</a></div></article>'
    return table + agenda + '</div>'
