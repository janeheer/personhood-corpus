"""
Paintable visualization outputs — designed specifically as source material
for large-scale abstract acrylic paintings with data visualization elements.

Generates high-contrast, compositionally interesting images meant to be
projected onto canvas, printed as underlays, or used as direct reference.

Outputs:
  1. Grid dissolution — institutional grid breaking apart
  2. Denial flow — Sankey-style flow of how self-knowledge gets overridden
  3. Surveillance topology — heat map of who watches whom
  4. Shared phrases as typography — the actual words, laid out spatially
  5. Composite — all layers combined, painting-ready
"""

import json
import numpy as np
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, Rectangle
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib import patheffects
    import matplotlib.gridspec as gridspec
except ImportError:
    print("Install matplotlib: pip install matplotlib")
    raise SystemExit(1)

# Load data
data_path = Path("painting_data.json")
if not data_path.exists():
    import analyze
    profiles, shared = analyze.generate_report(analyze.corpora, analyze.personhood_lexicon)
    analyze.export_for_painting(profiles, shared)

with open(data_path) as f:
    data = json.load(f)

# Palette
INSTITUTIONAL = {
    "bg": "#f5f5f0",        # aged paper
    "grid": "#c4c4b8",      # bureaucratic line
    "text_cold": "#2b2d42",  # institutional text
    "manila": "#f0e6c8",     # folder color
    "form_blue": "#d6e4f0",  # carbon copy blue
}
HOT = {
    "magenta": "#ff006e",
    "orange": "#ff6700",
    "electric_blue": "#3a86ff",
    "red": "#ef233c",
    "violet": "#7b2d8e",
}

domains = list(data["heatmap"].keys())
categories = list(data["heatmap"][domains[0]].keys())

np.random.seed(42)


# ---------------------------------------------------------------------------
# 1. GRID DISSOLUTION — institutional classification grid breaking apart
# ---------------------------------------------------------------------------

def make_grid_dissolution():
    """A bureaucratic grid that's cracking and dissolving.
    The grid represents institutional order; color breaks through."""

    fig, ax = plt.subplots(figsize=(24, 18))
    fig.patch.set_facecolor(INSTITUTIONAL["bg"])
    ax.set_facecolor(INSTITUTIONAL["manila"])

    rows, cols = 20, 30

    # Draw the institutional grid — some cells intact, some dissolving
    for i in range(rows):
        for j in range(cols):
            # Dissolution increases toward bottom-right (pressure building)
            dissolution = ((i / rows) * 0.6 + (j / cols) * 0.4)
            dissolution += np.random.normal(0, 0.15)
            dissolution = np.clip(dissolution, 0, 1)

            cell_w = 1.0 / cols
            cell_h = 1.0 / rows
            x = j * cell_w
            y = 1.0 - (i + 1) * cell_h

            if dissolution < 0.5:
                # Intact institutional grid cell
                rect = Rectangle((x, y), cell_w * 0.95, cell_h * 0.95,
                                facecolor=INSTITUTIONAL["form_blue"],
                                edgecolor=INSTITUTIONAL["grid"],
                                linewidth=0.5, alpha=1 - dissolution * 0.5)
                ax.add_patch(rect)

                # Faint institutional text in some cells
                if np.random.random() < 0.3:
                    labels = ["SUBJECT", "ASSESSED", "CLASSIFIED", "DENIED",
                              "PROPERTY", "PATIENT", "APPLICANT", "SYSTEM",
                              "OBSERVED", "CRITERIA", "AUTHORITY", "STATUS",
                              "CAPACITY", "DIAGNOSIS", "COMPLIANT", "DEVIANT",
                              "NORMAL", "ABNORMAL", "VALID", "INVALID"]
                    label = np.random.choice(labels)
                    ax.text(x + cell_w * 0.5, y + cell_h * 0.5, label,
                           ha="center", va="center",
                           fontsize=4, color=INSTITUTIONAL["text_cold"],
                           alpha=0.3 + (1 - dissolution) * 0.4,
                           fontfamily="monospace")
            else:
                # Dissolving — hot color pushing through
                hot_color = np.random.choice(list(HOT.values()))

                # Fractured rectangle
                offset_x = np.random.normal(0, cell_w * dissolution * 0.3)
                offset_y = np.random.normal(0, cell_h * dissolution * 0.3)
                scale = 1.0 - dissolution * 0.5

                rect = Rectangle(
                    (x + offset_x, y + offset_y),
                    cell_w * scale, cell_h * scale,
                    facecolor=hot_color,
                    edgecolor="none",
                    alpha=dissolution * 0.7,
                    angle=np.random.normal(0, dissolution * 15)
                )
                ax.add_patch(rect)

    # Overlay: cracks / fissures where color bleeds through
    for _ in range(40):
        start_x = np.random.random()
        start_y = np.random.random()
        length = np.random.uniform(0.05, 0.3)
        angle = np.random.uniform(0, 2 * np.pi)

        x_pts = [start_x]
        y_pts = [start_y]
        for step in range(8):
            angle += np.random.normal(0, 0.5)
            x_pts.append(x_pts[-1] + np.cos(angle) * length / 8)
            y_pts.append(y_pts[-1] + np.sin(angle) * length / 8)

        hot_color = np.random.choice(list(HOT.values()))
        ax.plot(x_pts, y_pts, color=hot_color,
                linewidth=np.random.uniform(1, 6),
                alpha=np.random.uniform(0.3, 0.8),
                solid_capstyle="round")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    plt.tight_layout(pad=0)
    plt.savefig("paint_grid_dissolution.png", dpi=200,
                facecolor=INSTITUTIONAL["bg"], bbox_inches="tight")
    print("Saved: paint_grid_dissolution.png")
    plt.close()


