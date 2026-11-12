#!/usr/bin/env python3
"""Read-only optional browser probe. Never interacts with human verification.

Requires optional Playwright and Chromium; core research verification is offline.
Raw page/screenshot material stays in the ignored local directory.
"""
import datetime
import hashlib
import json
import os
import pathlib
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = 'https://tibiacams.com/watch/e15cded1cdfb?t=0'


def main():
    from playwright.sync_api import sync_playwright
    local = ROOT / 'data/history_round9_local'
    local.mkdir(exist_ok=True)
    responses = []
    with sync_playwright() as p:
        settings = {'executable_path': '/usr/bin/chromium', 'headless': True,
                    'args': ['--no-sandbox', '--disable-dev-shm-usage']}
        proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
        if proxy:
            settings['proxy'] = {'server': proxy}
        browser = p.chromium.launch(**settings)
        page = browser.new_page(viewport={'width': 1280, 'height': 960})
        def response(r):
            parsed = urllib.parse.urlparse(r.url)
            if parsed.hostname == 'tibiacams.com' and parsed.path.startswith('/api/'):
                responses.append({'path': parsed.path, 'status': r.status})
        page.on('response', response)
        page.goto(URL, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(6000)
        screenshot = local / 'browser_probe.png'
        page.screenshot(path=str(screenshot))
        play = [x['status'] for x in responses if x['path'].endswith('/play')]
        modal = page.get_by_text('One moment', exact=True).count() > 0
        out = {'url': URL, 'retrieved_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'method': 'Fresh headless Chromium, normal public page load, no form submission or verification interaction.',
               'page_title': page.title(), 'api_responses': responses,
               'human_check_modal_visible': modal,
               'play_request_status': play[-1] if play else None,
               'recording_frames_inspected': 0, 'skull_room_coverage_verified': False,
               'catalog_date': '2007-01-10', 'catalog_client_version': '7.80',
               'catalog_date_is_authenticated_capture_date': False,
               'screenshot_sha256': hashlib.sha256(screenshot.read_bytes()).hexdigest(),
               'screenshot_location': str(screenshot.relative_to(ROOT)),
               'screenshot_published': False,
               'limits': ['Catalog metadata alone does not show the skull room or count objects.',
                          'No conclusion about a2010matrix change follows from this probe.',
                          'Player assets loading is not recording playback.']}
        browser.close()
    (ROOT / 'results/historical_cam_probe_round9.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
