#!/usr/bin/env python3
"""Static site generator for folphs.org.

Edit content in this file, then run:  python3 build.py
Every page is written to <slug>/index.html so URLs stay clean (no .html).
All internal links are relative, so the site works both on
GitHub Pages (username.github.io/folphs-website/) and on a custom domain.
"""
import json, os, re, pathlib

ROOT = pathlib.Path(__file__).parent

# ---------------------------------------------------------------- settings
EMAIL = "folphs@gmail.com"
INSTAGRAM = "https://www.instagram.com/lphschicago/"
FB_PAGE = "https://www.facebook.com/people/Friends-of-Lincoln-Park-High-School/61586578040811/"
FB_PARENTS_GROUP = "https://www.facebook.com/groups/2832926726795889/"
COFFEE_SIGNUP = "https://www.signupgenius.com/go/20F0D4DABA72BABF85-57854378-coffee#/"
VOLUNTEER_FORM = "https://tinyurl.com/FOLPHS-Volunteer-Interest-Form"
SPIRIT_STORE = "https://lphsspirit.square.site/"
MARQUEE_BUY = "https://folphs.z2systems.com/np/clients/folphs/product.jsp?product=1&"
RAISE_RIGHT = "https://www.raiseright.com/enroll"
RAISE_RIGHT_CODE = "G9BASLZ6VWIN"
LIBRARY_WISHLIST = "https://r20.rs6.net/tn.jsp?f=0018LaIUc4j_zHDc_KpnaaF9YY_IR_bkQeAwWqzXrxKsWWqGLdiq3C3wsxVgO-Lwlt297EsT4KserWTY-ClMrl0Gl0GMed9q8Ki6smSaIiNX0SYBpte50hGKivSFVp6sauwtDrPd1lwXEUjxg3rE8-ZKTHBzKbCciiPukrNq3AhX5ZH57WfWvz4rsMmfaAE5dG4EC6nqiAmrwWthIJfLrtrVA==&c=QocJfDCmcT671qFqXg1FQmEeD0e2zlIxWJOCSK6RO7DrDX7xicDUgg==&ch=et-egfdEIZpUalm6v60sq7AqiP8ME1RSloLmhf74OkHKRRoRKl2ZIg=="
TRIBUNE = "https://www.chicagotribune.com/2026/06/22/cps-budget-problems-school-fundraising/"
TAX_ID = "E99474484"
SITE_URL = "https://folphs.org"
# Path the site is served from. "/folphs-website/" on GitHub Pages preview; change to "/" once folphs.org points here.
SITE_BASE = "/"

# Online donation link for the Legacy Fund (Keely is creating it).
# Leave as None until it arrives: buttons then point to the Ways to Give section.
DONATE_URL = "https://fundraise.givesmart.com/form/eX2F7g?vid=1sqbel"

# --------------------------------------------------------------- helpers
def rel(depth, path):
    """Relative link from a page at `depth` to site path like 'about/' or '' (home)."""
    pre = "../" * depth
    if path.startswith("#"):
        return path
    return (pre + path) if (pre + path) else "./"

NAV = [
    ("Legacy Fund", "legacy-fund/", None),
    ("About", None, [("What We Do", "about/"), ("2026-27 Board Members", "about/#board")]),
    ("Events", None, [("2026-27 Calendar", "events/"), ("Coffee with the Principal", "events/#coffee"), ("Attend a Meeting", "stay-in-touch/#meetings")]),
    ("Stay in Touch", None, [("Instagram and Groups", "stay-in-touch/"), ("Monthly Meetings", "stay-in-touch/#meetings"), ("Meeting Minutes", "meeting-minutes/")]),
    ("Ways to Give", None, [("Lions Legacy Fund", "legacy-fund/#give"), ("Donate by Zelle", "ways-to-give/#zelle"), ("Marquee Messages", "ways-to-give/#marquee"), ("Raise Right Gift Cards", "ways-to-give/#raise-right"), ("Spirit Wear", "ways-to-give/#spirit-wear"), ("Library Wish List", "ways-to-give/#library")]),
    ("Sponsors", None, [("Become a Sponsor", "sponsors/"), ("Our Sponsors", "sponsors/#current")]),
    ("Get Involved", "get-involved/", None),
    ("Past Events", "past-events/", None),
]

IG_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>'
FB_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-7.5H16l.5-3h-3V8.6c0-.9.3-1.6 1.6-1.6h1.6V4.3c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.3H8v3h2.5V21h3z"/></svg>'

def donate_href(depth):
    # Roona: the online link is one way to pay; Zelle and check are listed too.
    return rel(depth, "legacy-fund/#give")

def header(depth, current):
    items = []
    for label, href, sub in NAV:
        if sub:
            is_cur = bool(current) and any(s[1].split("#")[0] == current for s in sub)
            subs = "".join(f'<li><a href="{rel(depth, h)}">{t}</a></li>' for t, h in sub)
            items.append(f'<li><details class="{"current" if is_cur else ""}"><summary>{label}</summary><ul class="sub">{subs}</ul></details></li>')
        else:
            cur = ' aria-current="page"' if current and href == current else ""
            items.append(f'<li><a href="{rel(depth, href)}"{cur}>{label}</a></li>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
<a class="brand" href="{rel(depth, '')}" aria-label="Friends of Lincoln Park High School, home"><img class="seal" src="{rel(depth, 'assets/img/lincoln-park-high-school-seal.png')}" alt="Lincoln Park High School seal" width="400" height="400"><img src="{rel(depth, 'assets/img/friends-of-lincoln-park-high-school-logo.png')}" alt="FOLPHS, Friends of Lincoln Park High School" width="900" height="322"></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav class="nav" id="site-nav" aria-label="Main"><ul>{"".join(items)}</ul>
<a class="btn btn-gold" href="{donate_href(depth)}">Donate</a></nav>
</div></header>'''

def footer(depth):
    r = lambda p: rel(depth, p)
    return f'''<footer class="site-footer"><div class="wrap">
<div class="cols">
<div><img class="logo" src="{r('assets/img/friends-of-lincoln-park-high-school-logo-white.png')}" alt="FOLPHS, Friends of Lincoln Park High School" width="900" height="306">
<p>A parent-run, volunteer organization supporting every student at Lincoln Park High School in Chicago.</p>
<p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<div><h2>Give</h2><ul><li><a href="{r('legacy-fund/')}">Lions Legacy Fund</a></li><li><a href="{r('ways-to-give/')}">Ways to Give</a></li><li><a href="{r('sponsors/')}">Become a Sponsor</a></li></ul></div>
<div><h2>Join Us</h2><ul><li><a href="{r('stay-in-touch/#meetings')}">Monthly Meetings</a></li><li><a href="{r('events/')}">2026-27 Calendar</a></li><li><a href="{r('get-involved/')}">Volunteer</a></li><li><a href="{r('meeting-minutes/')}">Meeting Minutes</a></li></ul></div>
<div><h2>Follow</h2><ul><li><a href="{INSTAGRAM}">Instagram @lphschicago</a></li><li><a href="{FB_PARENTS_GROUP}">All LPHS Parents group</a></li><li><a href="{r('stay-in-touch/')}">Stay in Touch</a></li></ul></div>
</div>
<div class="legal"><span>&copy; 2026 Friends of Lincoln Park High School. FOLPHS is a registered 501(c)(3) nonprofit, tax ID {TAX_ID}.</span><span>FOLPHS is independent of Lincoln Park High School and Chicago Public Schools.</span></div>
</div></footer>
<script>
(function(){{var b=document.querySelector('.menu-toggle'),n=document.getElementById('site-nav');
b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)}});
document.addEventListener('click',function(e){{document.querySelectorAll('.nav details[open]').forEach(function(d){{if(!d.contains(e.target))d.removeAttribute('open')}})}});
n.querySelectorAll('a').forEach(function(a){{a.addEventListener('click',function(){{n.classList.remove('open');b.setAttribute('aria-expanded','false')}})}});
}})();
</script>'''

def page(slug, title, desc, body, current=None, og_img="assets/img/folphs-lions-legacy-fund-share.jpg", out_file=None):
    depth = 0 if out_file else slug.count("/") + (1 if slug else 0)
    canonical = f"{SITE_URL}/{slug}".rstrip("/") if slug else SITE_URL
    html = f'''<!doctype html>
