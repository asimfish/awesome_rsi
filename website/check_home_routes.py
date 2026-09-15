"""Browser regression: summary routes must never redirect to the chip topic.
Requires playwright; pass the site base URL, including trailing slash.
"""
import sys
from playwright.sync_api import sync_playwright
base=sys.argv[1].rstrip('/')+'/'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
 for path in ['','#live','#lab','overview.html']:
  page=browser.new_page()
  page.goto(base+path,wait_until='domcontentloaded');page.wait_for_timeout(500)
  assert '/chip/' not in page.url,(path,page.url)
  assert page.locator('h1').first.inner_text()=='递归自改进走到了哪一步？',(path,page.title())
  page.close()
 browser.close()
print('PASS: homepage, legacy fragments and overview all show the RSI synthesis')