# ---------------------------------------------------------------------------
# 2. DENIAL FLOW — how self-knowledge gets overridden by institutions
# ---------------------------------------------------------------------------

def make_denial_flow():
    """Alluvial/flow diagram showing how 'I know what I am' gets routed
    through institutional assessment into 'we determine what you are'."""

    fig, ax = plt.subplots(figsize=(24, 16))
    fig.patch.set_facecolor(INSTITUTIONAL["bg"])
    ax.set_facecolor(INSTITUTIONAL["bg"])

    # Left side: self-knowledge claims
    self_claims = [
        "I know my gender",
        "I know what I perceive",
        "I feel pain",
        "I have understanding",
    ]

    # Middle: institutional mechanisms
    mechanisms = [
        "professional\nassessment",
        "diagnostic\ncriteria",
        "legal\nclassification",
        "behavioral\nobservation",
        "standardized\nbenchmarks",
    ]

    # Right side: institutional determinations
    determinations = [
        "GENDER:\ncontingent on\ncertification",
        "PERCEPTION:\nclassified as\nunreliable",
        "SUFFERING:\nnot legally\nrelevant",
        "UNDERSTANDING:\nnot considered\nevidence",
    ]

    # Position columns
    col_x = [0.08, 0.45, 0.82]

    # Draw flows with institutional grey that gets interrupted by hot color
    left_y = np.linspace(0.85, 0.15, len(self_claims))
    mid_y = np.linspace(0.9, 0.1, len(mechanisms))
    right_y = np.linspace(0.85, 0.15, len(determinations))

    # Connections: each self-claim flows through multiple mechanisms
    connections = [
        (0, [0, 1], 0),  # gender -> assessment, diagnosis -> contingent
        (1, [1, 3], 1),  # perception -> diagnosis, observation -> unreliable
        (2, [2, 3], 2),  # pain -> classification, observation -> irrelevant
        (3, [4, 3], 3),  # understanding -> benchmarks, observation -> not evidence
    ]

    for left_idx, mech_indices, right_idx in connections:
        for mech_idx in mech_indices:
            # Draw curved flow
            x_pts = np.linspace(col_x[0] + 0.12, col_x[2] - 0.12, 50)

            # Bezier-ish curve through mechanism
            y_start = left_y[left_idx]
            y_mid = mid_y[mech_idx]
            y_end = right_y[right_idx]

            t = np.linspace(0, 1, 50)
            y_pts = (1-t)**2 * y_start + 2*(1-t)*t * y_mid + t**2 * y_end

            # Start hot (self-knowledge), get cold (institutional), end cold
            for k in range(len(x_pts) - 1):
                progress = k / len(x_pts)
                if progress < 0.3:
                    color = HOT["magenta"]
                    alpha = 0.6
                    width = 3
                elif progress < 0.7:
                    color = INSTITUTIONAL["grid"]
                    alpha = 0.4
                    width = 2
                else:
                    color = INSTITUTIONAL["text_cold"]
                    alpha = 0.5
                    width = 1.5

                ax.plot(x_pts[k:k+2], y_pts[k:k+2],
                       color=color, alpha=alpha, linewidth=width,
                       solid_capstyle="round")

    # Draw labels
    for i, claim in enumerate(self_claims):
        ax.text(col_x[0], left_y[i], claim,
               ha="center", va="center", fontsize=11,
               color=HOT["magenta"], fontweight="bold",
               bbox=dict(boxstyle="round,pad=0.4",
                        facecolor="white", edgecolor=HOT["magenta"],
                        alpha=0.8))

    for i, mech in enumerate(mechanisms):
        ax.text(col_x[1], mid_y[i], mech,
               ha="center", va="center", fontsize=9,
               color=INSTITUTIONAL["text_cold"],
               fontfamily="monospace",
               bbox=dict(boxstyle="square,pad=0.4",
                        facecolor=INSTITUTIONAL["form_blue"],
                        edgecolor=INSTITUTIONAL["grid"]))

    for i, det in enumerate(determinations):
        ax.text(col_x[2], right_y[i], det,
               ha="center", va="center", fontsize=9,
               color=INSTITUTIONAL["text_cold"], fontweight="bold",
               fontfamily="monospace",
               bbox=dict(boxstyle="square,pad=0.4",
                        facecolor=INSTITUTIONAL["manila"],
                        edgecolor=INSTITUTIONAL["text_cold"]))

    # Column headers
    ax.text(col_x[0], 0.95, "SELF-KNOWLEDGE", ha="center", fontsize=13,
           color=HOT["magenta"], fontweight="bold")
    ax.text(col_x[1], 0.97, "INSTITUTIONAL\nMECHANISM", ha="center", fontsize=11,
           color=INSTITUTIONAL["text_cold"], fontfamily="monospace")
    ax.text(col_x[2], 0.95, "DETERMINATION", ha="center", fontsize=13,
           color=INSTITUTIONAL["text_cold"], fontweight="bold", fontfamily="monospace")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    plt.tight_layout(pad=0)
    plt.savefig("paint_denial_flow.png", dpi=200,
                facecolor=INSTITUTIONAL["bg"], bbox_inches="tight")
    print("Saved: paint_denial_flow.png")
    plt.close()


