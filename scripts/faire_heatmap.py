"""Graphe de contributions animé (SVG) à partir de la page publique GitHub, sans token.
Usage : python3 scripts/faire_heatmap.py darismbau"""
import json, re, sys, urllib.request
from datetime import date
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CASE, PAS, X0, Y0 = 13, 16, 34, 30  # taille d'une case, pas de la grille, marges


def lire_contributions(pseudo):
    """Renvoie [(date, niveau 0-4, nombre)] triés par date. Parcours linéaire du HTML : O(n)."""
    html = urllib.request.urlopen(f"https://github.com/users/{pseudo}/contributions").read().decode()
    nombres = {i: int(n) for i, n in re.findall(r'for="(contribution-day-component-[\d-]+)"[^>]*>(\d+) contribution', html)}
    cases = [dict(re.findall(r'([\w-]+)="([^"]*)"', td)) for td in re.findall(r'<td[^>]*ContributionCalendar-day[^>]*>', html)]
    return sorted((c["data-date"], int(c["data-level"]), nombres.get(c["id"], 0)) for c in cases if "data-date" in c)


def faire_svg(jours):
    """Une case par jour, colonne = semaine, ligne = jour de la semaine ; apparition en diagonale."""
    debut = date.fromisoformat(jours[0][0])
    decal = (debut.weekday() + 1) % 7  # GitHub commence la semaine le dimanche
    cases, mois = [], {}
    for d, niv, n in jours:
        k = (date.fromisoformat(d) - debut).days + decal
        sem, jour = divmod(k, 7)
        mois.setdefault(d[:7], sem)
        cases.append(f'<rect x="{X0 + sem * PAS}" y="{Y0 + jour * PAS}" width="{CASE}" height="{CASE}" rx="3" '
                     f'fill="{PALETTE[niv]}" style="animation-delay:{(sem + jour) * 0.025:.3f}s"><title>{n} le {d}</title></rect>')
    noms = "janv févr mars avr mai juin juil août sept oct nov déc".split()
    etiquettes = [f'<text x="{X0 + s * PAS}" y="{Y0 - 10}">{noms[int(m[5:]) - 1]}</text>'
                  for m, s in mois.items() if 2 <= s < 52]
    jours_sem = [f'<text x="4" y="{Y0 + j * PAS + 10}">{t}</text>' for j, t in ((1, "lun"), (3, "mer"), (5, "ven"))]
    total = sum(n for *_, n in jours)
    legende = "".join(f'<rect x="{722 + i * 16}" y="152" width="{CASE}" height="{CASE}" rx="3" fill="{c}"/>' for i, c in enumerate(PALETTE))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 180" width="880" height="180">
<style>
text{{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#7d8590}}
.g rect{{opacity:0;animation:apparition .35s ease-out forwards}}
@keyframes apparition{{from{{opacity:0;transform:translateY(-4px)}}to{{opacity:1;transform:none}}}}
</style>
<rect width="880" height="180" rx="10" fill="#0d1117"/>
{"".join(etiquettes)}{"".join(jours_sem)}
<g class="g">{"".join(cases)}</g>
<text x="{X0}" y="163" style="fill:#c9d1d9">{total} contributions sur les 12 derniers mois</text>
<text x="684" y="163">Moins</text>{legende}<text x="806" y="163">Plus</text>
</svg>'''


if __name__ == "__main__":
    jours = lire_contributions(sys.argv[1] if len(sys.argv) > 1 else "darismbau")
    racine = Path(__file__).resolve().parent.parent
    (racine / "data").mkdir(exist_ok=True)
    (racine / "data" / "contributions.json").write_text(json.dumps(jours))
    (racine / "contrib-heatmap.svg").write_text(faire_svg(jours), encoding="utf-8")
    print(len(jours), "jours,", sum(n for *_, n in jours), "contributions")
