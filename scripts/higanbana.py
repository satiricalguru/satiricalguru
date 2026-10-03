"""Generates the animated higanbana SVGs used in README.md.

Each spider lily is built procedurally (umbel of florets, recurved tepals,
upswept stamens) and coloured with CSS keyframes so it blooms white and
bleeds red on GitHub, no JavaScript needed.  Run: python3 scripts/higanbana.py
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

WHITE = "#efe8e0"
RED = "#d0142c"
STEM = "#1e281c"
BG = "#060505"


def f(v):
    return f"{v:.1f}"


def lily(cx, cy, size, rng):
    """Return (tepal_d, stamen_d, anther_d) path data for one flower head."""
    tep, sta, ant = [], [], []
    n = rng.randint(6, 8)
    for i in range(n):
        base = -math.pi - 0.38 + (math.pi + 0.76) * (i + 0.5) / n + rng.uniform(-0.15, 0.15)
        reach = rng.uniform(0.6, 1.0)
        ox, oy = cx + math.cos(base) * size * 0.035, cy + math.sin(base) * size * 0.035 - size * 0.02
        for j in range(6):
            a = base + (j - 2.5) * rng.uniform(0.15, 0.23)
            c, s = math.cos(a), math.sin(a)
            L = size * 0.26 * rng.uniform(0.8, 1.08) * reach
            nx, ny = -s, c
            curl = rng.uniform(0.65, 1.1) * (1 if j % 2 else -1)
            kx, ky = ox + c * L * 0.85, oy + s * L * 0.85
            tx = ox + c * L * 0.62 + nx * L * 0.42 * curl
            ty = oy + s * L * 0.62 + ny * L * 0.42 * curl - L * 0.12
            w = size * rng.uniform(0.032, 0.046)
            tep.append(
                f"M{f(ox)} {f(oy)}Q{f(kx + nx * w)} {f(ky + ny * w)} {f(tx)} {f(ty)}"
                f"Q{f(kx - nx * w * 0.4)} {f(ky - ny * w * 0.4)} {f(ox)} {f(oy)}Z"
            )
        for j in range(7):
            a = base + (j - 3) * rng.uniform(0.06, 0.1)
            c, s = math.cos(a), math.sin(a)
            L = size * 0.6 * rng.uniform(0.82, 1.1) * (0.55 + 0.45 * reach)
            up = L * 0.5 * rng.uniform(0.55, 1.0)
            ex, ey = ox + c * L * 0.82, oy + s * L * 0.72 - up
            sta.append(
                f"M{f(ox)} {f(oy)}C{f(ox + c * L * 0.42)} {f(oy + s * L * 0.42)} "
                f"{f(ox + c * L * 0.8)} {f(oy + s * L * 0.75 - up * 0.35)} {f(ex)} {f(ey)}"
            )
            r = max(0.8, size * 0.009)
            ant.append(f"M{f(ex - r)} {f(ey)}a{f(r)} {f(r)} 0 1 0 {f(2 * r)} 0a{f(r)} {f(r)} 0 1 0 {f(-2 * r)} 0")
    return "".join(tep), "".join(sta), "".join(ant)


def flower_group(x, head_y, ground, size, rng, cls, delay, depth_op):
    tep, sta, ant = lily(x, head_y, size, rng)
    bend = rng.uniform(-0.14, 0.14) * size * 2
    stem = f"M{f(x)} {f(ground)}Q{f(x + bend)} {f((ground + head_y) / 2)} {f(x)} {f(head_y)}"
    sw = max(1.0, size * 0.02)
    ss = max(0.5, size * 0.0055)
    sway = rng.uniform(4, 7)
    return (
        f'<g class="fl {cls}" style="--d:{delay:.2f}s;--s:{sway:.1f}s;opacity:{depth_op}" '
        f'transform-origin="{f(x)} {f(ground)}">'
        f'<path class="stem" d="{stem}" stroke-width="{f(sw)}"/>'
        f'<g class="head" style="transform-origin:{f(x)}px {f(head_y)}px">'
        f'<path class="tep" d="{tep}"/>'
        f'<path class="sta" d="{sta}" stroke-width="{f(ss)}"/>'
        f'<path class="ant" d="{ant}"/>'
        f"</g></g>"
    )


def petals(rng, w, h, count, cls="pt"):
    out = []
    for _ in range(count):
        x = rng.uniform(0, w)
        s = rng.uniform(4, 8)
        dur = rng.uniform(7, 12)
        delay = rng.uniform(0, 10)
        drift = rng.uniform(-60, 60)
        out.append(
            f'<path class="{cls}" style="--x:{drift:.0f}px;--h:{h + 40}px;animation-duration:{dur:.1f}s;'
            f'animation-delay:-{delay:.1f}s" d="M{f(x)} -20q{f(s / 2)} {f(-s * 0.22)} {f(s)} 0q{f(-s / 2)} {f(s * 0.22)} {f(-s)} 0z"/>'
        )
    return "".join(out)


BASE_CSS = f"""
.stem{{fill:none;stroke:{STEM};stroke-linecap:round;animation:stem var(--cycle) var(--d) infinite both}}
.tep,.ant{{fill:{WHITE};animation:fillc var(--cycle) var(--d) infinite both}}
.sta{{fill:none;stroke:{WHITE};stroke-linecap:round;animation:strokec var(--cycle) var(--d) infinite both}}
.head{{animation:bloom 2.2s cubic-bezier(.19,1,.22,1) calc(var(--d) * .25) both, sway var(--s) ease-in-out infinite alternate}}
.pt{{fill:{RED};opacity:.75;animation:fall linear infinite}}
@keyframes bloom{{from{{transform:scale(0) rotate(-25deg);opacity:0}}to{{transform:none;opacity:1}}}}
@keyframes sway{{from{{transform:rotate(-2.5deg)}}to{{transform:rotate(2.5deg)}}}}
@keyframes fall{{from{{transform:translate(0,0) rotate(0)}}to{{transform:translate(var(--x),var(--h)) rotate(540deg)}}}}
"""


def color_keys(white_until, red_from, red_until):
    """Keyframes: white → red → white within one cycle (percentages)."""
    return f"""
