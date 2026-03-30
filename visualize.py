"""
Visual outputs for painting source material.
Run after analyze.py, or standalone.

Generates:
  1. Heatmap — which institutional languages overlap
  2. Network graph — domains connected by shared phrases
  3. Overlap diagram — Venn-style intersections
  4. Radial chart — each domain's "fingerprint" of control language

All saved as PNGs you can project, print, or paint from.
"""

import json
import numpy as np
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import LinearSegmentedColormap
except ImportError:
    print("Install matplotlib first: pip install matplotlib")
    print("Then run this script again.")
    raise SystemExit(1)

# Run analyze.py first to generate this, or we'll generate it now
data_path = Path("painting_data.json")
if not data_path.exists():
    print("Running analysis first...")
    import analyze
    profiles, shared = analyze.generate_report(analyze.corpora, analyze.personhood_lexicon)
    analyze.export_for_painting(profiles, shared)

with open(data_path) as f:
    data = json.load(f)

# Color palette — institutional cold vs lived hot
COLD = "#2b2d42"       # dark institutional blue-grey
GRID = "#8d99ae"       # bureaucratic grey
HOT_COLORS = ["#ef233c", "#ff6700", "#ff006e", "#3a86ff"]  # the ungovernable
BG = "#edf2f4"         # paper white

domains = list(data["heatmap"].keys())
categories = list(data["heatmap"][domains[0]].keys())


# ---------------------------------------------------------------------------
# 1. HEATMAP — institutional language intensity across domains
# ---------------------------------------------------------------------------

def make_heatmap():
    fig, ax = plt.subplots(figsize=(12, 8))

    matrix = np.array([
        [data["heatmap"][d][c] for d in domains]
        for c in categories
    ], dtype=float)

    # Custom colormap: institutional grey -> hot magenta
    cmap = LinearSegmentedColormap.from_list("personhood", [BG, GRID, "#ff006e"])

    im = ax.imshow(matrix, cmap=cmap, aspect="auto")

    ax.set_xticks(range(len(domains)))
    ax.set_xticklabels([d.replace("_", "\n") for d in domains],
                        fontsize=11, fontweight="bold")
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels([c.replace("_", " ") for c in categories], fontsize=10)

    # Add values in cells
    for i in range(len(categories)):
        for j in range(len(domains)):
            val = int(matrix[i, j])
            color = "white" if val > matrix.max() * 0.6 else COLD
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=14, fontweight="bold", color=color)

    ax.set_title("How Institutions Talk About Defining Personhood",
                  fontsize=14, fontweight="bold", pad=20, color=COLD)

    plt.colorbar(im, ax=ax, label="frequency", shrink=0.8)
    plt.tight_layout()
    plt.savefig("heatmap.png", dpi=200, facecolor=BG)
    print("Saved: heatmap.png")
    plt.close()


# ---------------------------------------------------------------------------
# 2. NETWORK GRAPH — domains connected by shared language
# ---------------------------------------------------------------------------

def make_network():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor(BG)
    fig.patch.set_facecolor(BG)

    # Position domains in a square
    n = len(domains)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    radius = 3
    positions = {d: (radius * np.cos(a), radius * np.sin(a))
                 for d, a in zip(domains, angles)}

    # Draw edges with weight
    edges = data.get("edges", {})
    max_weight = max(edges.values()) if edges else 1

    for edge_str, weight in edges.items():
        parts = edge_str.split(" <-> ")
        if len(parts) == 2 and parts[0] in positions and parts[1] in positions:
            x = [positions[parts[0]][0], positions[parts[1]][0]]
            y = [positions[parts[0]][1], positions[parts[1]][1]]
            thickness = 1 + (weight / max_weight) * 12
            alpha = 0.3 + (weight / max_weight) * 0.5
            ax.plot(x, y, color="#ff006e", linewidth=thickness,
                    alpha=alpha, solid_capstyle="round")
            # Label the edge
            mx, my = np.mean(x), np.mean(y)
            ax.text(mx, my, str(weight), fontsize=9, ha="center",
                    va="center", color=COLD, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=BG, alpha=0.8))

    # Draw nodes
    for i, (domain, pos) in enumerate(positions.items()):
        circle = plt.Circle(pos, 0.6, color=HOT_COLORS[i % len(HOT_COLORS)],
                           alpha=0.9, zorder=5)
        ax.add_patch(circle)
        ax.text(pos[0], pos[1], domain.replace("_", "\n"),
                ha="center", va="center", fontsize=9, fontweight="bold",
                color="white", zorder=6)

    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Shared Language Network\nLines = phrases used across domains",
                  fontsize=13, fontweight="bold", color=COLD, pad=20)

    plt.tight_layout()
    plt.savefig("network.png", dpi=200, facecolor=BG)
    print("Saved: network.png")
    plt.close()


