#!/usr/bin/env python3
"""
Portfolio Auto Design Committer
================================
Cycles through a curated pool of trending design patches (CSS / JS),
applies the next one to index.html, and commits + pushes to GitHub.

Usage
-----
  python auto_design_commits.py              # apply next patch & commit
  python auto_design_commits.py --dry-run    # preview without writing
  python auto_design_commits.py --reset      # restart the patch cycle
  python auto_design_commits.py --list       # show all patches & status
  python auto_design_commits.py --help       # show this help

Notes
-----
  * Only index.html is modified — CSS/JS are injected into fixed <style> /
    <script> tags and replaced on each run (no accumulation).
  * All existing functionality, layout, and JS logic remain untouched.
  * State is tracked in .design-state.json (gitignored).
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
HTML_FILE   = SCRIPT_DIR / "index.html"
STATE_FILE  = SCRIPT_DIR / ".design-state.json"

CSS_TAG_RE = re.compile(r'<style id="auto-design-patch">.*?</style>', re.DOTALL)
JS_TAG_RE  = re.compile(r'<script id="auto-design-script">.*?</script>', re.DOTALL)

# -----------------------------------------------------------------------------
# Design Patches
# Each patch is a dict with keys:
#   id, name, description, css, js, commit_subject, commit_body
# CSS is injected into <style id="auto-design-patch"> inside <head>.
# JS  is injected into <script id="auto-design-script"> just before </body>.
# Both tags are created on the first run and replaced on subsequent runs.
# -----------------------------------------------------------------------------
PATCHES = [
    # -- 1 --------------------------------------------------------------------
    {
        "id": "scroll-progress-bar",
        "name": "Scroll Progress Indicator",
        "description": "Gradient progress bar pinned to viewport top, tracks scroll depth",
        "css": """\
  /* -- Scroll Progress Indicator -- */
  #scroll-progress {
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    width: 0%;
    background: linear-gradient(90deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%);
    z-index: 10000;
    transition: width 0.08s linear;
    border-radius: 0 2px 2px 0;
    box-shadow: 0 0 10px rgba(168, 85, 247, 0.7);
    pointer-events: none;
  }
""",
        "js": """\
  /* Scroll progress bar */
  (function () {
    var bar = document.createElement('div');
    bar.id = 'scroll-progress';
    document.body.prepend(bar);
    function update() {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (max > 0 ? Math.min((window.scrollY / max) * 100, 100) : 0) + '%';
    }
    window.addEventListener('scroll', update, { passive: true });
    update();
  })();
""",
        "commit_subject": "design: add scroll progress indicator with gradient glow",
        "commit_body": (
            "Adds a modern 3px gradient progress bar pinned to the viewport top.\n"
            "Uses purple→lavender gradient with a subtle glow matching the site accent.\n"
            "No existing functionality, layout, or JS logic is affected."
        ),
    },

    # -- 2 --------------------------------------------------------------------
    {
        "id": "animated-gradient-hero-text",
        "name": "Animated Gradient Hero Text",
        "description": "The hero headline accent span cycles through a flowing gradient animation",
        "css": """\
  /* -- Animated Gradient Hero Text -- */
  @keyframes adp-gradientFlow {
    0%   { background-position: 0%   50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0%   50%; }
  }
  #home h1 > span {
    display: inline-block;
    background: linear-gradient(270deg, #7c3aed, #a855f7, #6366f1, #7c3aed);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: adp-gradientFlow 6s ease infinite;
  }