<html lang="en"><head>
{f'<base href="{SITE_BASE}">' if out_file else ""}<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:type" content="website"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/{og_img}"><meta property="og:image:alt" content="{title}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{rel(depth, 'assets/img/folphs-lion-icon.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Albert+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=Oswald:wght@500&family=Playfair+Display:ital,wght@0,900;1,500;1,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(depth, 'assets/site.css')}">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"NGO","name":"Friends of Lincoln Park High School","alternateName":"FOLPHS","url":SITE_URL,"email":EMAIL,"logo":SITE_URL+"/assets/img/friends-of-lincoln-park-high-school-logo.png","sameAs":[INSTAGRAM,FB_PAGE],"address":{"@type":"PostalAddress","addressLocality":"Chicago","addressRegion":"IL","addressCountry":"US"}})}</script>
</head><body>
{header(depth, current)}
<main id="main">
{body(depth) if callable(body) else body}
</main>
{footer(depth)}
</body></html>'''
    out = ROOT / out_file if out_file else (ROOT / slug / "index.html" if slug else ROOT / "index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out

def img(depth, name, alt, w, h, cls="", lazy=True):
    return f'<img src="{rel(depth, "assets/img/" + name)}" alt="{alt}" width="{w}" height="{h}"{" loading=\"lazy\"" if lazy else ""}{f" class=\"{cls}\"" if cls else ""}>'

GOALS = [
    ("Update exercise equipment", "Support student stamina and wellness with new fitness equipment."),
    ("Keep one Chromebook for every student", "Replace aging laptops to maintain the 1:1 Chromebook ratio."),
    ("Fund student scholarships", "Help students take on academic endeavors and national competitions."),
    ("Protect music and drama", "Weather-safe storage for music and drama department instruments and items."),
    ("Build a space for social workers", "A deserving space where social workers can counsel students."),
]

def goals_list():
    return "<ol class=\"goals\">" + "".join(f"<li><div><h3>{t}</h3><p>{d}</p></div></li>" for t, d in GOALS) + "</ol>"

TIERS_ROWS = [
    ("Your logo in lights on the LPHS Armitage St. digital marquee", "5 weeks", "2 to 4 weeks", "1 week"),
    ("Exclusive recognition in school-wide communication reaching students, parents, staff and alumni", True, False, False),
    ("Advertising material available for circulation at the Spring Gala", True, True, False),
    ("Logo on the FOLPHS website*", True, True, True),
    ("Logo on the Armitage St. printed banner*", True, True, True),
    ("Appreciation throughout Legacy Fund communications", True, True, True),
    ("Visibility in FOLPHS social media posts", True, True, True),
]

def tiers_table():
    rows = []
    for i, (label, *vals) in enumerate(TIERS_ROWS):
        cells = []
        for v in vals:
            if v is True: cells.append('<td class="yes"><span class="sr-only" style="position:absolute;left:-9999px">Included</span></td>')
            elif v is False: cells.append('<td class="no"><span aria-label="Not included">&ndash;</span></td>')
            else: cells.append(f"<td>{v}</td>")
        rows.append(f'<tr{" class=\"hl\"" if i == 0 else ""}><td>{label}</td>{"".join(cells)}</tr>')
    return f'''<div class="table-wrap"><table class="tiers">
<caption style="position:absolute;left:-9999px">2026-27 business sponsorship levels and benefits</caption>
<thead><tr><th scope="col">Sponsorship benefits</th>
<th scope="col"><span class="tier">Leader of the Pack</span><span class="amt">$5,000+</span></th>
<th scope="col"><span class="tier">Member of the Pride</span><span class="amt">$2,000+</span></th>
<th scope="col"><span class="tier">Roar of the Lion</span><span class="amt">$1,000+</span></th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<p class="caption">*Logo size is based on sponsorship level.</p>'''

# ------------------------------------------------------------------ pages
def home(d):
    return f'''
<section class="legacy-hero on-navy" aria-labelledby="hero-title">
 <div class="wrap grid">
  <div class="copy">
   <span class="status-pill">2026-27 Annual Giving Campaign</span>
   <h1 id="hero-title" class="wordmark">Lions <span class="gold">Legacy</span><span class="fund">Fund</span></h1>
   <p class="tag">Invest in the Pride.</p>
   <p>Every gift to the Lions Legacy Fund goes straight to the Lincoln Park High School experience: new Chromebooks, fitness equipment, student scholarships and better spaces for staff and students.</p>
   <div class="cta-row">
    <a class="btn btn-gold" href="{donate_href(d)}">Give to the Legacy Fund</a>
    <a class="btn btn-ghost" href="{rel(d, 'legacy-fund/')}">See what we&rsquo;re funding</a>
   </div>
  </div>
  <a class="flyer-card" href="{rel(d, 'legacy-fund/')}" aria-label="Lions Legacy Fund campaign flyer">{img(d, 'lions-legacy-fund-2026-27-flyer.webp', 'Lions Legacy Fund flyer: Invest in the Pride, 2026-27 goals are new Chromebooks, health and fitness, student scholarships and staff spaces', 1000, 1470, lazy=False)}</a>
 </div>
</section>
<div class="gold-band"><div class="wrap"><span>Invest in a stronger LPHS for generations of Lions</span></div></div>

