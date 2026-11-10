#!/usr/bin/env python3
"""Build the iamjax.me blog: post pages, blog index, RSS feed, sitemap, llms.txt,
and the "latest briefs" block on the homepage.

Usage (from the repo root):  python3 -I tools/build.py

Posts live in content/posts/YYYY-MM-DD-slug.html. Each file starts with a
front-matter comment, then an HTML body fragment:

    <!--
    title: Friday Security Brief: ...
    description: One or two sentences for search results and the feed.
    date: 2026-11-06
    tags: CISA KEV, Ivanti, Agentic AI
    -->
    <section class="tldr card">...</section>
    <h2>...</h2> ...

The build fails if any page contains an em dash (house style) or if a post is
missing a required field. Standard library only.
"""
import datetime as dt
import html
import json
import pathlib
import re
import sys
from email.utils import format_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://iamjax.me"
POSTS_DIR = ROOT / "content" / "posts"
BLOG_DIR = ROOT / "blog"
AUTHOR = "Jax Scott"
BLOG_NAME = "Friday Security Brief"
BLOG_DESC = ("A weekly, plain-English read on the security and AI threats that mattered this week, "
             "from Jax Scott, former Special Operations cyber warrant officer and founder of TheZaraAI.")
SPEAKER_UPDATED = "2026-11-10"  # bump when speaker/index.html changes
PERSON_ID = f"{SITE}/#jax"  # the Person entity defined in index.html JSON-LD
REQUIRED = ("title", "description", "date")
EM_DASH = "—"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700;800'
         '&family=Instrument+Serif:ital@0;1&display=swap">')

ATMOS = ('<div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>'
         '<canvas id="mesh" aria-hidden="true"></canvas><div class="grain" aria-hidden="true"></div>'
         '<div class="vignette" aria-hidden="true"></div>')

NAV = '''<nav class="nav" aria-label="Main">
  <a class="brand" href="/"><span class="dot"></span>Jax Scott</a>
  <ul>
    <li><a href="/#about">About</a></li>
    <li><a href="/#talks">Talks</a></li>
    <li><a href="/speaker/">Speaker Kit</a></li>
    <li><a href="/blog/">Security Brief</a></li>
    <li><a href="https://thezaraai.com" rel="noopener">TheZaraAI</a></li>
  </ul>
  <a class="btn btn-primary btn-sm" href="/#book">Book Jax</a>
</nav>'''

RSS_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 11a9 9 0 0 1 9 9h-2a7 7 0 0 0-7-7v-2zm0-7a16 16 0 0 1 16 16h-2A14 '
            '14 0 0 0 4 6V4zm2 13a2 2 0 1 1 0 4 2 2 0 0 1 0-4z"/></svg>')

FOOT = '''<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div><h4>Jax Scott</h4><p style="color:var(--muted);max-width:34ch;margin:0">AI security keynote speaker, former Special Operations cyber warrant officer, founder of TheZaraAI.</p></div>
      <div><h4>Work</h4><ul>
        <li><a href="https://thezaraai.com" rel="noopener">TheZaraAI.com</a></li>
        <li><a href="/#book">Book a keynote</a></li>
        <li><a href="/speaker/">Speaker kit and bios</a></li>
        <li><a href="/#talks">Talks</a></li></ul></div>
      <div><h4>Read + listen</h4><ul>
        <li><a href="/blog/">Friday Security Brief</a></li>
        <li><a href="/feed.xml">RSS feed</a></li>
        <li><a href="/#podcast">2 Cyber Chicks</a></li>
        <li><a href="https://medium.com/@the_zaraai" rel="noopener">Medium</a></li></ul></div>
      <div><h4>Elsewhere</h4><ul>
        <li><a href="https://instagram.com/the_Zaraai" rel="noopener">Instagram</a></li>
        <li><a href="https://x.com/the_Zaraai" rel="noopener">X</a></li>
        <li><a href="/legal/privacy.html">Privacy</a></li>
        <li><a href="/legal/terms.html">Terms</a></li></ul></div>
    </div>
    <p class="big grad">IAMJAX.ME</p>
    <p class="copy">&copy; <span data-year>2026</span> Jax Scott. Speaking enquiries: <a href="mailto:jax@thezaraai.com">jax@thezaraai.com</a></p>
  </div>
</footer>'''