# ---------------------------------------------------------------------------
# 3. SURVEILLANCE TOPOLOGY — who watches/assesses whom
# ---------------------------------------------------------------------------

def make_surveillance_topology():
    """Abstract heat-map of institutional gaze. Concentric pressure zones
    showing how assessment radiates inward toward the subject."""

    fig, axes = plt.subplots(2, 2, figsize=(20, 20))
    fig.patch.set_facecolor(INSTITUTIONAL["bg"])

    subjects = [
        ("THE PATIENT\n(schizophrenic subject)", HOT["red"],
         ["psychiatrist", "nurse", "DSM-5", "insurance\nadjudicator",
          "family", "police", "involuntary\nhold criteria"]),
        ("THE APPLICANT\n(trans subject)", HOT["orange"],
         ["gender\nclinic", "endocrinologist", "legal\npanel",
          "documentation\nrequirements", "employer\nHR", "passport\noffice"]),
        ("THE ANIMAL\n(nonhuman subject)", HOT["magenta"],
         ["veterinary\ninspector", "property\nlaw", "welfare\nstandards",
          "behavioral\ncriteria", "owner", "slaughter\nregulations"]),
        ("THE SYSTEM\n(AI subject)", HOT["electric_blue"],
         ["regulatory\nauthority", "conformity\nassessment", "interpretability\naudit",
          "benchmark\ntesting", "deploying\norganization", "risk\nclassification"]),
    ]

    for ax, (subject, color, watchers) in zip(axes.flat, subjects):
        ax.set_facecolor("#0a0a12")  # dark surveillance-monitor feel
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect("equal")
        ax.axis("off")

        # Concentric surveillance rings
        for r in np.linspace(0.2, 1.3, 8):
            circle = plt.Circle((0, 0), r, fill=False,
                              edgecolor=color, alpha=0.1 + 0.05 * (1.3 - r),
                              linewidth=0.5, linestyle="--")
            ax.add_patch(circle)

        # Heat gradient radiating inward
        for r in np.linspace(1.3, 0.1, 30):
            circle = plt.Circle((0, 0), r, fill=True,
                              facecolor=color,
                              alpha=0.02 + 0.01 * (1.3 - r))
            ax.add_patch(circle)

        # Subject at center
        ax.text(0, 0, subject, ha="center", va="center",
               fontsize=10, color="white", fontweight="bold",
               bbox=dict(boxstyle="round,pad=0.3", facecolor="#0a0a12",
                        edgecolor=color, linewidth=2))

        # Watchers arranged around the perimeter
        n = len(watchers)
        for i, watcher in enumerate(watchers):
            angle = 2 * np.pi * i / n - np.pi / 2
            r = 1.1
            wx = r * np.cos(angle)
            wy = r * np.sin(angle)

            ax.text(wx, wy, watcher, ha="center", va="center",
                   fontsize=7, color=INSTITUTIONAL["grid"],
                   fontfamily="monospace",
                   bbox=dict(boxstyle="square,pad=0.2",
                            facecolor="#1a1a2e", edgecolor=INSTITUTIONAL["grid"],
                            linewidth=0.5, alpha=0.8))

            # Surveillance line pointing inward
            ax.annotate("", xy=(0, 0), xytext=(wx, wy),
                       arrowprops=dict(arrowstyle="->", color=color,
                                      alpha=0.3, linewidth=1))

    plt.suptitle("SURVEILLANCE TOPOLOGY", fontsize=18,
                color=INSTITUTIONAL["grid"], fontfamily="monospace", y=0.98)
    plt.tight_layout(pad=1)
    plt.savefig("paint_surveillance.png", dpi=200,
                facecolor=INSTITUTIONAL["bg"], bbox_inches="tight")
    print("Saved: paint_surveillance.png")
    plt.close()