# ---------------------------------------------------------------------------
# 3. RADAR / FINGERPRINT — each domain's control language profile
# ---------------------------------------------------------------------------

def make_radar():
    fig, axes = plt.subplots(2, 2, figsize=(12, 12),
                              subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG)

    angles_r = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
    angles_r = np.concatenate([angles_r, [angles_r[0]]])  # close the loop

    for idx, (domain, ax) in enumerate(zip(domains, axes.flat)):
        values = [data["heatmap"][domain][c] for c in categories]
        values = values + [values[0]]  # close

        ax.fill(angles_r, values, color=HOT_COLORS[idx % len(HOT_COLORS)],
                alpha=0.25)
        ax.plot(angles_r, values, color=HOT_COLORS[idx % len(HOT_COLORS)],
                linewidth=2)
        ax.scatter(angles_r[:-1], values[:-1],
                   color=HOT_COLORS[idx % len(HOT_COLORS)], s=40, zorder=5)

        ax.set_xticks(angles_r[:-1])
        ax.set_xticklabels([c.replace("_", "\n") for c in categories],
                           fontsize=7, color=COLD)
        ax.set_title(domain.replace("_", " "), fontsize=12,
                     fontweight="bold", color=COLD, pad=20)
        ax.set_facecolor(BG)
        ax.grid(color=GRID, alpha=0.3)

    plt.suptitle("Institutional Control Fingerprints",
                  fontsize=15, fontweight="bold", color=COLD, y=1.02)
    plt.tight_layout()
    plt.savefig("radar.png", dpi=200, facecolor=BG, bbox_inches="tight")
    print("Saved: radar.png")
    plt.close()


# ---------------------------------------------------------------------------
# 4. OVERLAP MATRIX — pairwise similarity between domains
# ---------------------------------------------------------------------------

def make_overlap_matrix():
    fig, ax = plt.subplots(figsize=(8, 8))

    # Build similarity from shared phrases
    matrix = np.zeros((len(domains), len(domains)))
    edges = data.get("edges", {})
    for edge_str, weight in edges.items():
        parts = edge_str.split(" <-> ")
        if len(parts) == 2:
            try:
                i = domains.index(parts[0])
                j = domains.index(parts[1])
                matrix[i][j] = weight
                matrix[j][i] = weight
            except ValueError:
                pass

    cmap = LinearSegmentedColormap.from_list("overlap", [BG, "#ff006e", COLD])
    im = ax.imshow(matrix, cmap=cmap)

    ax.set_xticks(range(len(domains)))
    ax.set_xticklabels([d.replace("_", "\n") for d in domains],
                        fontsize=10, fontweight="bold")
    ax.set_yticks(range(len(domains)))
    ax.set_yticklabels([d.replace("_", " ") for d in domains], fontsize=10)

    for i in range(len(domains)):
        for j in range(len(domains)):
            val = int(matrix[i, j])
            if val > 0:
                color = "white" if val > matrix.max() * 0.5 else COLD
                ax.text(j, i, str(val), ha="center", va="center",
                        fontsize=16, fontweight="bold", color=color)

    ax.set_title("How Much Institutional Language Is Shared",
                  fontsize=13, fontweight="bold", color=COLD, pad=15)
    plt.colorbar(im, ax=ax, label="shared phrases", shrink=0.8)
    plt.tight_layout()
    plt.savefig("overlap.png", dpi=200, facecolor=BG)
    print("Saved: overlap.png")
    plt.close()


# ---------------------------------------------------------------------------
# RUN ALL
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\nGenerating painting source images...\n")
    make_heatmap()
    make_network()
    make_radar()
    make_overlap_matrix()
    print("\nDone. Four PNGs ready to project or paint from.")
    print("Files: heatmap.png, network.png, radar.png, overlap.png")