<section class="after-hero" aria-labelledby="impact-title">
 <div class="wrap">
  <span class="eyebrow">Last year, together</span>
  <h2 id="impact-title">You gave. Here&rsquo;s what changed.</h2>
  <p class="lede">LP Lions in every grade and at every gift size came through for all of our students.</p>
  <div class="stats">
   <div class="stat big"><div class="num">$150,000+</div><div class="label">Raised for LPHS in 2025-26</div></div>
   <div class="stat"><div class="num">$50K</div><div class="label">Computer lab, fully funded</div></div>
   <div class="stat"><div class="num">31</div><div class="label">New computers, plus 2 printers and 9 kits</div></div>
  </div>
  <ul class="checks" style="margin-top:48px">
   <li>Fully funded the history department&rsquo;s training at the AHA conference</li>
   <li>Amplified the auditorium with a new speaker</li>
   <li>Supported sports with gym upgrades, including a new logo and paint</li>
   <li>Refurbished instruments and helped clubs like Model UN compete</li>
  </ul>
 </div>
</section>

<section class="band-navy" aria-labelledby="goals-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow" style="color:var(--gold-light)">The 2026-27 goals</span>
   <h2 id="goals-title">What your gift will build this year</h2>
   <p>Chicago Public Schools funding is always in flux. The Legacy Fund covers what the school budget can&rsquo;t, and it reaches every student.</p>
   <div class="cta-row"><a class="btn btn-gold" href="{donate_href(d)}">Give now</a></div>
  </div>
  {goals_list()}
 </div>
</section>

<section aria-labelledby="sponsor-title">
 <div class="wrap split rev">
  <div class="figure plain">{img(d, 'folphs-2026-27-business-sponsorship-levels.webp', '2026-27 FOLPHS business sponsorship chart with three levels: Leader of the Pack $5,000+, Member of the Pride $2,000+, Roar of the Lion $1,000+', 1400, 1030)}</div>
  <div>
   <span class="eyebrow">For local businesses</span>
   <h2 id="sponsor-title">Put your logo in lights on Armitage</h2>
   <p>Sponsor the Legacy Fund and your business shows up on the LPHS digital marquee, the Armitage St. banner, our website and social media, in front of thousands of neighborhood families.</p>
   <div class="cta-row"><a class="btn btn-navy" href="{rel(d, 'sponsors/')}">See sponsor levels</a><a class="btn btn-ghost" href="mailto:{EMAIL}?subject=Lions%20Legacy%20Fund%20sponsorship">Email us</a></div>
  </div>
 </div>
</section>

<section class="band-cream" aria-labelledby="join-title">
 <div class="wrap">
  <span class="eyebrow">Be part of the Pride</span>
  <h2 id="join-title">Come to a meeting. Grab a coffee. Follow along.</h2>
  <div class="feature-links">
   <a class="fl navy" href="{rel(d, 'stay-in-touch/#meetings')}">
    <span class="eyebrow">Monthly meetings</span>
    <div class="big-date">2nd Tuesday</div>
    <p>Every month at 6:00 pm at LPHS. Everyone is welcome, new families especially.</p>
    <span class="go">Meeting details &rarr;</span></a>
   <a class="fl" href="{rel(d, 'events/#coffee')}"><span class="eyebrow">Coffee with the Principal</span><h3>Sign up for a monthly coffee with Dr. Steinmiller</h3><span class="go">Reserve a spot &rarr;</span></a>
   <a class="fl" href="{rel(d, 'events/')}"><span class="eyebrow">2026-27 calendar</span><h3>Every key date for the school year in one place</h3><span class="go">View calendar &rarr;</span></a>
  </div>
  <div class="social-row"><a class="primary" href="{INSTAGRAM}">{IG_SVG} Follow @lphschicago on Instagram</a><a href="{rel(d, 'get-involved/')}">Volunteer with FOLPHS</a></div>
 </div>
</section>

<section aria-labelledby="about-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow">Who we are</span>
   <h2 id="about-title">Parents and neighbors, working for every LPHS student</h2>
  </div>
  <div>
   <p>Friends of Lincoln Park High School (FOLPHS) is a parent-run, volunteer-based organization that improves educational and cultural opportunities for all students at Lincoln Park High School in Chicago. We do it through fundraising, volunteering and community-building events all year long.</p>
   <p><a href="{rel(d, 'about/')}">Learn what we do and meet the 2026-27 board</a></p>
  </div>
 </div>
</section>'''

def legacy(d):
    return f'''
<section class="legacy-hero on-navy" aria-labelledby="hero-title">
 <div class="wrap grid">
  <div class="copy">
   <span class="status-pill">Kicking off soon</span>
   <h1 id="hero-title" class="wordmark">Lions <span class="gold">Legacy</span><span class="fund">Fund</span></h1>
   <p class="tag">Invest in a stronger LPHS for generations of Lions.</p>
   <p>The Lions Legacy Fund is the 2026-27 annual giving campaign from Friends of Lincoln Park High School. It runs through the end of December.</p>
   <div class="cta-row"><a class="btn btn-gold" href="{donate_href(d)}">Give now</a><a class="btn btn-ghost" href="#sponsor">Sponsor as a business</a></div>
  </div>
  <div class="flyer-card">{img(d, 'lions-legacy-fund-2026-27-flyer.webp', 'Lions Legacy Fund flyer: Invest in the Pride, 2026-27 goals are new Chromebooks, health and fitness, student scholarships and staff spaces', 1000, 1470, lazy=False)}</div>
 </div>
</section>
<div class="gold-band"><div class="wrap"><span>A stronger LPHS for generations of Lions</span></div></div>

<section class="after-hero" aria-labelledby="letter-title">
 <div class="wrap">
  <span class="eyebrow">A letter to our neighbors</span>
  <h2 id="letter-title">Why we&rsquo;re asking</h2>
  <div class="letter">
   <p>Dear Future Sponsor, I am personally asking you to invest in us.</p>
   <p><strong>Lincoln Park High School, ranked in the top 3% by US News&rsquo; list of Best U.S. High Schools, is the hub for academic consistency, creativity &amp; community!</strong> We represent nearly 2,200 students from all city zip codes, 93% are college-bound, 86%+ enroll in AP courses, plus plenty of participation in over 60 clubs &amp; more than 25 sports.</p>
   <p><strong>Thanks to our community, last year&rsquo;s fall fundraiser was a success: we raised about $150,000</strong> to build a new computer lab (equipped with 3-D printers), amplify our auditorium with a new speaker, and send teachers to training. But there is so much more to do, now!</p>
   <p>As a local, neighborhood business, your financial support is not only a chance to assist us, but is also a unique opportunity to gain goodwill with widespread recognition, both within &amp; around our school community; <strong>we&rsquo;ll provide prime advertising on Armitage St. as well as social media recognition, so that together, we can achieve all these goals:</strong></p>
   <ul class="checks">
    <li>Update exercise equipment to support student stamina &amp; wellness</li>
    <li>Replace laptops to maintain the 1:1 ratio of Chromebooks for every student</li>
    <li>Contribute to student scholarships for academic endeavors &amp; national competitions</li>
    <li>Protect music &amp; drama department items with weather-safe storage</li>
    <li>Construct a deserving space for social workers to counsel students</li>
   </ul>
   <p>Since CPS is always in flux, <strong>your investment equals 6% of LPHS&rsquo; budget, and is essential to enriching our experiences!</strong> (See: <a href="{TRIBUNE}">Chicago Tribune</a>.) It&rsquo;s easy to give, here&rsquo;s how:</p>
   <ul class="checks">
    <li><strong>Credit Card:</strong> donate through our <a href="{DONATE_URL}">online link</a> (quick &amp; convenient!)</li>
    <li><strong>Zelle:</strong> at <a href="{rel(d, 'ways-to-give/#zelle')}">{EMAIL}</a> (lower transaction fees = greater gifts!)</li>
    <li><strong>Check:</strong> we&rsquo;ll personally pick it up! (just contact: <a href="mailto:{EMAIL}">{EMAIL}</a>)</li>
   </ul>
   <p>Deepen your connection to our community, demonstrate commitment to education, and know your neighborhood patrons, we hope you&rsquo;ll help.</p>
   <p style="margin-top:32px">In partnership,</p>
   <p class="sig">Roona Shah</p>
   <p class="note">Mom, Parent, and Secretary for Friends of Lincoln Park High School<br>www.folphs.org, tax-i.d. #{TAX_ID}</p>
  </div>
 </div>