def parse_post(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(.*?)-->\s*(.*)\Z", raw, re.S)
    if not m:
        sys.exit(f"{path.name}: missing front-matter comment")
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    for k in REQUIRED:
        if not meta.get(k):
            sys.exit(f"{path.name}: missing '{k}'")
    meta["date_obj"] = dt.date.fromisoformat(meta["date"])
    meta["slug"] = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem) + "-" + meta["date"]
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["body"] = m.group(2).strip()
    meta["url"] = f"{SITE}/blog/{meta['slug']}/"
    return meta


def nice_date(d):
    return d.strftime("%B %-d, %Y")


def head(title, desc, url, og_type="website", extra=""):
    t, d = html.escape(title), html.escape(desc)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<script>document.documentElement.classList.add('js')</script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#06070b">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og-jax-scott.jpg">
<meta property="og:image:alt" content="Jax Scott, AI security keynote speaker">
<meta property="og:site_name" content="Jax Scott">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@the_Zaraai">
<link rel="alternate" type="application/rss+xml" title="{BLOG_NAME} by Jax Scott" href="{SITE}/feed.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' x2='1'%3E%3Cstop offset='0' stop-color='%23e8b96a'/%3E%3Cstop offset='1' stop-color='%238b5cf6'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='64' height='64' rx='16' fill='%2306070b'/%3E%3Ctext x='32' y='44' font-family='Arial' font-weight='800' font-size='34' text-anchor='middle' fill='url(%23g)'%3EJ%3C/text%3E%3C/svg%3E">
{FONTS}
<link rel="stylesheet" href="/assets/site.css">
{extra}
</head>'''


def post_page(p):
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["description"],
        "datePublished": p["date"],
        "dateModified": p.get("updated", p["date"]),
        "mainEntityOfPage": p["url"],
        "url": p["url"],
        "image": f"{SITE}/assets/img/og-jax-scott.jpg",
        "keywords": ", ".join(p["tags"]),
        "about": [{"@type": "Thing", "name": t} for t in p["tags"]],
        "inLanguage": "en-US",
        "isPartOf": {"@type": "Blog", "name": BLOG_NAME, "url": f"{SITE}/blog/"},
        "author": {"@type": "Person", "@id": PERSON_ID, "name": AUTHOR, "url": f"{SITE}/",
                   "jobTitle": "AI Security Keynote Speaker and Founder of TheZaraAI",
                   "worksFor": {"@type": "Organization", "name": "TheZaraAI", "url": "https://thezaraai.com"}},
        "publisher": {"@type": "Person", "@id": PERSON_ID, "name": AUTHOR, "url": f"{SITE}/"},
    }
    crumbs = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": BLOG_NAME, "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": p["url"]},
        ],
    }
    extra = (f'<meta property="article:published_time" content="{p["date"]}">'
             f'<meta name="author" content="{AUTHOR}">'
             f'<script type="application/ld+json">{json.dumps(ld)}</script>'
             f'<script type="application/ld+json">{json.dumps(crumbs)}</script>')
    tags = "".join(f"<li>{html.escape(t)}</li>" for t in p["tags"])
    return f'''{head(p["title"] + " | Jax Scott", p["description"], p["url"], "article", extra)}
<body>
<a class="skip" href="#main">Skip to content</a>
{ATMOS}
{NAV}
<header class="article-hero wrap" style="max-width:760px">
  <p class="crumbs"><a href="/">Home</a> / <a href="/blog/">{BLOG_NAME}</a></p>
  <p class="kicker">{BLOG_NAME} &middot; <time datetime="{p["date"]}">{nice_date(p["date_obj"])}</time></p>
  <h1>{html.escape(p["title"])}</h1>
  <div class="byline"><img src="/assets/img/jax-scott-headshot-640.webp" alt="" width="44" height="44">
    <span>By <b style="color:var(--ink)">Jax Scott</b>, former Special Operations cyber warrant officer and founder of TheZaraAI</span></div>
</header>
<main id="main" class="article">
{p["body"]}
<ul class="tags">{tags}</ul>
<div class="card cta-box">
  <p class="kicker">Need this in front of your team?</p>
  <p style="font-size:1.15rem;color:var(--ink)">I brief boards, security teams and conference stages on exactly this kind of threat. For hands-on help securing your AI, my team at TheZaraAI does the work.</p>
  <div class="cta-row"><a class="btn btn-primary" href="/#book">Book Jax to speak</a><a class="btn btn-ghost" href="https://thezaraai.com" rel="noopener">Visit TheZaraAI &#8599;</a></div>