""",
        "js": "",
        "commit_subject": "design: animate hero headline accent with flowing gradient text",
        "commit_body": (
            "Applies a continuously flowing purple→indigo gradient animation to\n"
            "the 'Full Stack Developer' span in the hero headline.\n"
            "Uses CSS background-clip:text — purely visual, zero layout impact."
        ),
    },

    # -- 3 --------------------------------------------------------------------
    {
        "id": "custom-scrollbar",
        "name": "Custom Branded Scrollbar",
        "description": "Slim scrollbar with purple gradient thumb matching the brand palette",
        "css": """\
  /* -- Custom Branded Scrollbar -- */
  ::-webkit-scrollbar { width: 8px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #7c3aed, #a855f7);
    border-radius: 10px;
    border: 2px solid transparent;
    background-clip: padding-box;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #6d28d9, #9333ea);
    background-clip: padding-box;
  }
  html { scrollbar-width: thin; scrollbar-color: #7c3aed transparent; }
""",
        "js": "",
        "commit_subject": "design: add custom branded scrollbar with gradient thumb",
        "commit_body": (
            "Replaces the default browser scrollbar with a slim purple-gradient thumb.\n"
            "Uses -webkit-scrollbar for Chromium/Safari and scrollbar-color for Firefox.\n"
            "Pure CSS — no JS, no layout shift, no functionality impact."
        ),
    },

    # -- 4 --------------------------------------------------------------------
    {
        "id": "glow-cta-button",
        "name": "Pulsing Glow on Primary CTA",
        "description": "Download Resume button breathes with a purple glow animation",
        "css": """\
  /* -- Pulsing Glow CTA Button -- */
  @keyframes adp-pulseGlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(124,58,237,0.5), 0 4px 15px rgba(124,58,237,0.3); }
    50%       { box-shadow: 0 0 0 8px rgba(124,58,237,0), 0 4px 22px rgba(124,58,237,0.55); }
  }
  #download-resume {
    animation: adp-pulseGlow 2.6s ease-in-out infinite;
    position: relative;
    overflow: hidden;
  }
  #download-resume::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.18) 0%, transparent 55%);
    pointer-events: none;
    border-radius: inherit;
  }
""",
        "js": "",
        "commit_subject": "design: add pulsing glow animation to primary CTA button",
        "commit_body": (
            "Applies a breathing box-shadow pulse and a subtle gloss overlay to #download-resume.\n"
            "Animation uses pure CSS keyframes — no JS or event handlers.\n"
            "Hover transform from the existing Tailwind class still overrides cleanly."
        ),
    },

    # -- 5 --------------------------------------------------------------------
    {
        "id": "glassmorphism-skill-cards",
        "name": "Glassmorphism Skill Cards",
        "description": "Frosted-glass depth on skill cards with purple-tinted hover shadow",
        "css": """\
  /* -- Glassmorphism Skill Cards -- */
  #skills .grid > div {
    background: rgba(249, 250, 251, 0.82) !important;
    border: 1px solid rgba(255, 255, 255, 0.65);
    transition: box-shadow 0.3s ease, transform 0.3s ease !important;
  }
  html.dark #skills .grid > div {
    background: rgba(31, 41, 55, 0.82) !important;
    border: 1px solid rgba(255, 255, 255, 0.07);
  }
  @supports (backdrop-filter: blur(1px)) {
    #skills .grid > div {
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
    }
  }
  #skills .grid > div:hover {
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.18) !important;
    transform: translateY(-5px) !important;
  }
""",
        "js": "",
        "commit_subject": "design: apply glassmorphism frosted-glass effect to skill cards",
        "commit_body": (
            "Skill cards now have a frosted-glass look via backdrop-filter + semi-transparent bg.\n"
            "Progressive enhancement: browsers without backdrop-filter fall back to solid fill.\n"
            "Hover adds a purple-tinted shadow and 5px upward lift."
        ),
    },

    # -- 6 --------------------------------------------------------------------
    {
        "id": "animated-section-underlines",
        "name": "Animated Underline on Section Headings",
        "description": "Gradient underline draws from center outward when heading enters viewport",
        "css": """\
  /* -- Animated Section Heading Underlines -- */
  .adp-heading {
    position: relative;
    padding-bottom: 14px;
    display: inline-block;
  }
  .adp-heading::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 3px;
    border-radius: 2px;
    background: linear-gradient(90deg, #7c3aed, #a855f7, #6366f1);
    transition: width 0.85s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }
  .adp-heading.adp-visible::after {
    width: 64%;
  }
""",
        "js": """\
  /* Animated section heading underlines */
  (function () {
    var sels = ['#about h2', '#skills h2', '#experience h2', '#projects h2', '#contact h2'];
    var headings = [];
    sels.forEach(function (s) {
      var el = document.querySelector(s);
      if (el) { el.classList.add('adp-heading'); headings.push(el); }
    });
    if (!headings.length) return;
    if (!('IntersectionObserver' in window)) {
      headings.forEach(function (h) { h.classList.add('adp-visible'); });
      return;
    }
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('adp-visible'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.5 });
    headings.forEach(function (h) { obs.observe(h); });
  })();