</section>

<section class="band-cream" id="give" aria-labelledby="give-title">
 <div class="wrap">
  <span class="eyebrow">It&rsquo;s easy to give</span>
  <h2 id="give-title">Three ways to give</h2>
  <div class="give-grid">
   <div class="give feature">
    <h3>Credit Card</h3>
    <p>Donate through our online link (quick &amp; convenient!)</p>
    {f'<a class="btn btn-gold" href="{DONATE_URL}">Donate online</a>' if DONATE_URL else '<p class="note">Our online giving page opens with the campaign kickoff. Check back soon, or give by Zelle or check today.</p>'}
   </div>
   <div class="give" id="zelle-give">
    <h3>Zelle</h3>
    <p>At <strong>{EMAIL}</strong> (lower transaction fees = greater gifts!)</p>
    <p class="note">Add &ldquo;Legacy Fund&rdquo; and your email in the memo.</p>
    <a class="btn btn-ghost" href="{rel(d, 'ways-to-give/#zelle')}">Show the Zelle QR code</a>
   </div>
   <div class="give">
    <h3>Check</h3>
    <p>We&rsquo;ll personally pick it up! (just contact: <strong>{EMAIL}</strong>)</p>
    <a class="btn btn-ghost" href="mailto:{EMAIL}?subject=Legacy%20Fund%20check%20pickup">Email {EMAIL}</a>
   </div>
  </div>
 </div>
</section>

<section class="band-navy" aria-labelledby="goals-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow" style="color:var(--gold-light)">Together we can achieve</span>
   <h2 id="goals-title">The 2026-27 goals</h2>
   <p>Since CPS funding is always in flux, gifts to FOLPHS make a real difference in the LPHS budget. The <a href="{TRIBUNE}">Chicago Tribune</a> reported this summer on how Chicago schools are turning to outside revenue amid the CPS budget crunch.</p>
  </div>
  {goals_list()}
 </div>
</section>

<section aria-labelledby="impact-title">
 <div class="wrap split">
  <div class="figure">{img(d, 'folphs-2025-26-fundraising-results.webp', 'Shining a light on our successes: together we raised over $150,000 in 2025-26, including a fully funded $50,000 computer lab with 31 computers, 2 printers and 9 kits', 1100, 1105)}</div>
  <div>
   <span class="eyebrow">Last year&rsquo;s results</span>
   <h2 id="impact-title">Over $150,000 raised for LPHS</h2>
   <p>Thanks to our community, last year&rsquo;s fall fundraiser reflected LP Lions loyalty in every grade and at every gift size. Together we:</p>
   <ul class="checks">
    <li>Fully funded a $50,000 computer lab with 31 computers, 2 printers and 9 kits</li>
    <li>Fully funded the history department&rsquo;s training at the AHA conference</li>
    <li>Amplified the auditorium with a new speaker</li>
    <li>Supported sports with gym upgrades, including a new logo and paint</li>
    <li>Refurbished instruments and paved the way for clubs like Model UN to compete</li>
   </ul>
   <p><a href="{rel(d, 'past-events/#giving-2025')}">See the 2025 campaign and our donor families</a></p>
  </div>
 </div>
</section>

<section class="band-cream" id="sponsor" aria-labelledby="sponsor-title">
 <div class="wrap">
  <span class="eyebrow">Business sponsorships</span>
  <h2 id="sponsor-title">Join the LPHS Pride as a sponsor</h2>
  <p class="lede">Your financial support is also a unique opportunity to gain goodwill with widespread recognition, within and around our school community.</p>
  {tiers_table()}
  <div class="cta-row"><a class="btn btn-navy" href="mailto:{EMAIL}?subject=Lions%20Legacy%20Fund%20sponsorship">Email {EMAIL} to sponsor</a></div>
 </div>
</section>

'''

def about(d):
    # (name, role, photo file in assets/img or None). Add a headshot by dropping it in assets/img and naming it here.
    board = [("Colin O&rsquo;Brien", "President", "folphs-board-colin-obrien.jpg"), ("Keely Selko", "Vice President", "folphs-board-keely-selko.jpg"), ("Mavia Lozano", "Treasurer", None), ("Roona Shah", "Secretary", "folphs-board-roona-shah.jpg")]
    def photo(n, f):
        if f:
            return f'<img class="headshot" src="{rel(d, "assets/img/" + f)}" alt="{n.replace("&rsquo;", "\'")}" width="200" height="200" loading="lazy">'
        return f'<img class="headshot seal" src="{rel(d, "assets/img/lincoln-park-high-school-seal.png")}" alt="Lincoln Park High School seal, photo of {n.replace("&rsquo;", "\'")} coming soon" width="400" height="400" loading="lazy">'
    people = "".join(f'<li>{photo(n, f)}<div class="name">{n}</div><div class="role">{r}</div></li>' for n, r, f in board)
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">About FOLPHS</span><h1>What we do</h1><p>Parents, volunteers and neighbors improving educational and cultural opportunities for all students at Lincoln Park High School.</p></div></section>
<section aria-labelledby="mission-title">
 <div class="wrap split">
  <div>
   <h2 id="mission-title">Fundraising, volunteering and community building, all year long</h2>
   <p>Friends of Lincoln Park High School (FOLPHS) is a parent-run, volunteer-based organization seeking to improve educational and cultural opportunities for all students at Lincoln Park High School (LPHS) in Chicago, IL. With our combined energy, ideas and commitment, we fulfill our mission through fundraising, volunteering and community-building events throughout the school year.</p>
   <p>Each year, our collective work raises significant dollars to support the school and its activities. With your support, we can accomplish even more.</p>
   <div class="cta-row"><a class="btn btn-navy" href="{rel(d, 'get-involved/')}">Join us</a><a class="btn btn-ghost" href="{rel(d, 'stay-in-touch/#meetings')}">Attend a meeting</a></div>
  </div>
  <div>
   <ul class="goals" style="margin-top:0">
    <li><div><h3>Fundraising</h3><p>Pledge drive, online auction, annual gala, corporate and individual sponsorships, grant writing and more.</p></div></li>
    <li><div><h3>Communications</h3><p>Parent newsletter, association articles and PR announcements.</p></div></li>
    <li><div><h3>School spirit</h3><p>Teacher appreciation, school recruitment, the <a href="{SPIRIT_STORE}">online Spirit Wear store</a>, parent mixers, IB hospitality and student volunteer opportunities.</p></div></li>
   </ul>
  </div>
 </div>
</section>
<section class="band-cream" id="board" aria-labelledby="board-title">
 <div class="wrap">
  <span class="eyebrow">Officers</span>
  <h2 id="board-title">2026-27 Board Members</h2>
  <ul class="people">{people}</ul>
  <div class="callout" style="margin-top:48px"><p><strong>Committees:</strong> we always need more hands. Email <a href="mailto:{EMAIL}">{EMAIL}</a> to get involved.</p></div>
 </div>
</section>'''

