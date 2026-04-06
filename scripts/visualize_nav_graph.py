#!/usr/bin/env python3
"""Nav graph 시각화 — 맵 위에 vertex + lane 오버레이."""

import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from PIL import Image
import os

# 한글 폰트
_font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
if os.path.exists(_font_path):
    plt.rcParams['font.family'] = fm.FontProperties(fname=_font_path).get_name()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAP_PGM    = os.path.join(BASE, 'src/pinky_pro/pinky_navigation/map/shop.pgm')
MAP_YAML   = os.path.join(BASE, 'src/pinky_pro/pinky_navigation/map/shop.yaml')
GRAPH_YAML = os.path.join(BASE, 'src/control_center/shoppinkki_rmf/maps/shop_nav_graph.yaml')

# ── 맵 로드 ───────────────────────────────────────────────────────────────────
with open(MAP_YAML) as f:
    map_meta = yaml.safe_load(f)

resolution = map_meta['resolution']
origin     = map_meta['origin']

img  = np.array(Image.open(MAP_PGM))
h, w = img.shape

def world_to_px(x, y):
    px = (x - origin[0]) / resolution
    py = h - (y - origin[1]) / resolution
    return px, py

# ── nav graph 로드 ────────────────────────────────────────────────────────────
with open(GRAPH_YAML) as f:
    graph = yaml.safe_load(f)

vertices = graph['levels']['L1']['vertices']
lanes    = graph['levels']['L1']['lanes']

# 양방향 판별: (a→b) 와 (b→a) 가 둘 다 있으면 양방향
lane_set = {(l[0], l[1]) for l in lanes}
drawn_bidir = set()   # 이미 양방향으로 그린 쌍

# ── 그리기 ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 22))
ax.imshow(img, cmap='gray', origin='upper')
ax.set_title('ShopPinkki Nav Graph', fontsize=18, pad=12)
ax.axis('off')

for lane in lanes:
    fi, ti = lane[0], lane[1]
    x0, y0 = world_to_px(vertices[fi][0], vertices[fi][1])
    x1, y1 = world_to_px(vertices[ti][0], vertices[ti][1])

    is_bidir = (ti, fi) in lane_set
    pair     = tuple(sorted([fi, ti]))

    if is_bidir:
        if pair in drawn_bidir:
            continue
        drawn_bidir.add(pair)
        # 양방향: 양쪽 화살표, 초록
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='<->', color='limegreen',
                                   lw=2.0, mutation_scale=18))
    else:
        # 단방향: 한쪽 화살표, 하늘색
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color='deepskyblue',
                                   lw=2.0, mutation_scale=18))

# Vertex
for i, v in enumerate(vertices):
    vx, vy = world_to_px(v[0], v[1])
    params = v[2] if len(v) > 2 else {}
    name   = params.get('name', str(i))

    if params.get('is_charger'):
        color, marker, ms = 'lime', '*', 22
    elif params.get('is_holding_point'):
        color, marker, ms = 'orange', 's', 14
    elif params.get('pickup_zone'):
        color, marker, ms = 'yellow', 'o', 12
    else:
        color, marker, ms = 'white', 'o', 10

    ax.plot(vx, vy, marker=marker, color=color, markersize=ms,
            markeredgecolor='black', markeredgewidth=1.0, zorder=5)
    ax.text(vx + 5, vy - 5, f'{i}: {name}', fontsize=11, color='white',
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.65))

# 범례
legend = [
    mpatches.Patch(color='lime',        label='충전소 (charger)'),
    mpatches.Patch(color='orange',      label='결제구역 (holding point)'),
    mpatches.Patch(color='yellow',      label='픽업존 (pickup zone)'),
    mpatches.Patch(color='white',       label='일반 waypoint'),
    mpatches.Patch(color='limegreen',   label='양방향 lane ↔'),
    mpatches.Patch(color='deepskyblue', label='단방향 lane →'),
]
ax.legend(handles=legend, loc='lower right', fontsize=12,
          facecolor='black', labelcolor='white', framealpha=0.85)

plt.tight_layout()
out = os.path.join(BASE, 'docs/nav_graph_viz.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f'저장: {out}')
plt.show()
