"""Browser checks for navigation, per-paper search and reading controls.
Requires playwright and Chrome. Pass the served site base URL.
"""
import sys
from playwright.sync_api import sync_playwright
base=sys.argv[1].rstrip('/')+'/'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
 for width in [390,1440]:
  context=browser.new_context(viewport={'width':width,'height':1000})
  page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
  for path in ['','overview.html','reports/05_who_grades_the_grader.html','reports/32_last_ai_built_by_humans.html','bytedance/','resources.html','reference.html']:
   page.goto(base+path,wait_until='domcontentloaded')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,path)
   if page.locator('.toc-panel').count():
    assert page.locator('.toc-body').is_visible()==(width>760),(width,path)
    if width<760:
     page.locator('.toc-panel summary').click();assert page.locator('.toc-body').is_visible()
     link=page.locator('.toc-body a').first;link.click();assert not page.locator('.toc-body').is_visible()
   page.locator('#font-size').click();assert page.locator('html').get_attribute('data-large')=='true'
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('large',width,path)
   page.locator('#font-size').click()
  page.goto(base+'papers.html');page.fill('#search','Aspire');assert page.locator('.paper-entry:visible').count()==1
  page.fill('#search','The Last AI Built');assert page.locator('.paper-entry:visible').count()==1
  page.fill('#search','S3Gym');assert page.locator('.paper-entry:visible').count()==1
  page.fill('#search','unmatched-xyz');assert page.locator('#empty').is_visible()
  page.fill('#search','');page.select_option('#category',index=15);assert page.locator('.paper-entry:visible').count()==3
  page.goto(base+'reports.html');page.fill('#search','EvoLM');assert page.locator('.search-card:visible').count()>0
  page.locator('#theme').click();assert page.locator('html').get_attribute('data-theme')=='dark'
  page.reload();assert page.locator('html').get_attribute('data-theme')=='dark'
  assert not errors,errors;context.close()
 browser.close()
print('PASS: responsive TOC, large text, theme persistence, exact paper search and report search')