""",
        "commit_subject": "design: animate gradient underline on section headings via IntersectionObserver",
        "commit_body": (
            "Attaches a CSS pseudo-element underline to each section h2.\n"
            "Line animates from 0 to 64% width when the heading enters the viewport.\n"
            "Uses IntersectionObserver with a no-motion fallback for older browsers."
        ),
    },

    # -- 7 --------------------------------------------------------------------
    {
        "id": "dot-grid-background",
        "name": "Dot Grid Background Texture",
        "description": "Radial-gradient dot grid on About, Skills, and Contact sections",
        "css": """\
  /* -- Dot Grid Background Texture -- */
  #about, #contact {
    background-image: radial-gradient(rgba(124, 58, 237, 0.09) 1.5px, transparent 1.5px);
    background-size: 28px 28px;
  }
  html.dark #about, html.dark #contact {
    background-image: radial-gradient(rgba(168, 85, 247, 0.08) 1.5px, transparent 1.5px);
    background-size: 28px 28px;
  }
  #skills {
    background-image: radial-gradient(rgba(124, 58, 237, 0.07) 1px, transparent 1px);
    background-size: 22px 22px;
  }
  html.dark #skills {
    background-image: radial-gradient(rgba(168, 85, 247, 0.06) 1px, transparent 1px);
    background-size: 22px 22px;
  }
""",
        "js": "",
        "commit_subject": "design: add subtle dot grid texture to section backgrounds",
        "commit_body": (
            "Overlays a radial-gradient dot pattern on About, Skills, and Contact sections.\n"
            "Brand purple at 6–9% opacity — visible on close inspection, not distracting.\n"
            "Dark mode uses slightly elevated opacity to compensate for the dark base."
        ),
    },

    # -- 8 --------------------------------------------------------------------
    {
        "id": "gradient-border-experience",
        "name": "Animated Gradient Border on Experience Cards",
        "description": "The solid purple left accent on experience cards becomes an animated gradient",
        "css": """\
  /* -- Animated Gradient Experience Card Border -- */
  @keyframes adp-borderSlide {
    0%   { background-position: 0%   0%; }
    100% { background-position: 0% 200%; }
  }
  #experience .relative .absolute.w-1 {
    background: linear-gradient(180deg, #7c3aed, #a855f7, #6366f1, #7c3aed) !important;
    background-size: 100% 200% !important;
    animation: adp-borderSlide 3s linear infinite;
    border-radius: 4px;
  }
  #experience .rounded-xl {
    transition: box-shadow 0.3s ease, transform 0.3s ease;
  }
  #experience .rounded-xl:hover {
    box-shadow: 0 20px 55px rgba(124, 58, 237, 0.13);
    transform: translateY(-3px);
  }
""",
        "js": "",
        "commit_subject": "design: animate gradient on experience card accent border",
        "commit_body": (
            "The solid purple left border on experience cards now cycles through a\n"
            "purple→indigo gradient. Adds a subtle lift + shadow on card hover.\n"
            "Targets .absolute.w-1 — only the decorative border element, nothing structural."
        ),
    },

    # -- 9 --------------------------------------------------------------------
    {
        "id": "floating-hero-accent",
        "name": "Gentle Float on Hero Accent Text",
        "description": "The 'Full Stack Developer' span bobs up and down to draw the eye",
        "css": """\
  /* -- Floating Hero Accent -- */
  @keyframes adp-gentleFloat {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-9px); }
  }
  #home h1 > span {
    display: inline-block;
    animation: adp-gentleFloat 4.5s ease-in-out infinite;
    will-change: transform;
  }
  @media (prefers-reduced-motion: reduce) {
    #home h1 > span { animation: none; }
  }
""",
        "js": "",
        "commit_subject": "design: add gentle float animation to hero headline accent",
        "commit_body": (
            "The 'Full Stack Developer' span gently bobs 9px upward and back on a\n"
            "4.5s ease-in-out cycle, drawing the visitor's eye to the key role title.\n"
            "Respects prefers-reduced-motion — static for users who prefer no motion."
        ),
    },

    # -- 10 -------------------------------------------------------------------
    {
        "id": "skill-card-3d-tilt",
        "name": "3D Perspective Tilt on Skill Cards",
        "description": "Skill cards tilt in 3D space following the mouse cursor on hover",
        "css": """\
  /* -- 3D Tilt Skill Cards -- */
  #skills .grid > div {
    transform-style: preserve-3d;
    will-change: transform;
    cursor: default;
  }
  #skills .grid > div.adp-tilt-active {
    box-shadow: 0 14px 42px rgba(124, 58, 237, 0.2) !important;
  }
