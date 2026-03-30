"""
Personhood Corpus Analyzer
Compares language across four institutional domains that define/deny personhood:
  1. Psychiatric diagnosis (DSM-5)
  2. Gender recognition law
  3. Animal welfare / property law
  4. AI regulation / sentience proposals

Outputs: heatmaps, network graphs, and overlap reports
that can serve as source material for paintings.
"""

import re
import json
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. CORPORA — real institutional texts from DSM-5, UK GRA, US statutes,
#    Animal Welfare Act, EU AI Act
# ---------------------------------------------------------------------------

from corpora import psychiatric, gender_law, animal_law, ai_regulation

corpora = {
    "psychiatric": psychiatric,
    "gender_law": gender_law,
    "animal_law": animal_law,
    "ai_regulation": ai_regulation,
}


# ---------------------------------------------------------------------------
# 2. PERSONHOOD KEYWORDS — the institutional language of defining/denying
# ---------------------------------------------------------------------------

# Words and phrases that show up when institutions decide who/what is real
personhood_lexicon = {
    "assessment": [
        "assess", "assessment", "evaluate", "evaluation", "determine",
        "determination", "examine", "examination", "classify", "classification",
        "diagnose", "diagnosis", "audit", "inspect", "review"
    ],
    "authority": [
        "qualified", "professional", "registered", "certified", "authorized",
        "practitioner", "clinician", "examiner", "inspector", "auditor",
        "panel", "authority", "expert"
    ],
    "denial_of_self_knowledge": [
        "lacks insight", "unable to provide reliable", "self-report",
        "self-declaration is not sufficient", "subjective experience",
        "not directly relevant", "not considered reliable", "self-knowledge",
        "internal states", "subordinate to"
    ],
    "institutional_power": [
        "the state", "legal", "regulatory", "jurisdiction", "statute",
        "regulation", "criteria", "standards", "compliance", "framework",
        "burden of proof", "contingent upon", "administrative"
    ],
    "personhood_status": [
        "person", "personhood", "agent", "property", "product", "subject",
        "patient", "applicant", "individual", "citizen", "owner", "operator",
        "system", "animal", "entity"
    ],
    "capacity": [
        "capacity", "ability", "functioning", "capable", "autonomy",
        "autonomous", "consent", "judgment", "awareness", "consciousness",
        "sentience", "understanding", "creativity", "insight", "perception",
        "reality"
    ]
}


# ---------------------------------------------------------------------------
# 3. ANALYSIS
# ---------------------------------------------------------------------------

def tokenize(text):
    """Lowercase and split into words."""
    return re.findall(r"[a-z']+", text.lower())


def count_lexicon_hits(text, lexicon):
    """Count how many times each lexicon category appears in text."""
    tokens = tokenize(text)
    full_text = text.lower()
    hits = {}
    for category, terms in lexicon.items():
        count = 0
        for term in terms:
            if " " in term:
                # phrase search
                count += full_text.count(term)
            else:
                count += tokens.count(term)
        hits[category] = count
    return hits


def find_shared_phrases(corpora, min_length=3, min_domains=2):
    """Find multi-word phrases that appear across multiple domains."""
    domain_ngrams = {}
    for domain, text in corpora.items():
        tokens = tokenize(text)
        ngrams = set()
        for n in range(min_length, min_length + 3):
            for i in range(len(tokens) - n + 1):
                ngrams.add(" ".join(tokens[i:i+n]))
        domain_ngrams[domain] = ngrams

    # find overlaps
    all_ngrams = set()
    for ngrams in domain_ngrams.values():
        all_ngrams |= ngrams

    shared = {}
    for ngram in all_ngrams:
        domains = [d for d, ng in domain_ngrams.items() if ngram in ng]
        if len(domains) >= min_domains:
            shared[ngram] = domains

    return shared


def generate_report(corpora, lexicon):
    """Main analysis — returns structured results."""
    # Per-domain lexicon counts
    domain_profiles = {}
    for domain, text in corpora.items():
        domain_profiles[domain] = count_lexicon_hits(text, lexicon)

    # Shared phrases
    shared = find_shared_phrases(corpora)

    # Sort shared phrases by how many domains they span
    shared_sorted = sorted(shared.items(), key=lambda x: -len(x[1]))

    return domain_profiles, shared_sorted