CAL = [
    ("Aug. 24", "First Day of School"), ("Aug. 27", "Parent Mixer @ Marquee Lounge"), ("Sept. 7", "No School"),
    ("Sept. 8", "First FOLPHS Meeting of the Year", True), ("Sept. 11", "Clubapoolza"), ("Sept. 17", "FOLPHS Trivia Night", True),
    ("Sept. 17", "Underclassman Picture Day"), ("Sept. 24", "HoCo Game"), ("Sept. 25", "No School"), ("Sept. 26", "HoCo Dance"),
    ("Oct. 1", "Senior Picture Day"), ("Oct. 12", "No School"), ("Oct. 17", "Open House"), ("Oct. 17", "PSAT Test"),
    ("Nov. 2", "No School, Parent/Teacher Conferences"), ("Nov. 3", "No School"), ("Nov. 11", "No School"),
    ("Nov. 23-27", "Thanksgiving Break"), ("Dec. 21-Jan. 4", "Holiday Break"), ("Jan. 18", "No School"), ("Jan. 29", "No School"),
    ("Feb. 15", "No School"), ("Feb. 23", "No School"), ("March 22-26", "Spring Break"), ("March 30", "College Fair"),
    ("April 6", "No School"), ("April 12", "No School, Parent/Teacher Conferences"), ("April 23-May 19", "IB Test Window"),
    ("May 3-14", "AP Test Window"), ("May 7", "Grad Night"), ("May 31", "No School"), ("June 3", "Graduation"), ("June 14", "Last Day of School"),
]

def events(d):
    items = "".join(f'<li class="{"folphs" if len(e) > 2 else ""}"><span class="d">{e[0]}</span><span>{e[1]}</span></li>' for e in CAL)
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">Upcoming events</span><h1>2026-27 School Year</h1><p>Key LPHS dates for families, plus FOLPHS events. Meetings are held the 2nd Tuesday of every month.</p></div></section>
<section aria-labelledby="cal-title">
 <div class="wrap split cal-split">
  <div>
   <h2 id="cal-title">Calendar</h2>
   <ul class="cal">{items}</ul>
   <div class="callout"><p><strong>Be on the lookout for:</strong> Winter Formal in January, ACT Testing in February, the Spring Gala in April and Prom in May.</p></div>
  </div>
  <div>
   <div class="figure">{img(d, 'lphs-2026-27-school-year-calendar.webp', '2026-2027 LPHS school year calendar magnet with key dates and FOLPHS meetings on the 2nd Tuesday of every month', 900, 1350)}</div>
   <p class="caption">The 2026-27 calendar magnet. <a href="{rel(d, 'assets/img/lphs-2026-27-school-year-calendar.webp')}">Open full size</a></p>
  </div>
 </div>
</section>
<section class="band-cream" id="coffee" aria-labelledby="coffee-title">
 <div class="wrap split rev">
  <div class="figure">{img(d, 'lphs-coffee-with-the-principal.webp', 'Coffee with the Principal: sign up to have coffee with Dr. Steinmiller', 900, 900)}</div>
  <div>
   <span class="eyebrow">Monthly coffee</span>
   <h2 id="coffee-title">Coffee with the Principal</h2>
   <p>Sign up to have coffee with LPHS Principal Dr. Steinmiller. Spots are limited each month, so reserve yours early.</p>
   <div class="cta-row"><a class="btn btn-navy" href="{COFFEE_SIGNUP}">Sign up on SignUpGenius</a></div>
  </div>
 </div>
</section>'''

def stay(d):
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">Stay in touch</span><h1>Follow along with the Pride</h1><p>News, events and photos from FOLPHS, plus parent groups where veteran LPHS families answer questions.</p></div></section>
<section aria-labelledby="ig-title">
 <div class="wrap split">
  <div>
   <h2 id="ig-title">Follow us on Instagram</h2>
   <p>Instagram is where FOLPHS shares campaign updates, event photos and reminders.</p>
   <div class="social-row"><a class="primary" href="{INSTAGRAM}">{IG_SVG} @lphschicago</a></div>
  </div>
  <div>
   <h2 style="font-size:32px">Find support on Facebook</h2>
   <p>These LPHS groups offer parents support and access to &ldquo;veteran&rdquo; parents who can answer questions.</p>
   <div class="social-row"><a href="{FB_PARENTS_GROUP}">{FB_SVG} All LPHS Parents</a><a href="{FB_PAGE}">{FB_SVG} Friends of Lincoln Park HS</a></div>
  </div>
 </div>
</section>
<section class="band-cream" id="meetings" aria-labelledby="meet-title">
 <div class="wrap split rev">
  <div class="figure">{img(d, 'folphs-meetings-2nd-tuesday-6pm.webp', 'FOLPHS is moving to a new time: please join us on the 2nd Tuesday of every month at 6pm at LPHS', 900, 1125)}</div>
  <div>
   <span class="eyebrow">Attend our meetings</span>
   <h2 id="meet-title">New time: the 2nd Tuesday of every month</h2>
   <p>FOLPHS meetings are held on the <strong>2nd Tuesday of every month at 6:00 pm at LPHS</strong>. All are welcome, and it&rsquo;s never too early to get involved. Look for meeting information in your email.</p>
   <p>Can&rsquo;t make it but still want to help? <a href="{rel(d, 'get-involved/')}">See how to get involved</a>.</p>
   <div class="cta-row"><a class="btn btn-navy" href="{rel(d, 'events/')}">See the 2026-27 calendar</a><a class="btn btn-ghost" href="{rel(d, 'meeting-minutes/')}">Read meeting minutes</a></div>
  </div>
 </div>
</section>'''

MONTHS = "august september october november december january february march april may".split()

