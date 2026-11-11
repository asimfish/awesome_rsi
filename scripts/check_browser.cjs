/* Browser verification with Playwright. Artifacts go to a temporary folder.
 * Usage: PLAYWRIGHT_MODULE=/path/to/playwright CHROME_BIN=/path/to/chrome node scripts/check_browser.cjs
 * Without overrides, uses a locally installed playwright package and its Chromium.
 * --virtual accepts an in-memory map of repository files on stdin for draft QA.
 */
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const os = require("node:os");
const assert = require("node:assert/strict");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");

async function main() {
  const virtual = process.argv.includes("--virtual");
  const overlay = virtual ? JSON.parse(fs.readFileSync(0, "utf8")) : null;
  const root = virtual ? process.cwd() : path.resolve(__dirname, "..");
  const repos = virtual ? ["awesome_loop_transformer", "awesome_rsi"] : [""];
  const output = fs.mkdtempSync(path.join(os.tmpdir(), "awesome-library-qa-"));
  const get = relative => overlay && Object.hasOwn(overlay, relative) ? Buffer.from(overlay[relative]) : fs.readFileSync(path.join(root, relative));
  const server = http.createServer((req, res) => {
    let relative;
    try {
      relative = decodeURIComponent(new URL(req.url, "http://localhost").pathname).replace(/^\/+/, "") || "index.html";
      const resolved = path.resolve(root, relative);
      if (path.relative(root, resolved).startsWith("..")) { res.writeHead(403).end(); return; }
      const types = { ".html":"text/html; charset=utf-8", ".js":"text/javascript; charset=utf-8", ".css":"text/css; charset=utf-8", ".svg":"image/svg+xml", ".json":"application/json", ".pdf":"application/pdf", ".md":"text/plain; charset=utf-8" };
      const content = get(relative);
      res.writeHead(200, {"Content-Type":types[path.extname(relative)] || "text/plain"});
      res.end(content);
    } catch { if (!res.headersSent) res.writeHead(404); res.end("Not found"); }
  });
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const origin = "http://127.0.0.1:" + server.address().port;
  let browser;
  const reports = [];
  try {
    browser = await chromium.launch({headless:true, ...(process.env.CHROME_BIN ? {executablePath:process.env.CHROME_BIN} : {})});
    for (const repo of repos) {
      const prefix = repo ? repo + "/" : "";
      const config = JSON.parse(get(prefix + "data/site.json"));
      const papers = JSON.parse(get(prefix + "data/library.json"));
      const base = origin + "/" + prefix + "index.html";
      const context = await browser.newContext({viewport:{width:1440,height:1000}, reducedMotion:"reduce"});
      await context.route("**/*", route => route.request().url().startsWith(origin) ? route.continue() : route.abort());
      const page = await context.newPage();
      const errors = [];
      page.on("pageerror", error => errors.push(error.message));
      await page.goto(base, {waitUntil:"networkidle"});
      await page.waitForSelector("body.enhanced");
      const visible = () => page.locator(".paper:not([hidden])");
      const reset = async () => { await page.locator("#reset").click(); };
      const search = config.repo === "awesome_loop_transformer" ? "2502.05171" : "WikiSkill";
      const waitResult = async expected => {
        await page.waitForFunction(n => document.querySelectorAll(".paper:not([hidden])").length === n, expected);
      };
      assert.equal(await visible().count(), 20);
      assert.equal(await page.evaluate(() => /[\u3400-\u9fff]/.test(document.body.innerText)), false);
      await page.screenshot({path:path.join(output, config.repo+"-desktop.png")});
      await page.locator("#core").check();
      assert.equal(await visible().count(), papers.filter(p=>p.core).length);
      await reset();
      await page.locator("#search").fill(search);
      await waitResult(1);
      await page.locator("#search").fill("no-such-reference-zzzzzz");
      await waitResult(0);
      assert.equal(await page.locator("#empty").isVisible(), true);
      await page.locator("#empty-reset").click();
      assert.equal(await visible().count(),20);
      const category = config.categories[1][0];
      await page.locator("[data-category]").filter({hasText:category}).click();
      const ids = await visible().evaluateAll(nodes=>nodes.map(n=>n.id));
      assert(ids.length>0 && ids.every(id=>papers.find(p=>p.id===id).categories.includes(category)));
      await reset();
      const oldest = Math.min(...papers.map(p=>p.year));
      await page.locator("#year").selectOption(String(oldest));
      const oldIds = await visible().evaluateAll(nodes=>nodes.map(n=>n.id));
      assert(oldIds.length>0 && oldIds.every(id=>papers.find(p=>p.id===id).year===oldest));
      await reset();
      await page.locator("#code").check();
      const codeIds = await visible().evaluateAll(nodes=>nodes.map(n=>n.id));
      assert(codeIds.length>0 && codeIds.every(id=>papers.find(p=>p.id===id).links.some(l=>l.label==="Code")));
      await reset();
      if (config.repo === "awesome_rsi") {
        await page.locator("#kind").selectOption("Tool");
        assert.equal(await visible().count(),2);
        await reset();
      }
      await page.locator("#sort").selectOption("title");
      const titles = await visible().locator("h3").allTextContents();
      assert.deepEqual(titles, [...titles].sort((a,b)=>a.localeCompare(b,"en")));
      await reset();
      await page.locator("#more").click();
      assert.equal(await visible().count(),40);
      await reset();
      const button = visible().first().locator("[data-save]");
      await button.click();
      assert.equal(await button.getAttribute("aria-pressed"),"true");
      assert.equal(await button.evaluate(n=>document.activeElement===n),true);
      await page.reload();
      await page.waitForSelector("body.enhanced");
      assert.equal(await page.locator("#saved-count").textContent(),"1");
      await page.locator("#saved").check();
      assert.equal(await visible().count(),1);
      await visible().first().locator("[data-save]").click();
      assert.equal(await visible().count(),0);
      assert.equal(await page.locator("#saved").evaluate(n=>document.activeElement===n),true);
      await reset();
      await page.goto(base+"?q="+encodeURIComponent(search)+"&core=1&sort=title");
      await waitResult(1);
      assert.equal(await page.locator("#core").isChecked(),true);
      assert.equal(await page.locator("#search").inputValue(),search);
      await page.evaluate(()=>Object.defineProperty(navigator,"clipboard",{configurable:true,value:{writeText:async()=>{throw new Error("Clipboard unavailable");}}}));
      await page.locator("#share").click();
      assert.equal(await page.locator("#share-dialog").isVisible(),true);
      assert((await page.locator("#share-url").inputValue()).includes("q="));
      await page.getByRole("button",{name:"Done",exact:true}).click();
      await reset();
      await page.locator("body").click({position:{x:5,y:5}});
      await page.keyboard.press("/");
      assert.equal(await page.locator("#search").evaluate(n=>document.activeElement===n),true);
      await page.keyboard.type("temporary");
      await page.keyboard.press("Escape");
      assert.equal(await page.locator("#search").inputValue(),"");
      for (const width of [320,390,768,1440]) {
        await page.setViewportSize({width,height:900});
        await page.evaluate(()=>window.scrollTo(0,0));
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),"Horizontal page overflow at "+width);
        assert(await page.locator(".overview img").evaluate(n=>n.complete && n.naturalWidth>0),"Overview image did not load");
        if(width===390) {
          await page.screenshot({path:path.join(output,config.repo+"-mobile.png")});
          await page.locator("#library-title").scrollIntoViewIfNeeded();
          await page.screenshot({path:path.join(output,config.repo+"-mobile-library.png")});
        }
      }
      await page.setViewportSize({width:1440,height:1000});
      await page.locator("#library-title").scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(output,config.repo+"-desktop-library.png")});
      await page.goto(origin+"/"+prefix+"guide.html",{waitUntil:"networkidle"});
      assert.equal(await page.locator("h1").count(),1);
      assert.equal(await page.locator(".guide-sections li").count(),5);
      assert.equal(await page.evaluate(()=>/[\u3400-\u9fff]/.test(document.body.innerText)),false);
      assert.deepEqual(errors,[]);
      await context.close();
      const blocked = await browser.newContext();
      await blocked.addInitScript(()=>{
        Object.defineProperty(Storage.prototype,"getItem",{value(){throw new DOMException("Blocked","SecurityError");}});
        Object.defineProperty(Storage.prototype,"setItem",{value(){throw new DOMException("Blocked","SecurityError");}});
      });
      const blockedPage = await blocked.newPage();
      await blockedPage.goto(base);
      await blockedPage.locator(".paper:not([hidden]) [data-save]").first().click();
      assert((await blockedPage.locator("#notice").textContent()).includes("unavailable"));
      assert.equal(await blockedPage.locator("#saved-count").textContent(),"1");
      await blocked.close();
      const noJS = await browser.newContext({javaScriptEnabled:false});
      const fallback = await noJS.newPage();
      await fallback.goto(base);
      assert.equal(await fallback.locator(".paper").count(),papers.length);
      assert.equal(await fallback.locator("#search").isVisible(),false);
      await noJS.close();
      reports.push({repo:config.repo,entries:papers.length,status:"passed",checks:["search","empty state","category/year/resource/code filters","sorting","pagination","saved state and focus","URL restoration","clipboard fallback","keyboard shortcuts","320/390/768/1440px overflow","images","reading guide","blocked storage","no-JavaScript fallback","no page errors"]});
      console.log("PASS "+config.repo);
    }
    fs.writeFileSync(path.join(output,"report.json"),JSON.stringify(reports,null,2));
    console.log(JSON.stringify({output,reports},null,2));
  } finally {
    if(browser) await browser.close();
    await new Promise(resolve=>server.close(resolve));
  }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