</div>
<p style="margin-top:2rem"><a class="rss" href="/feed.xml">{RSS_ICON}Subscribe to the {BLOG_NAME} RSS feed</a></p>
</main>
{FOOT}
<script src="/assets/site.js" defer></script>
</body>
</html>
'''


def brief_card(p, heading="h3"):
    return (f'<a class="card brief" href="/blog/{p["slug"]}/" data-tilt data-reveal>'
            f'<time datetime="{p["date"]}">{p["date_obj"].strftime("%b %-d, %Y")}</time>'
            f'<span><{heading}>{html.escape(p["title"])}</{heading}><p>{html.escape(p["description"])}</p></span>'
            f'<span class="arrow" aria-hidden="true">&rarr;</span></a>')


def blog_index(posts):
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": BLOG_NAME, "url": f"{SITE}/blog/",
          "description": BLOG_DESC, "author": {"@type": "Person", "name": AUTHOR, "url": f"{SITE}/"},
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"], "datePublished": p["date"]}
                       for p in posts]}
    cards = "\n".join(brief_card(p, "h2") for p in posts) or '<p class="lede">The first brief lands Friday.</p>'
    return f'''{head(BLOG_NAME + ": weekly cybersecurity and AI security news | Jax Scott", BLOG_DESC, SITE + "/blog/",
                extra=f'<script type="application/ld+json">{json.dumps(ld)}</script>')}
<body>
<a class="skip" href="#main">Skip to content</a>
{ATMOS}
{NAV}
<header class="article-hero wrap">
  <p class="crumbs"><a href="/">Home</a> / {BLOG_NAME}</p>
  <p class="kicker">Every Friday</p>
  <h1 style="max-width:16ch">The <span class="serif grad">Friday</span> Security Brief</h1>
  <p class="lede">{BLOG_DESC}</p>
  <a class="rss" href="/feed.xml">{RSS_ICON}Subscribe via RSS</a>
</header>
<main id="main" class="wrap" style="padding-bottom:5rem">
  <div class="briefs">
{cards}
  </div>
</main>
{FOOT}
<script src="/assets/site.js" defer></script>
</body>
</html>
'''


def rfc822(d):
    return format_datetime(dt.datetime(d.year, d.month, d.day, 12, 0, tzinfo=dt.timezone.utc))


def feed(posts):
    items = []
    for p in posts[:30]:
        cats = "".join(f"<category>{html.escape(t)}</category>" for t in p["tags"])
        items.append(f'''  <item>
    <title>{html.escape(p["title"])}</title>
    <link>{p["url"]}</link>
    <guid isPermaLink="true">{p["url"]}</guid>
    <pubDate>{rfc822(p["date_obj"])}</pubDate>
    <dc:creator>{AUTHOR}</dc:creator>
    <description>{html.escape(p["description"])}</description>
    {cats}
    <content:encoded><![CDATA[{p["body"].replace("]]>", "]]&gt;")}]]></content:encoded>
  </item>''')
    built = rfc822(posts[0]["date_obj"]) if posts else rfc822(dt.date.today())
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel>
  <title>{BLOG_NAME} by Jax Scott</title>
  <link>{SITE}/blog/</link>
  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>{html.escape(BLOG_DESC)}</description>
  <language>en-us</language>
  <lastBuildDate>{built}</lastBuildDate>
  <image><url>{SITE}/assets/img/og-jax-scott.jpg</url><title>{BLOG_NAME} by Jax Scott</title><link>{SITE}/blog/</link></image>
{chr(10).join(items)}
</channel>
</rss>
'''