# ---------------------------------------------------------------------------
# 4. VISUALIZATION (text-based; swap for matplotlib when ready)
# ---------------------------------------------------------------------------

def print_heatmap(domain_profiles):
    """Print a text heatmap of lexicon hits per domain."""
    categories = list(next(iter(domain_profiles.values())).keys())
    domains = list(domain_profiles.keys())

    # Header
    col_width = 14
    print("\n" + "=" * 70)
    print("INSTITUTIONAL LANGUAGE HEATMAP")
    print("How each domain talks about defining/denying personhood")
    print("=" * 70)
    print(f"\n{'':>24}", end="")
    for d in domains:
        print(f"{d:>{col_width}}", end="")
    print()
    print("-" * (24 + col_width * len(domains)))

    for cat in categories:
        print(f"{cat:>24}", end="")
        for d in domains:
            val = domain_profiles[d][cat]
            # visual intensity
            bar = "#" * min(val, 12)
            print(f"{bar:>{col_width}}", end="")
        print(f"  ({cat})")
    print()


def print_shared_phrases(shared_sorted, limit=30):
    """Print phrases shared across domains."""
    print("\n" + "=" * 70)
    print("SHARED LANGUAGE ACROSS DOMAINS")
    print("Phrases that appear in multiple institutional texts")
    print("=" * 70 + "\n")

    for phrase, domains in shared_sorted[:limit]:
        domain_str = " + ".join(sorted(domains))
        print(f"  \"{phrase}\"")
        print(f"    found in: {domain_str}\n")


def print_network_edges(shared_sorted, limit=50):
    """Print domain connections as edges for network visualization."""
    print("\n" + "=" * 70)
    print("NETWORK EDGES (for visualization)")
    print("Each shared phrase is a connection between domains")
    print("=" * 70 + "\n")

    edge_weights = Counter()
    for phrase, domains in shared_sorted[:limit]:
        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                edge = tuple(sorted([domains[i], domains[j]]))
                edge_weights[edge] += 1

    for edge, weight in edge_weights.most_common():
        bar = "=" * weight
        print(f"  {edge[0]:>14} <{bar}> {edge[1]:<14}  ({weight} shared phrases)")
    print()


def export_for_painting(domain_profiles, shared_sorted, path="painting_data.json"):
    """Export structured data you can use as painting source material."""
    output = {
        "heatmap": domain_profiles,
        "shared_phrases": [
            {"phrase": phrase, "domains": domains}
            for phrase, domains in shared_sorted[:50]
        ],
        "edges": {}
    }

    edge_weights = Counter()
    for phrase, domains in shared_sorted:
        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                edge = f"{sorted([domains[i], domains[j]])[0]} <-> {sorted([domains[i], domains[j]])[1]}"
                edge_weights[edge] += 1
    output["edges"] = dict(edge_weights.most_common())

    outpath = Path(path)
    outpath.write_text(json.dumps(output, indent=2))
    print(f"\nExported painting source data to {outpath.resolve()}")


# ---------------------------------------------------------------------------
# 5. RUN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\nPERSONHOOD CORPUS ANALYZER")
    print("Comparing how institutions define and deny personhood across domains\n")

    profiles, shared = generate_report(corpora, personhood_lexicon)

    print_heatmap(profiles)
    print_shared_phrases(shared)
    print_network_edges(shared)
    export_for_painting(profiles, shared)

    print("\n" + "-" * 70)
    print("NEXT STEPS:")
    print("  1. Replace sample texts with real excerpts from:")
    print("     - DSM-5 schizophrenia criteria")
    print("     - Your state's gender recognition statutes")
    print("     - Relevant animal property/welfare law")
    print("     - EU AI Act or similar regulation")
    print("  2. Run: python analyze.py")
    print("  3. Use painting_data.json as source material")
    print("  4. See visualize.py for matplotlib graphics (coming next)")
    print("-" * 70)