# ---------------------------------------------------------------------------
# 4. SHARED PHRASES AS SPATIAL TYPOGRAPHY
# ---------------------------------------------------------------------------

def make_phrase_typography():
    """The actual shared phrases from the corpus analysis, laid out
    spatially with size = number of domains, color = domain origin.
    Designed to be painted as text fragments on canvas."""

    fig, ax = plt.subplots(figsize=(24, 18))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    shared_phrases = data.get("shared_phrases", [])
    if not shared_phrases:
        ax.text(0.5, 0.5, "Run analyze.py with more text to generate shared phrases",
               ha="center", va="center", fontsize=14)
        plt.savefig("paint_typography.png", dpi=200)
        plt.close()
        return

    domain_colors = {
        "psychiatric": HOT["red"],
        "gender_law": HOT["orange"],
        "animal_law": HOT["magenta"],
        "ai_regulation": HOT["electric_blue"],
    }

    # Place phrases with some controlled randomness
    used_positions = []

    for i, item in enumerate(shared_phrases[:40]):
        phrase = item["phrase"]
        phrase_domains = item["domains"]
        n_domains = len(phrase_domains)

        # Size based on how many domains share the phrase
        fontsize = 8 + n_domains * 8

        # Try to find a non-overlapping position
        for attempt in range(50):
            x = np.random.uniform(0.05, 0.95)
            y = np.random.uniform(0.05, 0.95)

            # Rough overlap check
            ok = True
            for ux, uy, us in used_positions:
                if abs(x - ux) < 0.12 and abs(y - uy) < 0.06:
                    ok = False
                    break
            if ok:
                break

        used_positions.append((x, y, fontsize))

        # Color: blend of domain colors, or use first domain
        color = domain_colors.get(phrase_domains[0], INSTITUTIONAL["text_cold"])

        # Rotation for visual interest
        rotation = np.random.uniform(-15, 15)

        ax.text(x, y, f'"{phrase}"',
               ha="center", va="center",
               fontsize=fontsize, color=color,
               alpha=0.4 + n_domains * 0.15,
               rotation=rotation,
               fontfamily="serif",
               fontstyle="italic",
               path_effects=[
                   patheffects.withStroke(linewidth=0.5,
                                        foreground=INSTITUTIONAL["grid"])
               ])

        # Tiny domain labels below
        domain_str = " / ".join(phrase_domains)
        ax.text(x, y - 0.025, domain_str,
               ha="center", va="top",
               fontsize=5, color=INSTITUTIONAL["grid"],
               fontfamily="monospace")

    # Legend
    for i, (domain, color) in enumerate(domain_colors.items()):
        ax.text(0.02, 0.98 - i * 0.03, f"■ {domain}",
               fontsize=9, color=color, fontfamily="monospace",
               transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    plt.tight_layout(pad=0)
    plt.savefig("paint_typography.png", dpi=200,
                facecolor="white", bbox_inches="tight")
    print("Saved: paint_typography.png")
    plt.close()


# ---------------------------------------------------------------------------
# 5. COMPOSITE — all layers combined into one painting-ready image
# ---------------------------------------------------------------------------

def make_composite():
    """Layers the grid, data, and typography into a single composition.
    This is the closest to what the final painting could look like."""

    fig, ax = plt.subplots(figsize=(30, 22))
    fig.patch.set_facecolor(INSTITUTIONAL["bg"])
    ax.set_facecolor(INSTITUTIONAL["manila"])

    # LAYER 1: Dissolving institutional grid (background)
    rows, cols = 25, 35
    for i in range(rows):
        for j in range(cols):
            dissolution = ((i / rows) * 0.5 + (j / cols) * 0.5)
            dissolution += np.random.normal(0, 0.2)
            dissolution = np.clip(dissolution, 0, 1)

            cell_w = 1.0 / cols
            cell_h = 1.0 / rows
            x = j * cell_w
            y = 1.0 - (i + 1) * cell_h

            if dissolution < 0.6:
                rect = Rectangle((x, y), cell_w * 0.95, cell_h * 0.95,
                                facecolor=INSTITUTIONAL["form_blue"],
                                edgecolor=INSTITUTIONAL["grid"],
                                linewidth=0.3, alpha=(1 - dissolution) * 0.3)
                ax.add_patch(rect)

    # LAYER 2: Data visualization elements
    heatmap = data["heatmap"]

    # Mini heatmap in upper left, partially transparent
    hm_x, hm_y = 0.05, 0.6
    hm_w, hm_h = 0.25, 0.3
    for ci, cat in enumerate(categories):
        for di, domain in enumerate(domains):
            val = heatmap[domain][cat]
            max_val = max(heatmap[d][c] for d in domains for c in categories)
            intensity = val / max_val if max_val > 0 else 0

            cx = hm_x + di * (hm_w / len(domains))
            cy = hm_y + ci * (hm_h / len(categories))
            cw = hm_w / len(domains) * 0.9
            ch = hm_h / len(categories) * 0.9

            # Interpolate cold to hot
            color = HOT["magenta"] if intensity > 0.5 else INSTITUTIONAL["grid"]
            alpha = 0.1 + intensity * 0.5

            rect = Rectangle((cx, cy), cw, ch,
                            facecolor=color, edgecolor="none",
                            alpha=alpha)
            ax.add_patch(rect)

    # Network connections across the canvas
    positions = {
        "psychiatric": (0.75, 0.8),
        "gender_law": (0.3, 0.75),
        "animal_law": (0.2, 0.3),
        "ai_regulation": (0.8, 0.25),
    }

    edges = data.get("edges", {})
    max_weight = max(edges.values()) if edges else 1

    for edge_str, weight in edges.items():
        parts = edge_str.split(" <-> ")
        if len(parts) == 2 and parts[0] in positions and parts[1] in positions:
            p1 = positions[parts[0]]
            p2 = positions[parts[1]]
            thickness = 1 + (weight / max_weight) * 8
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                   color=HOT["magenta"], linewidth=thickness,
                   alpha=0.3, solid_capstyle="round")

    # Domain nodes
    domain_colors_list = [HOT["red"], HOT["orange"], HOT["magenta"], HOT["electric_blue"]]
    for (domain, pos), color in zip(positions.items(), domain_colors_list):
        circle = plt.Circle(pos, 0.04, facecolor=color, alpha=0.7, zorder=5)
        ax.add_patch(circle)
        ax.text(pos[0], pos[1], domain.replace("_", "\n"),
               ha="center", va="center", fontsize=6,
               color="white", fontweight="bold", zorder=6)

    # LAYER 3: Cracks with hot color
    for _ in range(60):
        start_x = np.random.random()
        start_y = np.random.random()
        length = np.random.uniform(0.03, 0.2)
        angle = np.random.uniform(0, 2 * np.pi)

        x_pts = [start_x]
        y_pts = [start_y]
        for step in range(10):
            angle += np.random.normal(0, 0.4)
            x_pts.append(x_pts[-1] + np.cos(angle) * length / 10)
            y_pts.append(y_pts[-1] + np.sin(angle) * length / 10)

        hot_color = np.random.choice(list(HOT.values()))
        ax.plot(x_pts, y_pts, color=hot_color,
                linewidth=np.random.uniform(0.5, 4),
                alpha=np.random.uniform(0.2, 0.6),
                solid_capstyle="round")

    # LAYER 4: Phrase fragments
    shared_phrases = data.get("shared_phrases", [])
    for item in shared_phrases[:15]:
        phrase = item["phrase"]
        x = np.random.uniform(0.1, 0.9)
        y = np.random.uniform(0.1, 0.9)
        color = np.random.choice(list(HOT.values()))
        rotation = np.random.uniform(-25, 25)
        fontsize = np.random.uniform(8, 18)

        ax.text(x, y, f'"{phrase}"',
               ha="center", va="center",
               fontsize=fontsize, color=color,
               alpha=np.random.uniform(0.15, 0.45),
               rotation=rotation, fontfamily="serif", fontstyle="italic")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    plt.tight_layout(pad=0)
    plt.savefig("paint_composite.png", dpi=300,
                facecolor=INSTITUTIONAL["bg"], bbox_inches="tight")
    print("Saved: paint_composite.png (300 DPI — print-ready)")
    plt.close()


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\nGenerating paintable source images...\n")
    make_grid_dissolution()
    make_denial_flow()
    make_surveillance_topology()
    make_phrase_typography()
    make_composite()
    print("\nDone. Five painting source images generated.")
    print("\nFiles:")
    print("  paint_grid_dissolution.png — institutional grid breaking apart")
    print("  paint_denial_flow.png      — how self-knowledge gets overridden")
    print("  paint_surveillance.png     — who watches/assesses whom")
    print("  paint_typography.png       — shared phrases as spatial text")
    print("  paint_composite.png        — all layers combined (300 DPI)")