@keyframes fillc{{0%,{white_until}%{{fill:{WHITE}}}{red_from}%,{red_until}%{{fill:{RED}}}100%{{fill:{WHITE}}}}}
@keyframes strokec{{0%,{white_until}%{{stroke:{WHITE}}}{red_from}%,{red_until}%{{stroke:#ff2a46}}100%{{stroke:{WHITE}}}}}
@keyframes stem{{0%,{white_until}%{{stroke:{STEM}}}{red_from}%,{red_until}%{{stroke:#4a0a12}}100%{{stroke:{STEM}}}}}
"""


def field_svg():
    """Bottom banner: a field of white lilies that turns red in a wave, then resets."""
    rng = random.Random(7)
    W, H = 1200, 320
    groups = []
    flowers = []
    for _ in range(46):
        depth = rng.choices([0, 1, 2], [0.45, 0.35, 0.2])[0]
        x = rng.uniform(-30, W + 30)
        size = {0: rng.uniform(40, 62), 1: rng.uniform(70, 100), 2: rng.uniform(110, 150)}[depth]
        head = H * {0: rng.uniform(0.42, 0.62), 1: rng.uniform(0.5, 0.75), 2: rng.uniform(0.68, 0.92)}[depth]
        flowers.append((depth, head, x, size))
    flowers.sort()
    for depth, head, x, size in flowers:
        # The red wave sweeps left → right; delay is negative-offset inside the cycle.
        delay = (x / W) * 2.6 + rng.uniform(0, 0.5)
        op = {0: 0.4, 1: 0.72, 2: 1}[depth]
        groups.append(flower_group(x, head, H + 10, size, rng, f"d{depth}", delay, op))
    css = BASE_CSS + color_keys(28, 46, 80)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A field of white spider lilies slowly turning red">
<title>Higanbana — white flowers turning red</title>
<style>:root{{--cycle:12s}}svg{{--cycle:12s}}{css}
.glow{{animation:glow var(--cycle) 1.2s infinite both}}
@keyframes glow{{0%,30%{{opacity:0}}55%,80%{{opacity:.9}}100%{{opacity:0}}}}
</style>
<defs>
<radialGradient id="g" cx="50%" cy="100%" r="70%"><stop offset="0" stop-color="#c41226" stop-opacity=".45"/><stop offset="1" stop-color="#c41226" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".35" stop-color="{BG}" stop-opacity="0"/><stop offset=".9" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect class="glow" width="{W}" height="{H}" fill="url(#g)"/>
<g style="--cycle:12s">{''.join(groups)}</g>
{petals(rng, W, H, 26)}
<rect width="{W}" height="{H}" fill="url(#fade)" pointer-events="none"/>
<text x="{W - 24}" y="{H - 18}" text-anchor="end" font-family="ui-monospace,Menlo,monospace" font-size="11" letter-spacing="3" fill="#7d756e">1000 − 7 = 993 · 彼岸花</text>
</svg>"""


def header_svg():
    """Top banner: name on the left, a cluster blooming and bleeding red on the right."""
    rng = random.Random(23)
    W, H = 1200, 400
    groups = []
    flowers = []
    for _ in range(30):
        depth = rng.choices([0, 1, 2], [0.4, 0.38, 0.22])[0]
        x = rng.uniform(560, W + 40)
        size = {0: rng.uniform(42, 64), 1: rng.uniform(72, 104), 2: rng.uniform(112, 158)}[depth]
        head = H * {0: rng.uniform(0.25, 0.55), 1: rng.uniform(0.35, 0.7), 2: rng.uniform(0.55, 0.9)}[depth]
        flowers.append((depth, head, x, size))
    flowers.sort()
    for depth, head, x, size in flowers:
        delay = ((W - x) / 640) * 1.8 + rng.uniform(0, 0.6)
        op = {0: 0.38, 1: 0.7, 2: 1}[depth]
        groups.append(flower_group(x, head, H + 10, size, rng, f"d{depth}", delay, op))
    css = BASE_CSS + color_keys(22, 40, 84)
    serif = "'Shippori Mincho','Hiragino Mincho ProN','Yu Mincho',Georgia,'Times New Roman',serif"
    mono = "ui-monospace,SFMono-Regular,Menlo,monospace"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Jatin Pandey — spider lilies blooming white and turning red">
<title>Jatin Pandey — Higanbana</title>
<style>svg{{--cycle:14s}}{css}
.rise{{animation:rise 1.6s cubic-bezier(.19,1,.22,1) both}}
.r1{{animation-delay:.1s}}.r2{{animation-delay:.35s}}.r3{{animation-delay:.7s}}.r4{{animation-delay:.95s}}
@keyframes rise{{from{{transform:translateY(40px);opacity:0}}to{{transform:none;opacity:1}}}}
.dot{{animation:pulse 2.4s ease-out infinite}}
@keyframes pulse{{0%{{r:4;opacity:1}}70%{{r:12;opacity:0}}100%{{r:4;opacity:0}}}}
.outline{{fill:none;stroke:#ede7df;stroke-opacity:.75;stroke-width:1.2;stroke-dasharray:1400;stroke-dashoffset:1400;animation:draw 3.2s .6s ease forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.kv{{animation:kv 14s infinite both}}
@keyframes kv{{0%,22%{{fill:#b9b1a8}}40%,84%{{fill:#e01b34}}100%{{fill:#b9b1a8}}}}
</style>
<defs><linearGradient id="veil" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".42" stop-color="{BG}" stop-opacity=".85"/><stop offset=".62" stop-color="{BG}" stop-opacity="0"/></linearGradient>
<linearGradient id="bot" x1="0" y1="0" x2="0" y2="1"><stop offset=".7" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<g>{''.join(groups)}</g>
{petals(rng, W, H, 18)}
<rect width="{W}" height="{H}" fill="url(#veil)"/>
<rect width="{W}" height="{H}" fill="url(#bot)"/>
<g font-family="{mono}" font-size="12" letter-spacing="3" fill="#b9b1a8">
  <g class="rise r1"><circle class="dot" cx="54" cy="74" r="4" fill="#e01b34"/><circle cx="54" cy="74" r="3.5" fill="#e01b34"/>
  <text x="70" y="78">APP &amp; WEB DEVELOPER — INDIA</text></g>
</g>
<g font-family="{serif}" font-weight="500" letter-spacing="-4">
  <text class="rise r2" x="44" y="198" font-size="124" fill="#ede7df">Jatin</text>
  <text class="outline" x="118" y="302" font-size="124">Pandey</text>
</g>
<g class="rise r4" font-family="{mono}" font-size="12" letter-spacing="2.5" fill="#7d756e">
  <text x="48" y="352">BUILDING THINGS, <tspan fill="#e01b34">BREAKING</tspan> THINGS, AND OCCASIONALLY FIXING THEM.</text>
</g>
<text class="kv" x="{W - 30}" y="70" font-family="{serif}" font-size="16" letter-spacing="10" writing-mode="tb" glyph-orientation-vertical="0">彼岸花・咲いて赤く染まる</text>
</svg>"""


def countdown_svg():
    """The '1000 − 7' gag: counts down by sevens, forever."""
    W, H = 1200, 150
    vals = [1000 - 7 * i for i in range(0, 143, 6)] + [6]
    n = len(vals)
    step = 100 / n
    frames = []
    for i, v in enumerate(vals):
        a, b = i * step, (i + 1) * step
        frames.append(
            f'<text class="n" style="animation-name:k{i}" x="{W / 2}" y="104" text-anchor="middle">{v}</text>'
            f"<style>@keyframes k{i}{{0%,{a:.2f}%{{opacity:0}}{a + 0.01:.2f}%,{b:.2f}%{{opacity:1}}{b + 0.01:.2f}%,100%{{opacity:0}}}}</style>"
        )
    serif = "'Shippori Mincho',Georgia,'Times New Roman',serif"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="1000 minus 7, counting down">
<title>1000 − 7</title>
<style>.n{{font-family:{serif};font-size:84px;font-weight:500;letter-spacing:-3px;fill:#ede7df;opacity:0;animation-duration:6s;animation-iteration-count:infinite;animation-timing-function:step-end}}
.bar{{animation:bar 6s linear infinite;transform-origin:0 0}}@keyframes bar{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
<text x="{W / 2}" y="30" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" letter-spacing="6" fill="#e01b34">1000 − 7</text>
{''.join(frames)}
<text x="40" y="{H - 16}" font-family="ui-monospace,Menlo,monospace" font-size="10" letter-spacing="3" fill="#4f4945">STILL COUNTING</text>
<text x="{W - 40}" y="{H - 16}" text-anchor="end" font-family="ui-monospace,Menlo,monospace" font-size="10" letter-spacing="3" fill="#4f4945">彼岸花</text>
<rect class="bar" x="0" y="{H - 2}" width="{W}" height="2" fill="#c41226"/>
</svg>"""


def divider_svg():
    """A thin animated red line with a lily mark, used between sections."""
    W, H = 1200, 40
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="divider">
<style>.l{{stroke:#c41226;stroke-width:1;stroke-dasharray:560;stroke-dashoffset:560;animation:d 2.4s ease forwards}}
.m{{animation:spin 8s linear infinite;transform-origin:600px 20px}}@keyframes d{{to{{stroke-dashoffset:0}}}}@keyframes spin{{to{{transform:rotate(360deg)}}}}</style>
<line class="l" x1="580" y1="20" x2="20" y2="20"/><line class="l" x1="620" y1="20" x2="1180" y2="20"/>
<g class="m" fill="none" stroke="#e01b34" stroke-width="1.4" stroke-linecap="round" transform="translate(584 4)">
<path d="M16 19C13.5 13.5 9 10.5 3.5 10M16 19C18.5 13.5 23 10.5 28.5 10M16 19C15 12.5 12.5 7 9 3.5M16 19C17 12.5 19.5 7 23 3.5M16 19V2.5M16 19C11.5 19.5 7.5 18 6 14.5M16 19C20.5 19.5 24.5 18 26 14.5"/></g>
</svg>"""


for name, svg in {
    "higanbana-header.svg": header_svg(),
    "higanbana-field.svg": field_svg(),
    "countdown.svg": countdown_svg(),
    "divider.svg": divider_svg(),
}.items():
    (OUT / name).write_text(svg, encoding="utf-8")
    print(f"{name}: {len(svg) / 1024:.0f} KB")