""",
        "js": """\
  /* 3D tilt on skill cards */
  (function () {
    var cards = document.querySelectorAll('#skills .grid > div');
    cards.forEach(function (card) {
      card.addEventListener('mousemove', function (e) {
        var rect = card.getBoundingClientRect();
        var x = ((e.clientX - rect.left) / rect.width  - 0.5) * 20;
        var y = -((e.clientY - rect.top)  / rect.height - 0.5) * 20;
        card.style.transform = 'perspective(500px) rotateX(' + y + 'deg) rotateY(' + x + 'deg) scale(1.05)';
        card.classList.add('adp-tilt-active');
      });
      card.addEventListener('mouseleave', function () {
        card.style.transform = '';
        card.classList.remove('adp-tilt-active');
      });
    });
  })();
""",
        "commit_subject": "design: add 3D perspective tilt effect to skill cards on hover",
        "commit_body": (
            "Skill cards now track the mouse cursor and rotate up to ±20° in 3D perspective.\n"
            "Uses CSS perspective() + JS mousemove for precise, per-card tracking.\n"
            "Resets cleanly on mouseleave — no permanent style mutation."
        ),
    },

    # -- 11 -------------------------------------------------------------------
    {
        "id": "aurora-hero-background",
        "name": "Animated Aurora Orbs on Hero",
        "description": "Blurred radial gradient orbs slowly drift behind the hero text",
        "css": """\
  /* -- Aurora Orb Background on Hero -- */
  @keyframes adp-auroraMove {
    0%   { transform: translate(0%, 0%)   scale(1);    }
    33%  { transform: translate(3%, -4%)  scale(1.06); }
    66%  { transform: translate(-3%, 3%)  scale(0.97); }
    100% { transform: translate(0%, 0%)   scale(1);    }
  }
  #home { position: relative; overflow: hidden; }
  #home::before, #home::after {
    content: '';
    position: absolute;
    border-radius: 50%;
    filter: blur(90px);
    pointer-events: none;
    animation: adp-auroraMove 12s ease-in-out infinite;
    z-index: 0;
  }
  #home::before {
    width: 560px; height: 560px;
    background: radial-gradient(circle, rgba(124,58,237,0.22) 0%, transparent 70%);
    top: -130px; right: -80px;
  }
  #home::after {
    width: 480px; height: 480px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    bottom: -80px; left: -60px;
    animation-delay: -6s;
  }
  html.dark #home::before { opacity: 1.4; }
  #home > div { position: relative; z-index: 1; }
""",
        "js": "",
        "commit_subject": "design: add animated aurora gradient orbs to hero section",
        "commit_body": (
            "Two blurred radial gradient orbs (purple & indigo) slowly drift behind hero text.\n"
            "Implemented as CSS ::before/::after pseudo-elements — zero DOM nodes added.\n"
            "pointer-events: none ensures no interaction interference with hero buttons."
        ),
    },

    # -- 12 -------------------------------------------------------------------
    {
        "id": "contact-form-focus-glow",
        "name": "Glowing Focus States on Contact Form",
        "description": "Input and textarea get a soft purple glow ring on focus for better UX",
        "css": """\
  /* -- Contact Form Focus Glow -- */
  #contact input, #contact textarea {
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
  }
  #contact input:focus, #contact textarea:focus {
    outline: none;
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.22), 0 0 14px rgba(124,58,237,0.1);
  }
  html.dark #contact input:focus, html.dark #contact textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.28), 0 0 18px rgba(168,85,247,0.12);
  }
  #contact button[type="submit"] {
    transition: box-shadow 0.2s ease, transform 0.2s ease, background-color 0.2s ease;
  }
  #contact button[type="submit"]:hover {
    box-shadow: 0 6px 20px rgba(124,58,237,0.4);
  }
