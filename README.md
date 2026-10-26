# Audubon Inn website

Public website: https://mle-k55.github.io/audubon-inn/

## Build and check

Python 3.12 or newer is recommended.

```sh
python -m pip install -r requirements.txt
python -X utf8 build.py
python -X utf8 check_site.py
python -m http.server 8877 --directory dist
```

The public build allows search indexing and writes the canonical sitemap. For a private preview, run `python build.py --preview --output preview-dist`. Do not deploy a preview build to GitHub Pages.

## Edit the website

- `site_content.py`: home, rooms, events, weddings, bar, contact, FAQs, and history.
- `site-config.json`: public canonical URL, booking URL, inquiry route, optional managed form, optional Analytics ID and Search Console verification, and approved property facts used in structured data. If property facts change, update the visible wording in `site_content.py` and the guides too.
- `brand.html`: shared official Audubon Inn logo.
- `wedding-content.html`: comments explaining where to add wedding photos. Empty photo sections are not shown to guests.
- `area-content.html`: local attractions and the calendar section; comments reserve three future attraction entries.
- `dining-content.html`: The Meating Place and four commented future restaurant positions.
- `wedding-guide-content.html` and `marsh-weekend-content.html`: practical trip-planning guides.
- `inquiry-content.html`: event email composer. The visitor must open their own email app and send the message; nothing is submitted in the background.
- `privacy-content.html` and `sources-content.html`: provider, privacy, and credit information.
- `dist/style.css` and `dist/app.js`: shared styling and interactions.
- `dist/assets/`: photographs, responsive WebP sizes, and favicon. Keep dimensions and source credits accurate when adding photos. The original 177-by-181 ceremony photo is deliberately displayed small.

## Calendar upkeep

Edit `local-events.json` with ISO start/end times including offsets, title, organizer, venue, official link, registration instructions, last-checked date, and status. America/Chicago is used for visitor dates. Use `scheduled` for confirmed listings, or remove/change status when cancelled. The calendar opens on the current month and supports month navigation. Expired events move out of the upcoming agenda. An empty month links visitors to official community calendars; it does not invent listings. Review weekly and when dates change.

## Publishing

The GitHub Actions workflow checks and publishes `dist/` on pushes to `main`. Rebuild locally before committing when using the file-upload interface. Upload source files at repository root, built files under `dist`, and image variants under `dist/assets`.

The older Sites preview remains separate and private. Its hosting manifest is retained; do not replace the public GitHub Pages URL with the preview URL or copy public indexing settings to a private preview.

## Inquiry routing

On October 26, 2026, the old Dubsado form displayed “This form can no longer be used” and disabled Send. Public links now lead to the on-site email composer and phone option. No inquiry delivery or CRM completion is claimed. To reconnect a working managed form, verify the new URL and owner first, enter it in `managed_inquiry_url`, then rebuild. Update contact/FAQ/privacy wording to match the actual service. Check delivery and receipt with the owner.

## Analytics and search setup

`analytics_measurement_id` is empty by default. No Google Analytics request is made until a real ID is configured and the visitor allows optional analytics. The implementation records page views and intent clicks, not booking or inquiry completions. URLs omit query strings/fragments; events do not contain guest names, messages, dates, emails, or phone numbers. Confirm cross-domain support with ResNexus before claiming reservation attribution.

Use `search_console_verification` for an owner-provided HTML verification token. Then verify the URL-prefix property and submit `sitemap.xml`. GitHub project sites cannot control host-root robots.txt from a project subdirectory; a missing robots.txt does not block indexing.

See MAINTENANCE.md for remaining account setup, property details, and the report implementation record.