def minutes(d):
    data = json.loads((ROOT / "minutes/index.json").read_text())
    groups = {"2025-26 School Year": [], "2024-25 School Year": [], "2023-24 School Year": [], "2022-23 School Year": [], "Earlier Years": []}
    def year_of(label):
        m = re.match(r"(\w+) (\d{4})", label)
        if not m: return "Earlier Years"
        mon, yr = m.group(1).lower(), int(m.group(2))
        start = yr if MONTHS.index(mon) <= 4 else yr - 1
        return f"{start}-{str(start + 1)[2:]} School Year"
    for label, f in data:
        groups.setdefault(year_of(label), []).append((label, f))
    order = lambda lf: (int(re.search(r"\d{4}", lf[0]).group()) if re.search(r"\d{4}", lf[0]) else 0, MONTHS.index(lf[0].split()[0].lower()) if lf[0].split()[0].lower() in MONTHS else 0)
    blocks = ['<div class="minutes-year"><h3>2026-27 School Year</h3><p class="note">Minutes from this year&rsquo;s meetings will be posted here after each meeting.</p></div>']
    for g, items in groups.items():
        if not items: continue
        links = "".join(f'<a href="{rel(d, "minutes/" + f)}">{l}<span class="ft">{f.rsplit(".", 1)[1]}</span></a>' for l, f in sorted(items, key=order))
        blocks.append(f'<div class="minutes-year"><h3>{g}</h3><div class="minutes-grid">{links}</div></div>')
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">Meeting minutes</span><h1>Minutes from every meeting</h1><p>All FOLPHS meetings are open to the public. Please come join us on the 2nd Tuesday of every month.</p></div></section>
<section><div class="wrap">{"".join(blocks)}</div></section>'''

def give(d):
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">Ways to give</span><h1>Every gift reaches LPHS students</h1><p>Almost all of the LPHS budget goes to personnel. Your support funds everything else that makes high school great.</p></div></section>
<section aria-labelledby="lf-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow">The big one this fall</span>
   <h2 id="lf-title">Give to the Lions Legacy Fund</h2>
   <p>Our 2026-27 annual giving campaign funds new Chromebooks, fitness equipment, student scholarships and better spaces for staff and students.</p>
   <div class="cta-row"><a class="btn btn-gold" href="{donate_href(d)}">Give to the Legacy Fund</a></div>
  </div>
  <div class="figure plain">{img(d, 'lions-legacy-fund-2026-27-header.webp', 'Lions Legacy Fund: invest in a stronger LPHS for generations of Lions', 1280, 281)}</div>
 </div>
</section>
<section class="band-cream" id="why" aria-labelledby="why-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow">Why should I give?</span>
   <h2 id="why-title">The funding gap is real</h2>
  </div>
  <div>
   <p>All CPS schools, including LPHS, are significantly underfunded. LPHS actually receives less per student than the average CPS school, because our student demographics don&rsquo;t qualify us for federal grants. Almost 100% of the LPHS budget goes to our amazing personnel, which leaves little for other critical parts of the high school experience, such as:</p>
   <ul class="checks">
    <li>Classroom technology and Chromebooks for every student</li>
    <li>Gym and weight room equipment</li>
    <li>Senior graduation activities and buses for college visits</li>
    <li>Faculty professional development and staff appreciation</li>
    <li>Textbooks, novel collections, music and science classroom supplies</li>
   </ul>
   <p>We&rsquo;re counting on your support to fund these needs and keep LPHS&rsquo; culture of excellence going.</p>
  </div>
 </div>
</section>
<section id="zelle" aria-labelledby="zelle-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow">No card fees</span>
   <h2 id="zelle-title">Donate or pay by Zelle</h2>
   <p>Prefer not to use a credit card? We&rsquo;d love that too, since it saves us the 3% fee. Scan the QR code in your banking app or find us at <strong>{EMAIL}</strong>.</p>
   <div class="callout"><p>Please add a note in the memo that tells us what you&rsquo;re giving toward (for example Legacy Fund, Marquee or Business Sponsorship) and include your email. We can&rsquo;t contact you otherwise.</p></div>
  </div>
  <div class="figure" style="max-width:420px">{img(d, 'folphs-zelle-donation-qr-code.webp', 'Zelle QR code to pay Friends of Lincoln Park High School', 700, 607)}</div>
 </div>
</section>
<section class="band-cream" id="marquee" aria-labelledby="marquee-title">
 <div class="wrap split rev">
  <div class="figure">{img(d, 'lphs-marquee-sign-armitage.webp', 'The LPHS marquee sign on Armitage showing a personalized congratulations message', 1200, 900)}</div>
  <div>
   <span class="eyebrow">$50 donation</span>
   <h2 id="marquee-title">Put a name in lights on the marquee</h2>
   <p>Send a personalized message to someone special for a week on the LPHS marquee sign. Thank a teacher, wish your student happy birthday or good luck, or congratulate someone on an impressive achievement.</p>
   <p>Every dollar goes to FOLPHS general funds to support our students.</p>
   <p class="note">Messages are subject to the approval of Lincoln Park High School.</p>
   <div class="cta-row"><a class="btn btn-navy" href="{MARQUEE_BUY}">Buy a marquee message</a></div>
  </div>
 </div>
</section>
<section id="raise-right" aria-labelledby="rr-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow">Shop and support</span>
   <h2 id="rr-title">Raise Right gift cards</h2>
   <p>When you buy gift cards through Raise Right, a percentage of every purchase goes back to LPHS. For example, a Bath &amp; Body Works gift card returns 12% to the school.</p>
   <p>Enroll with our code:</p>
   <p><span class="code">{RAISE_RIGHT_CODE}</span></p>
   <div class="cta-row"><a class="btn btn-navy" href="{RAISE_RIGHT}">Enroll at Raise Right</a></div>
  </div>
  <div>
   <h3>What are the fees?</h3>
   <ul class="checks">
    <li>$0.29 per transaction when you pay from a linked bank account</li>
    <li>1% for debit card payments</li>
    <li>3% for credit card payments</li>
   </ul>
   <p class="note">Processing fees go to the payment processors, not to LPHS. The school earns the percentage donated by each retailer. Friends and family can enroll too.</p>
  </div>
 </div>
</section>
<section class="band-cream" id="spirit-wear" aria-labelledby="sw-title">
 <div class="wrap split rev">
  <div class="figure plain" style="max-width:460px">{img(d, 'lphs-spirit-wear.webp', 'LPHS spirit wear: hoodies, t-shirts, sweatpants and shorts', 636, 741)}</div>
  <div>
   <span class="eyebrow">Show your Lions pride</span>
   <h2 id="sw-title">Shop spirit wear</h2>
   <p><strong>Online:</strong> open to anyone, 24/7. Pick up your order in the main building cafeteria on the first Wednesday of every month.</p>
   <p><strong>In person:</strong> open to current LP students, staff and community on the first Wednesday of every month during the school year, September through June, 11:00 am to 2:30 pm in the Main Building Cafeteria. Incoming students can shop on designated days such as Freshman Connection and Quick Start.</p>
   <p>Need a different pick-up arrangement? Email Spirit Wear lead Leslie at <a href="mailto:sw4lphs@gmail.com">sw4lphs@gmail.com</a> before you order.</p>
   <div class="cta-row"><a class="btn btn-navy" href="{SPIRIT_STORE}">Shop the online store</a></div>
  </div>
 </div>
</section>
<section id="library" aria-labelledby="lib-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow">The LPHS library</span>
   <h2 id="lib-title">Buy a book for the library</h2>
   <p>The LPHS library receives no CPS funds for new books, so our community fills the gap. Thanks to your generosity the library has already added 175 new books. Based on student requests, librarian Ms. Giannopoulos keeps a wish list of titles the library is missing.</p>
   <div class="cta-row"><a class="btn btn-navy" href="{LIBRARY_WISHLIST}">See the library wish list</a></div>
  </div>
  <div class="figure">{img(d, 'lphs-library-book-drive.webp', 'A tall stack of library books', 1000, 666)}</div>
 </div>
</section>'''

