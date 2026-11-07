# Friday Security Brief: weekly runbook

Followed every Friday by the cloud routine. Jax approved auto-publishing on 2026-11-06,
on the condition that every fact is sourced. Accuracy beats volume, always.

## 1. Research (window: previous Saturday through today, Friday)

Use web search in extended mode (very recent news). Open every source you cite and
confirm its date is inside the window.

- **CISA KEV additions.** Fetch
  `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`
  and list entries whose `dateAdded` is in the window. Pick the 2 to 4 that matter most.
  Every CVE ID, vendor, product and date you publish must match this JSON exactly.
- **2 to 3 confirmed incidents.** Use reputable outlets only: CISA, vendor advisories,
  Reuters, AP, BleepingComputer, The Record, SecurityWeek, Krebs, Dark Reading,
  The Hacker News. Report scope, numbers and attribution exactly as the source states them.
  Leave out leak-site claims that the victim hasn't confirmed.
- **1 to 3 AI security items.** Cover attacks on or with AI, LLM or agent vulnerabilities,
  prompt injection, and AI governance moves.

If a section has nothing solid, say so in one line instead of padding it.

## 2. Write the post

Create `content/posts/YYYY-MM-DD-friday-security-brief.html`, using today's date.
Copy the structure of `content/posts/2026-11-06-friday-security-brief.html` exactly:
front-matter comment, then the `card tldr` "The short version" box, then these sections:

- Patch this week
- AI security
- Incidents
- What I would do on Monday
- Sources

Rules:
- **Title:** `Friday Security Brief: <the top 2 or 3 stories>`. Keep it under 110 characters.
- **Description:** 1 or 2 sentences that name the key products and CVEs (this is the SEO
  text).
- **Tags:** 5 to 8, the specific product and threat names.
- **Voice:** Jax speaks in the first person. Plain English, short sentences, no hype.
- **Facts versus opinion:** facts go in normal paragraphs, each with an inline link to its
  source. Opinion goes only in `<p class="why"><b>My take:</b> ...</p>`, and never adds
  new facts.
- **No em dashes anywhere.** The build fails if one appears.
- **Don't invent anything:** no invented URLs, numbers, dates, quotes or attributions.
  Don't call something exploited unless KEV or the vendor says so.
- **Product names only:** never mention TheZaraAI clients, Outpost Gray, or any private
  person by name.
- **Length:** 700 to 1,100 words.

## 3. Build and check

```
python3 -I tools/build.py
python3 -I -c "import xml.dom.minidom as m; m.parse('feed.xml'); m.parse('sitemap.xml')"
```

Both must succeed. Then re-read the post once, against the KEV JSON and your sources.

## 4. Publish

Commit only `content/posts/<new file>`, `blog/`, `index.html`, `feed.xml`, `sitemap.xml`
and `llms.txt`. Use the message `Friday Security Brief YYYY-MM-DD`, then push to `main`.
GitHub Pages publishes within about a minute.

Then confirm these three URLs return 200:
- `https://iamjax.me/blog/friday-security-brief-YYYY-MM-DD/`
- `https://iamjax.me/feed.xml`
- `https://iamjax.me/`

## 5. If something goes wrong

If the build fails, the push is rejected, or the research doesn't support a credible post,
don't publish a weak one. Stop and report what happened in the run output.
