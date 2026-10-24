# The Audubon Inn website

Static HTML/CSS/JavaScript website for the Audubon Inn. No framework or database is required.

## Editing

- `build.py` contains HTML page templates and the verified booking and inquiry URLs. Run `python build.py` after changing it.
- `dist/style.css` contains visual styles and responsive breakpoints.
- `dist/app.js` contains navigation, dialogs, room filters, local stay planning, seasonal suggestions, and email-draft generation.
- `dist/assets/` contains local optimized property and USFWS photos and the heron SVG favicon.
- `dist/sources.html` documents property/destination sources and photo credits.
- Open `dist/index.html` directly for local browsing, or serve the static `dist` directory.

## Behavior

Reservations link to the hotel's verified ResNexus account. The local date planner is explicitly a planning aid; guests re-enter dates at the provider. No live room inventory or reservation is created locally.

Events link to the hotel's existing Dubsado inquiry form. No form is submitted by this site automatically.

Contact form data stays in the browser. It creates a reviewable draft and mailto link. The visitor must open their email app and send it.

## Content review

Research checked October 23, 2026. Existing official pages contain conflicting room counts, capacities, prices, desk hours, and policies. This site uses 18 rooms based on the user's confirmed count and the official homepage. It omits conflicting capacities/prices/policies and directs guests to confirm current arrangements. The bar's published Friday/Saturday 5 p.m. opening is shown with a prompt to confirm closing times/private-event closures.

Property photos originate on hotelonthemarsh.com or its image CDN. They are authentic property photos for this private redesign, not a claim about current furnishings. USFWS sunrise and boardwalk images are identified as public domain with credits in the site. Secure permission for public reuse of hotel photos or replace them with owner-supplied originals before making the site public.

The GitHub Pages version is public. The original Sites preview is private. This repository does not change the hotel’s existing booking or event services.

## Wedding page photographs

Edit `wedding-content.html`, which is the source for `dist/weddings.html`.
Search for `WEDDING PHOTO 1` through `WEDDING PHOTO 4`. Each HTML comment
names the suggested image file, the `src` to replace, and the alt text to update.
Put your photos in `dist/assets/`, then run `python -X utf8 build.py`.
The four current SVG placeholders are intentional and can be replaced individually.
Rebuilding updates the local files; publishing is a separate step.


## Local attractions, dining, and calendar

- Edit `area-content.html`: search `ACTIVITY 1`, `ACTIVITY 2`, and `ACTIVITY 3` for the three blank attraction sections.
- Edit `dining-content.html`: search `DINING 1` through `DINING 4` for four blank restaurants. Each comment explains where to put the photo, change its src/alt, and add details.
- Photos belong in `dist/assets/`. The current placeholders are SVG files.
- Edit `local-events.json` for the calendar year, month, dates, titles, local times, venues, and organizer URLs. `local_calendar.py` builds the matching month grid and agenda. It supports multiple events on one day.
- The calendar is a static October 2026 edition, not an auto-updating feed. When changing months, also update the dated headings, verification date, and October link text in `area-content.html`.
- Run `python -X utf8 build.py` then `python -X utf8 check_site.py`; publish separately to update the hosted website.
- Sources checked October 24, 2026: https://horiconmarsh.org/events/ ; https://www.fws.gov/refuge/horicon/visit-us ; https://themeatingplacemayville.com/ ; https://themeatingplacemayville.com/contact-the-meating-place/ ; https://themeatingplacemayville.com/events-specials/ .


## GitHub Pages

The `Publish website` workflow publishes `dist/` when changes reach `main`. In Settings > Pages, select GitHub Actions as the build source. Rebuild with `python -X utf8 build.py` before committing page edits.