SPONSORS = [
    ("Champion Level", [("Berman Auto Group", "berman-auto-group", None)]),
    ("Leader Level", [("Milito&rsquo;s Auto Repair", "militos-auto-repair", "https://militosautorepair.com/")]),
    ("Member Level", [("Orangetheory Fitness", "orangetheory-fitness", None), ("Wrightwood Neighbors Association", "wrightwood-neighbors", None), ("Sheffield Neighborhood Association", "sheffield-neighborhood-association", None), ("Naveen&rsquo;s Cuisine", "naveens-cuisine", None)]),
    ("Friend Level", [("Don Pez Fish Tacos", "don-pez-fish-tacos", None), ("Chicago Costume Company", "chicago-costume-company", None)]),
]

def sponsors(d):
    tiers = []
    for i, (tier, items) in enumerate(SPONSORS):
        logos = "".join((f'<a href="{u}">' if u else "<span>") + img(d, f"sponsors/{s}.webp", n.replace("&rsquo;", "'"), 500, 300) + ("</a>" if u else "</span>") for n, s, u in items)
        tiers.append(f'<div class="sponsor-tier"><h3>{tier}</h3><div class="logos{" lg" if i < 2 else ""}">{logos}</div></div>')
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">Business sponsors</span><h1>Become a sponsor</h1><p>As a neighborhood business, you have a unique opportunity to support our students while gaining local visibility and goodwill.</p></div></section>
<section aria-labelledby="become-title">
 <div class="wrap">
  <h2 id="become-title">2026-27 sponsorship levels</h2>
  <p class="lede">Partner with FOLPHS to deepen your connection to the community and show your commitment to education and to the Lincoln Park neighborhood. Every level supports the Lions Legacy Fund.</p>
  {tiers_table()}
  <div class="split" style="margin-top:64px">
   <div><h3>Ready to join the Pride?</h3><p>Email us today and we&rsquo;ll find the right level for your business.</p><div class="cta-row"><a class="btn btn-navy" href="mailto:{EMAIL}?subject=FOLPHS%20business%20sponsorship">Email {EMAIL}</a></div></div>
   <div class="figure plain">{img(d, 'folphs-2026-27-business-sponsorship-levels.webp', '2026-27 FOLPHS sponsorship chart: Leader of the Pack $5,000+, Member of the Pride $2,000+, Roar of the Lion $1,000+', 1400, 1030)}<p class="caption" style="padding:0 16px 12px">Download-ready chart to share with your team.</p></div>
  </div>
 </div>
</section>
<section class="band-cream" id="current" aria-labelledby="current-title">
 <div class="wrap">
  <span class="eyebrow">Thank you</span>
  <h2 id="current-title">Our 2025-26 sponsors</h2>
  <p>These neighborhood businesses stood with LPHS students last year.</p>
  {"".join(tiers)}
 </div>
</section>'''

def involved(d):
    roles = ["Legacy Fund / fall pledge drive committee", "Grant writing", "Corporate sponsorship", "Volunteer coordinator", "Brick campaign", "Marquee messages", "Board members (usually meet in person once a month)"]
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">Get involved</span><h1>You will make a difference</h1><p>Help with a project or join the board. Even if you&rsquo;re new to LPHS, it&rsquo;s never too early to get involved.</p></div></section>
<section aria-labelledby="open-title">
 <div class="wrap split">
  <div>
   <h2 id="open-title">Open FOLPHS positions</h2>
   <p>We&rsquo;re looking for board members and for help in a number of specific areas.</p>
   <ul class="pill-list">{"".join(f"<li>{r}</li>" for r in roles)}</ul>
  </div>
  <div class="letter" style="padding:40px">
   <h3>Interested? Questions?</h3>
   <p>Fill out our volunteer interest form or email us. We look forward to meeting and working with you.</p>
   <div class="cta-row"><a class="btn btn-navy" href="{VOLUNTEER_FORM}">Volunteer interest form</a><a class="btn btn-ghost" href="mailto:{EMAIL}?subject=Volunteering%20with%20FOLPHS">Email us</a></div>
  </div>
 </div>
</section>
<section class="band-cream" aria-labelledby="meet2-title">
 <div class="wrap split">
  <div><h2 id="meet2-title">The easiest first step: come to a meeting</h2></div>
  <div><p>FOLPHS meets the 2nd Tuesday of every month at 6:00 pm at LPHS. Everyone is welcome.</p><p><a href="{rel(d, 'stay-in-touch/#meetings')}">Meeting details</a> &middot; <a href="{rel(d, 'events/')}">2026-27 calendar</a></p></div>
 </div>
</section>'''

def past(d):
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">Past events</span><h1>Thank you for showing up</h1><p>A look back at recent FOLPHS campaigns and galas.</p></div></section>
<section id="giving-2025" aria-labelledby="g25-title">
 <div class="wrap">
  <span class="eyebrow">2025 Annual Giving Campaign</span>
  <h2 id="g25-title">Shine Together: over $150,000 raised</h2>
  <div class="figure plain" style="margin:32px 0">{img(d, 'folphs-2025-shine-together-campaign.webp', 'Shine Together, the 2025 FOLPHS annual giving campaign', 1280, 364)}</div>
  <div class="split">
   <div class="figure">{img(d, 'folphs-2025-26-fundraising-results.webp', 'Shining a light on our successes: over $150,000 raised to enhance educational experiences at LPHS', 1100, 1105)}</div>
   <div>
    <h3>Thank you to our donor families</h3>
    <p>LP Lions loyalty showed up in every grade and at every gift size. Thank you to every family who gave.</p>
    <div class="figure plain">{img(d, 'folphs-2025-26-donor-families.webp', 'List of 2025-26 donor families who supported the annual giving campaign', 1280, 1447)}</div>
   </div>
  </div>
 </div>
