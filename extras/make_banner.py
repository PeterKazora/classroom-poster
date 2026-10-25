"""Physics header image for a Google Classroom class (Customize -> Upload photo).
2000 x 500 px (4:1). Deep-space background with soft glows and stars; seven translucent topic panels
(A Level physics formulas + one glowing diagram each), textbook (STIX) maths. Left panels are a touch
brighter because Classroom fades the left of the header into the theme colour.

Needs numpy and matplotlib. Edit PANELS to change the topics and formulas.
Run: python make_banner.py   -> class-header.png in the current folder."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, FancyArrowPatch

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
W, Y0, Y1 = 20, -0.3, 5.1
fig = plt.figure(figsize=(20, 5), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(Y0, Y1); ax.axis('off')

# ---------- background: deep navy, soft coloured glows, faint stars ----------
nx, ny = 800, 200
X, Y = np.meshgrid(np.linspace(0, W, nx), np.linspace(Y0, Y1, ny))
img = np.zeros((ny, nx, 3))
img[..., 0], img[..., 1], img[..., 2] = 0.04, 0.07, 0.20
img[..., 2] += 0.08 * (X / W)
for gx, gy, r, col, a in [(15.5, 4.6, 4.0, (0.15, 0.55, 0.75), 0.35), (4.5, 0.2, 4.5, (0.45, 0.25, 0.75), 0.30),
                          (10.5, 2.4, 3.5, (0.10, 0.35, 0.65), 0.25), (19.5, 0.5, 3.0, (0.55, 0.35, 0.70), 0.25)]:
    k = a * np.exp(-((X - gx) ** 2 + ((Y - gy) * 1.6) ** 2) / (2 * r ** 2))
    for c in range(3):
        img[..., c] += k * col[c]
ax.imshow(np.clip(img, 0, 1), extent=[0, W, Y0, Y1], origin='lower', aspect='auto', zorder=0)
rng = np.random.default_rng(7)
sx, sy = rng.uniform(0, W, 260), rng.uniform(Y0, Y1, 260)
ax.scatter(sx, sy, s=rng.uniform(0.5, 4, 260), c='white', alpha=0.35, linewidths=0, zorder=1)

GLOW = lambda col, w=5: [pe.withStroke(linewidth=w, foreground=col, alpha=0.18)]


def glow_line(xs, ys, col, lw=2.2, a=0.95):
    ax.plot(xs, ys, color=col, lw=lw * 4, alpha=0.10, zorder=3, solid_capstyle='round')
    ax.plot(xs, ys, color=col, lw=lw, alpha=a, zorder=4, solid_capstyle='round')


def arrow(x1, y1, x2, y2, col, lw=1.4, a=0.9):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=9, color=col, lw=lw, alpha=a, zorder=4))


def ring(x, y, w, h, col, ang=0, lw=1.8):
    ax.add_patch(Ellipse((x, y), w, h, angle=ang, fill=False, ec=col, lw=lw * 4, alpha=0.10, zorder=3))
    ax.add_patch(Ellipse((x, y), w, h, angle=ang, fill=False, ec=col, lw=lw, alpha=0.9, zorder=4))


def ball(x, y, r, col):
    ax.add_patch(Circle((x, y), r * 2.2, color=col, alpha=0.10, zorder=3))
    ax.add_patch(Circle((x, y), r * 1.5, color=col, alpha=0.18, zorder=3))
    ax.add_patch(Circle((x, y), r, color=col, zorder=5))


# ---------- panels ----------
PANELS = [
    ('GRAVITATION', '#ffd166', [r'$F=\frac{GMm}{r^{2}}$', r'$\phi=-\frac{GM}{r}$', r'$g=\frac{GM}{r^{2}}$', r'$a=r\omega^{2}=\frac{v^{2}}{r}$']),
    ('THERMAL PHYSICS', '#ff9f7a', [r'$pV=nRT$', r'$pV=\frac{1}{3}Nm\langle c^{2}\rangle$', r'$\langle E_K\rangle=\frac{3}{2}kT$', r'$\Delta U=q+W$']),
    ('OSCILLATIONS', '#6ff0c8', [r'$a=-\omega^{2}x$', r'$x=x_0\sin\omega t$', r'$v=\pm\omega\sqrt{x_0^{2}-x^{2}}$', r'$E=\frac{1}{2}m\omega^{2}x_0^{2}$']),
    ('ELECTRIC FIELDS', '#7cc4ff', [r'$F=\frac{Qq}{4\pi\varepsilon_0 r^{2}}$', r'$E=\frac{V}{d}$    $C=\frac{Q}{V}$', r'$W=\frac{1}{2}CV^{2}$', r'$x=x_0e^{-t/RC}$']),
    ('MAGNETISM', '#ff8fd0', [r'$F=BIL\sin\theta$', r'$F=BQv$    $\Phi=BA$', r'$\varepsilon=-\frac{d(N\Phi)}{dt}$', r'$V_H=\frac{BI}{ntq}$']),
    ('QUANTUM & NUCLEAR', '#c3a6ff', [r'$E=hf=\frac{hc}{\lambda}$', r'$hf=\Phi+\frac{1}{2}mv^{2}_{max}$', r'$\lambda=\frac{h}{p}$    $E=mc^{2}$', r'$A=\lambda N$']),
    ('MEDICAL & ASTRO', '#ffe08a', [r'$I=I_0e^{-\mu x}$', r'$Z=\rho c$    $v=H_0d$', r'$L=4\pi\sigma r^{2}T^{4}$', r'$\frac{\Delta\lambda}{\lambda}=\frac{v}{c}$']),
]
PW, GAP, X0 = 2.70, 0.12, 0.10
for i, (name, col, eqs) in enumerate(PANELS):
    x0 = X0 + i * (PW + GAP)
    left = i < 3                                   # through Classroom's fade: brighter
    ax.add_patch(FancyBboxPatch((x0, -0.12), PW, 5.06, boxstyle='round,pad=0,rounding_size=0.18',
                                fc=col, ec=col, lw=1.2, alpha=0.07 if not left else 0.10, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, -0.12), PW, 5.06, boxstyle='round,pad=0,rounding_size=0.18',
                                fc='none', ec=col, lw=1.3, alpha=0.45, zorder=2))
    ax.text(x0 + 0.18, 4.6, name, color=col, fontsize=13, fontweight='bold', alpha=0.95, zorder=5,
            family='DejaVu Sans', path_effects=GLOW(col, 4))
    ax.plot([x0 + 0.18, x0 + PW - 0.18], [4.45, 4.45], color=col, lw=1, alpha=0.5, zorder=4)
    for j, s in enumerate(eqs):
        ax.text(x0 + 0.2, 3.85 - j * 0.72, s, color='white', fontsize=23 if left else 22, alpha=0.97 if left else 0.92,
                zorder=5, path_effects=GLOW(col, 6))

# ---------- one glowing diagram per panel (bottom of each panel) ----------
def px(i):
    return X0 + i * (PW + GAP)

# gravitation: planet + orbit + satellite with velocity
cx, cy = px(0) + 1.37, 0.55
ball(cx, cy, 0.17, '#ffb347')
ring(cx, cy, 1.9, 0.62, '#9fd3ff', -8)
ball(cx + 0.92, cy - 0.12, 0.06, '#ffffff')
arrow(cx + 0.92, cy - 0.12, cx + 0.98, cy + 0.32, '#ffffff')
# thermal: p-V cycle with arrows
p0x, p0y = px(1) + 0.55, 0.05
glow_line([p0x, p0x, p0x + 1.6, p0x], [p0y, p0y + 0.95, p0y, p0y], '#ff9f7a', 2)
arrow(p0x, p0y + 0.3, p0x, p0y + 0.65, '#ff9f7a'); arrow(p0x + 1.1, p0y, p0x + 0.6, p0y, '#ff9f7a')
ax.text(p0x - 0.28, p0y + 0.85, 'p', color='white', alpha=0.7, fontsize=15, zorder=5)
ax.text(p0x + 1.7, p0y - 0.1, 'V', color='white', alpha=0.7, fontsize=15, zorder=5)
# oscillations: damped wave
xs = np.linspace(px(2) + 0.2, px(2) + PW - 0.2, 300)
glow_line(xs, 0.5 + 0.42 * np.exp(-(xs - xs[0]) / 1.2) * np.sin(7.5 * (xs - xs[0])), '#6ff0c8', 2.4)
glow_line(xs, 0.5 + 0.42 * np.exp(-(xs - xs[0]) / 1.2), '#6ff0c8', 0.8, 0.35)
# electric: + and - charges with field lines
pq, nq = np.array([px(3) + 0.55, 0.5]), np.array([px(3) + 2.2, 0.5])
mid = (pq[0] + nq[0]) / 2; half = (nq[0] - pq[0]) / 2
for k in (0.22, 0.42):
    th = np.linspace(0, np.pi, 100)
    for sgn in (1, -1):
        glow_line(mid + half * np.cos(np.pi - th), 0.5 + sgn * k * np.sin(th), '#7cc4ff', 1.2, 0.7)
glow_line([pq[0], nq[0]], [0.5, 0.5], '#7cc4ff', 1.2, 0.7)
ball(*pq, 0.15, '#ff6b6b'); ball(*nq, 0.15, '#4fa3ff')
ax.text(*pq, '+', color='white', ha='center', va='center', fontsize=15, fontweight='bold', zorder=6)
ax.text(*nq, '−', color='white', ha='center', va='center', fontsize=17, fontweight='bold', zorder=6)
# magnetism: field round a current-carrying wire
mx, my = px(4) + 1.37, 0.5
for r in (0.18, 0.36, 0.54):
    ring(mx, my, 2 * r * 1.6, 2 * r, '#ff8fd0', 0, 1.4)
ball(mx, my, 0.06, '#ffffff')
# quantum & nuclear: energy levels + photon
ex = px(5) + 0.35
for yy in (0.05, 0.45, 0.72, 0.9):
    glow_line([ex, ex + 1.15], [yy, yy], '#c3a6ff', 1.3, 0.85)
arrow(ex + 0.4, 0.9, ex + 0.4, 0.08, '#ffffff', 1.5)
xw = np.linspace(ex + 1.25, ex + 2.2, 200)
glow_line(xw, 0.5 + 0.12 * np.sin(30 * (xw - xw[0])), '#c3a6ff', 1.6)
arrow(xw[-1] - 0.05, 0.5, xw[-1] + 0.12, 0.5, '#c3a6ff')
# medical & astro: glowing star + red-shift spectrum strip
stx, sty = px(6) + 0.6, 0.5
ball(stx, sty, 0.2, '#fff1b8')
for k in range(12):
    a = 2 * np.pi * k / 12
    ax.plot([stx + 0.28 * np.cos(a), stx + 0.42 * np.cos(a)], [sty + 0.28 * np.sin(a), sty + 0.42 * np.sin(a)],
            color='#fff1b8', lw=1.4, alpha=0.8, zorder=4)
sp = px(6) + 1.2
grad = np.linspace(0, 1, 100)[None, :]
ax.imshow(plt.cm.turbo(grad)[..., :3], extent=[sp, sp + 1.35, 0.3, 0.7], aspect='auto', alpha=0.85, zorder=4)
for lx in (0.25, 0.55, 0.9):
    ax.plot([sp + lx, sp + lx], [0.3, 0.7], color='black', lw=2, zorder=5)
    ax.plot([sp + lx + 0.18, sp + lx + 0.18], [0.3, 0.7], color='white', lw=1, alpha=0.6, zorder=5)

fig.savefig('class-header.png', dpi=100)
print('saved')
