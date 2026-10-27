"""Carte de présentation façon neofetch (SVG animé). Usage : python3 scripts/faire_carte.py"""
from html import escape
from pathlib import Path

LARGEUR, HAUTEUR = 490, 400
LIGNES = [
    ("Rôle", "Élève ingénieur Informatique & Réseaux"),
    ("École", "ENSISA, Mulhouse"),
    ("Focus", "Réseaux informatiques"),
    ("", "Infrastructure pour l'IA"),
    ("", "Sécurité réseau"),
    ("Projets", "Réseau opérateur multi-sites"),
    ("", "Vidéosurveillance avec IA"),
    ("", "Traceur GPS LoRaWAN"),
    ("Site", "darismbau.github.io"),
]
COULEURS = ["#f85149", "#d29922", "#39d353", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]


def faire_carte():
    """Titre, séparateur, lignes clé/valeur qui apparaissent l'une après l'autre, puis la palette."""
    y = lambda i: 100 + i * 27
    lignes = "".join(
        f'<text x="26" y="{y(i)}" style="animation-delay:{0.4 + i * 0.12:.2f}s">'
        f'<tspan class="k">{escape(c)}</tspan><tspan x="118" class="v">{escape(v)}</tspan></text>'
        for i, (c, v) in enumerate(LIGNES))
    fin = 0.4 + len(LIGNES) * 0.12
    palette = "".join(f'<rect x="{26 + i * 26}" y="{y(len(LIGNES)) + 4}" width="22" height="14" fill="{c}" '
                      f'style="animation-delay:{fin:.2f}s"/>' for i, c in enumerate(COULEURS))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGEUR} {HAUTEUR}" width="{LARGEUR}" height="{HAUTEUR}">
<style>
text{{font:13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#c9d1d9}}
.k{{fill:#39d353;font-weight:bold}} .t{{fill:#58a6ff;font-weight:bold}}
text[style],rect[style]{{opacity:0;animation:entree .45s ease-out forwards}}
@keyframes entree{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
</style>
<rect width="{LARGEUR}" height="{HAUTEUR}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="20" cy="18" r="5" fill="#f85149"/><circle cx="36" cy="18" r="5" fill="#d29922"/><circle cx="52" cy="18" r="5" fill="#3fb950"/>
<text x="26" y="58" class="t">daris<tspan fill="#c9d1d9">@</tspan>ensisa</text>
<text x="26" y="74" fill="#30363d">──────────────────────────────────────────</text>
{lignes}{palette}
</svg>'''


if __name__ == "__main__":
    Path(__file__).resolve().parent.parent.joinpath("info-card.svg").write_text(faire_carte(), encoding="utf-8")