</section>
<section class="band-cream" id="gala-2026" aria-labelledby="gala26-title">
 <div class="wrap split">
  <div>
   <span class="eyebrow">April 25, 2026 at Mary Jo McGuire&rsquo;s</span>
   <h2 id="gala26-title">Blue &amp; Gold Fundraising Gala</h2>
   <p>A fun, no-tie-required evening supporting our students, with an online auction of experiences and gift cards from beloved local spots. Proceeds supported performing arts upgrades, teacher development, books and college prep, and facility improvements.</p>
   <p>Thank you to event sponsor Berman Auto Group and to everyone who attended and bid.</p>
  </div>
  <div class="figure" style="max-width:480px">{img(d, 'folphs-2026-blue-gold-gala-thank-you.webp', 'Blue and Gold Fundraising Gala thank-you note with auction item pickup details and event photos', 1000, 1294)}</div>
 </div>
</section>
<section id="gala-2025" aria-labelledby="gala25-title">
 <div class="wrap split rev">
  <div class="figure">{img(d, 'folphs-2025-walk-in-the-park-gala.webp', 'A Walk in the Park fundraising gala, April 26 at the Floating World Gallery, celebrating 150 years of LPHS', 1200, 927)}</div>
  <div><span class="eyebrow">2025 Spring Gala</span><h2 id="gala25-title">A Walk in the Park</h2><p>Our 2025 Spring Gala at the Floating World Gallery brought families, staff and neighbors together for an evening of celebration, entertainment and community.</p></div>
 </div>
</section>
'''

NOT_FOUND = lambda d: f'''<section class="page-hero"><div class="wrap"><span class="eyebrow" style="color:var(--gold-light)">Page not found</span><h1>This page moved</h1><p>We refreshed the FOLPHS website. Try the links below.</p><div class="cta-row"><a class="btn btn-gold" href="./">Home</a><a class="btn btn-ghost" href="legacy-fund/">Lions Legacy Fund</a></div></div></section>'''

# Old Wix URLs -> new pages (keeps shared links working)
REDIRECTS = {
    "about": None, "meet-our-board": "about/#board", "what-s-new": "", "upcoming-events": "events/",
    "upcoming-events/2025-26-calendar": "events/", "upcoming-events/monthly-coffee": "events/#coffee",
    "social-media": "stay-in-touch/", "meetings": "stay-in-touch/#meetings", "marquee-messages": "ways-to-give/#marquee",
    "pay-by-zelle": "ways-to-give/#zelle", "ways-to-donate": "ways-to-give/", "ways-to-donate/purchase-gift-card-through-raise-right": "ways-to-give/#raise-right",
    "how-does-raise-right-work": "ways-to-give/#raise-right", "ways-to-donate/purchase-a-book-for-the-library": "ways-to-give/#library",
    "shop-spirit-wear": "ways-to-give/#spirit-wear", "business-sponsors": "sponsors/", "business-sponsors/current-sponsors": "sponsors/#current",
    "business-sponsors/become-a-sponsor": "sponsors/", "volunteer": "get-involved/", "volunteer/join-us": "get-involved/",
    "volunteer/current-volunteer-opportunities": "get-involved/", "copy-of-2026-fundraising-gala": "past-events/#gala-2026",
    "copy-of-2026-fundraising-gala-1": "past-events/#gala-2026", "copy-of-marquee-messages": "past-events/#gala-2026",
    "copy-of-folphs-fundraising-gala-2025": "past-events/#gala-2026", "folphs-fundraising-gala-2025": "past-events/#gala-2025",
    "2024-spring-soiree-fundraiser": "past-events/", "blank": "past-events/#giving-2025", "lphs-cameo-celebrity-list": "past-events/",
}

def redirect_stub(old, new):
    depth = old.count("/") + 1
    target = rel(depth, new)
    out = ROOT / old / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f'<!doctype html><meta charset="utf-8"><title>Moved</title><meta name="robots" content="noindex"><link rel="canonical" href="{SITE_URL}/{new}"><meta http-equiv="refresh" content="0; url={target}"><p>This page moved. <a href="{target}">Continue</a>.</p>', encoding="utf-8")

if __name__ == "__main__":
    page("", "Friends of Lincoln Park High School | Lions Legacy Fund 2026-27", "Friends of Lincoln Park High School (FOLPHS) is a parent-run volunteer organization supporting every LPHS student. Give to the 2026-27 Lions Legacy Fund.", home)
    page("legacy-fund", "Lions Legacy Fund 2026-27 | Friends of Lincoln Park High School", "Give to the Lions Legacy Fund, the 2026-27 annual giving campaign for Lincoln Park High School: Chromebooks, fitness, scholarships and staff spaces.", legacy, "legacy-fund/")
    page("about", "What We Do and 2026-27 Board | FOLPHS", "Friends of Lincoln Park High School is a parent-run, volunteer-based organization. Meet the 2026-27 board members.", about, "about/")
    page("events", "2026-27 Calendar and Coffee with the Principal | FOLPHS", "Key 2026-27 Lincoln Park High School dates, FOLPHS events and the monthly Coffee with the Principal signup.", events, "events/")
    page("stay-in-touch", "Stay in Touch and Monthly Meetings | FOLPHS", "Follow FOLPHS on Instagram, join LPHS parent groups and attend FOLPHS meetings on the 2nd Tuesday of every month at 6 pm.", stay, "stay-in-touch/")
    page("meeting-minutes", "Meeting Minutes | FOLPHS", "Minutes from Friends of Lincoln Park High School meetings, open to the public.", minutes, "meeting-minutes/")
    page("ways-to-give", "Ways to Give | FOLPHS", "Support Lincoln Park High School: Lions Legacy Fund, Zelle, marquee messages, Raise Right gift cards, spirit wear and the library wish list.", give, "ways-to-give/")
    page("sponsors", "Business Sponsors | FOLPHS", "Become a 2026-27 FOLPHS business sponsor: your logo on the LPHS Armitage St. marquee, banner, website and social media.", sponsors, "sponsors/")
    page("get-involved", "Get Involved | FOLPHS", "Volunteer with Friends of Lincoln Park High School or join the board.", involved, "get-involved/")
    page("past-events", "Past Events | FOLPHS", "Past FOLPHS campaigns and galas, including the 2025 Shine Together annual giving campaign.", past, "past-events/")
    page("", "Page not found | FOLPHS", "Page not found.", NOT_FOUND, out_file="404.html")
    for old, new in REDIRECTS.items():
        if new is not None:
            redirect_stub(old, new)
    urls = ["", "legacy-fund", "about", "events", "stay-in-touch", "meeting-minutes", "ways-to-give", "sponsors", "get-involved", "past-events"]
    def page_images(u):
        html = (ROOT / u / "index.html").read_text() if u else (ROOT / "index.html").read_text()
        return sorted(set(re.findall(r'assets/img/([\w/.-]+\.(?:webp|png|jpg))', html)))
    entries = []
    for u in urls:
        imgs = "".join(f"<image:image><image:loc>{SITE_URL}/assets/img/{i}</image:loc></image:image>" for i in page_images(u))
        entries.append(f"<url><loc>{SITE_URL}/{u}</loc>{imgs}</url>")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' + "".join(entries) + "</urlset>\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print("built")