""",
        "js": "",
        "commit_subject": "design: add glowing focus states and hover glow to contact form",
        "commit_body": (
            "Contact form inputs emit a soft purple glow ring on focus.\n"
            "Submit button gains a lifted shadow on hover for clearer affordance.\n"
            "Dark mode uses a wider, brighter ring to maintain visibility on dark backgrounds."
        ),
    },
]

# -----------------------------------------------------------------------------
# State helpers
# -----------------------------------------------------------------------------

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"current_index": 0, "history": []}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_next_patch(state):
    idx = state["current_index"] % len(PATCHES)
    return PATCHES[idx], idx

# -----------------------------------------------------------------------------
# HTML injection
# -----------------------------------------------------------------------------

def inject_patch(html, patch):
    """Replace or create the auto-design-patch <style> and <script> tags."""
    css_block = f'<style id="auto-design-patch">\n{patch["css"]}\n</style>'
    js_block  = (
        f'<script id="auto-design-script">\n{patch["js"]}\n</script>'
        if patch["js"] else
        '<script id="auto-design-script"></script>'
    )

    if CSS_TAG_RE.search(html):
        html = CSS_TAG_RE.sub(css_block, html)
    else:
        html = html.replace('</head>', f'  {css_block}\n  </head>', 1)

    if JS_TAG_RE.search(html):
        html = JS_TAG_RE.sub(js_block, html)
    else:
        html = html.replace('</body>', f'  {js_block}\n  </body>', 1)

    return html

# -----------------------------------------------------------------------------
# Git helpers
# -----------------------------------------------------------------------------

def run_git(args):
    r = subprocess.run(["git"] + args, cwd=SCRIPT_DIR,
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def cmd_list():
    state = load_state()
    applied_ids = [h["patch_id"] for h in state.get("history", [])]
    current = state["current_index"] % len(PATCHES)
    print(f"\n  Portfolio Design Patches  ({len(PATCHES)} total)\n")
    for i, p in enumerate(PATCHES):
        marker = ">" if i == current else ("*" if p["id"] in applied_ids else " ")
        print(f"  {marker} [{i+1:2d}] {p['id']}")
        print(f"         {p['name']}")
        print(f"         {p['description']}\n")


def cmd_reset():
    state = load_state()
    state["current_index"] = 0
    save_state(state)
    print("  State reset — next run will apply patch [1].")


def cmd_apply(dry_run=False):
    if not HTML_FILE.exists():
        print(f"  ERROR: {HTML_FILE} not found.")
        sys.exit(1)

    state = load_state()
    patch, idx = get_next_patch(state)

    print(f"\n{'=' * 62}")
    print(f"  Patch {idx + 1}/{len(PATCHES)}: {patch['name']}")
    print(f"  {patch['description']}")
    print(f"{'=' * 62}\n")

    html     = HTML_FILE.read_text(encoding="utf-8")
    new_html = inject_patch(html, patch)

    if dry_run:
        print("  [dry-run] Would write index.html with:\n")
        print("  CSS ------------------------------------------")
        print(patch["css"])
        if patch["js"]:
            print("  JS -------------------------------------------")
            print(patch["js"])
        print(f"\n  Commit: {patch['commit_subject']}")
        return

    HTML_FILE.write_text(new_html, encoding="utf-8")
    print(f"  [ok] index.html updated  ({patch['id']})")

    # git add
    rc, _, err = run_git(["add", "index.html"])
    if rc != 0:
        print(f"  ✗ git add failed: {err}")
        sys.exit(1)
    print("  [ok] git add index.html")

    # git commit
    commit_msg = f"{patch['commit_subject']}\n\n{patch['commit_body']}"
    rc, out, err = run_git(["commit", "-m", commit_msg])
    if rc != 0:
        print(f"  ✗ git commit failed: {err}")
        sys.exit(1)
    print(f"  [ok] git commit")

    # git push
    rc, _, err = run_git(["push"])
    if rc != 0:
        print(f"  ✗ git push failed: {err}")
        sys.exit(1)
    print(f"  [ok] git push")

    # Update state
    state["current_index"] = (idx + 1) % len(PATCHES)
    state["history"].append({
        "patch_id": patch["id"],
        "patch_name": patch["name"],
        "applied_at": datetime.now().isoformat(),
        "commit": patch["commit_subject"],
    })
    save_state(state)

    next_patch = PATCHES[state["current_index"]]
    print(f"\n  Done!  Next patch → {next_patch['name']}\n")


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--list" in args:
        cmd_list()
        return

    if "--reset" in args:
        cmd_reset()
        return

    cmd_apply(dry_run="--dry-run" in args)


if __name__ == "__main__":
    main()