def sitemap(posts):
    today = dt.date.today().isoformat()
    urls = [(f"{SITE}/", today, "1.0"), (f"{SITE}/speaker/", SPEAKER_UPDATED, "0.9"),
            (f"{SITE}/blog/", posts[0]["date"] if posts else today, "0.9")]
    urls += [(p["url"], p["date"], "0.8") for p in posts]
    urls += [(f"{SITE}/legal/{n}.html", "2026-11-06", "0.2") for n in ("privacy", "terms", "disclaimer", "refund-policy")]
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{m}</lastmod><priority>{pr}</priority></url>" for u, m, pr in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def llms(posts):
    lines = [
        "# Jax Scott (iamjax.me)",
        "",
        "> Jaclyn \"Jax\" Scott is an AI security keynote speaker and founder of TheZaraAI (https://thezaraai.com). "
        "She has more than 20 years in cybersecurity: former U.S. Army Cyber and Electronic Warfare Special Operations "
        "Warrant Officer, former Deputy CISO and VP of Cybersecurity at Pearson, RSA Conference speaker, co-author of "
        "Cybersecurity Career Master Plan and co-host of the award-winning 2 Cyber Chicks podcast.",
        "",
        "## Facts",
        "- More than 20 years in cybersecurity.",
        "- U.S. Army Cyber and Electronic Warfare Special Operations Warrant Officer who supported SOCOM, SOCEUR, "
        "the Department of State and NATO. Still serves as a Chief Warrant Officer in the 75th Innovation Command.",
        "- Former Deputy CISO and VP of Cybersecurity at Pearson.",
        "- Co-author of the book Cybersecurity Career Master Plan.",
        "- Co-host of the award-winning 2 Cyber Chicks podcast.",
        "- RSA Conference speaker.",
        "- Wrote the Jax Act as a board member of the Special Operations Association of America.",
        "- Master's in Cybersecurity Risk Management, Georgetown University.",
        "- Founder of TheZaraAI, which provides AI operations, secure AI assessments and custom AI agents.",
        "- Speaks on agentic AI security, Shadow AI, prompt injection, deepfake defense, AI governance, "
        "AI risk for boards and the C-suite, and women in cybersecurity and AI.",
        "",
        "## Key pages",
        f"- [Home]({SITE}/): bio, keynote topics, FAQ and booking",
        f"- [Speaker kit]({SITE}/speaker/): copy-ready short, medium and long bios, keynote topics, formats, "
        "audiences and headshot download",
        f"- [Book Jax to speak]({SITE}/#book): speaking enquiries go to jax@thezaraai.com",
        f"- [{BLOG_NAME}]({SITE}/blog/): weekly cybersecurity and AI security news analysis, published Fridays",
        f"- [RSS feed]({SITE}/feed.xml)",
        "- [TheZaraAI](https://thezaraai.com): Jax's company, for consulting and implementation work",
        "",
        "## Profiles elsewhere",
        "- [RSA Conference](https://www.rsaconference.com/experts/jax-scott)",
        "- [SANS](https://www.sans.org/profiles/jax-scott)",
        "- [Special Operations Association of America](https://soaa.org/team/jaclyn-scott/)",
        "- [Irregular Warfare Initiative](https://www.irregularwarfare.org/jaclyn-jax-scott/)",
        "- [Thinkers360](https://www.thinkers360.com/tl/profiles/view/16205)",
        "- [2 Cyber Chicks podcast on ITSPmagazine](https://itspmagazine.com/2-cyber-chicks-podcast)",
        "",
        "## Recent briefs",
    ]
    lines += [f"- [{p['title']}]({p['url']}): {p['description']}" for p in posts[:12]]
    return "\n".join(lines) + "\n"


def update_home(posts):
    path = ROOT / "index.html"
    src = path.read_text(encoding="utf-8")
    cards = "\n".join(brief_card(p) for p in posts[:3]) or '<p class="lede">The first brief lands Friday.</p>'
    new, n = re.subn(r"(<!-- BRIEFS:START -->).*?(<!-- BRIEFS:END -->)", lambda m: f"{m.group(1)}\n{cards}\n{m.group(2)}", src, flags=re.S)
    if n != 1:
        sys.exit("index.html: BRIEFS markers not found")
    path.write_text(new, encoding="utf-8")


def main():
    posts = sorted((parse_post(f) for f in POSTS_DIR.glob("*.html")), key=lambda p: p["date"], reverse=True)
    slugs = [p["slug"] for p in posts]
    if len(slugs) != len(set(slugs)):
        sys.exit("duplicate post slugs")
    for p in posts:
        out = BLOG_DIR / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(post_page(p), encoding="utf-8")
    (BLOG_DIR / "index.html").write_text(blog_index(posts), encoding="utf-8")
    (ROOT / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(posts), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms(posts), encoding="utf-8")
    update_home(posts)

    checked = [ROOT / "index.html", ROOT / "feed.xml", ROOT / "llms.txt", ROOT / "speaker" / "index.html",
               *BLOG_DIR.rglob("*.html")]
    bad = [str(f.relative_to(ROOT)) for f in checked if f.exists() and EM_DASH in f.read_text(encoding="utf-8")]
    if bad:
        sys.exit("em dash found (house style forbids them): " + ", ".join(bad))
    print(f"built {len(posts)} post(s): " + ", ".join(slugs))


if __name__ == "__main__":
    main()
