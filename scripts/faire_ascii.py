"""Portrait ASCII animé (SVG) à partir d'une photo sur fond clair uni.
Usage : python3 scripts/faire_ascii.py photo.png   (la photo n'est pas versionnée)"""
import sys
from html import escape
from pathlib import Path
import cv2, numpy as np

RAMPE = " .`:-=+*cs#%@"  # du plus clair (vide) au plus dense
COLS, LARGEUR, HAUTEUR = 92, 370, 400


def photo_en_ascii(chemin):
    """Détoure le fond par remplissage depuis les coins, renforce le contraste (CLAHE), échantillonne une grille. O(pixels)."""
    gris = cv2.cvtColor(cv2.imread(chemin), cv2.COLOR_BGR2GRAY)
    h, l = gris.shape
    gris = gris[int(h * .05):, int(l * .1):int(l * .9)]  # recadrage sur la tête et les épaules
    masque = np.zeros((gris.shape[0] + 2, gris.shape[1] + 2), np.uint8)
    for coin in ((0, 0), (gris.shape[1] - 1, 0)):
        cv2.floodFill(gris.copy(), masque, coin, 0, 12, 12, cv2.FLOODFILL_MASK_ONLY | 4 | (255 << 8))
    gris = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gris)
    fond = masque[1:-1, 1:-1] > 0
    lignes = round(COLS * gris.shape[0] / gris.shape[1] * 0.5)  # un caractère est ~2x plus haut que large
    petit = cv2.resize(gris, (COLS, lignes), interpolation=cv2.INTER_AREA).astype(int)
    vide = cv2.resize(fond.astype(np.uint8), (COLS, lignes), interpolation=cv2.INTER_AREA) > 0
    indices = 1 + petit * (len(RAMPE) - 2) // 255  # fond sombre : zone claire = caractère dense
    indices[vide] = 0
    return ["".join(RAMPE[i] for i in ligne).rstrip() for ligne in indices]


def faire_svg(lignes):
    """Chaque ligne se dévoile de gauche à droite (clip animé), avec un curseur bloc, puis reste figée."""
    pas_y = HAUTEUR / (len(lignes) + 1)
    taille = pas_y * 0.95
    defs, textes = [], []
    for i, ligne in enumerate(lignes):
        debut, y = 0.3 + i * 0.07, (i + 1) * pas_y
        defs.append(f'<clipPath id="c{i}"><rect x="0" y="{y - taille:.1f}" height="{taille * 1.3:.1f}" width="0">'
                    f'<animate attributeName="width" from="0" to="{LARGEUR}" begin="{debut:.2f}s" dur=".35s" fill="freeze"/></rect></clipPath>')
        textes.append(f'<text y="{y:.1f}" clip-path="url(#c{i})" xml:space="preserve">{escape(ligne)}</text>'
                      f'<rect y="{y - taille * .8:.1f}" width="{taille * .55:.1f}" height="{taille * .9:.1f}" fill="#39d353" opacity="0">'
                      f'<animate attributeName="x" from="0" to="{LARGEUR}" begin="{debut:.2f}s" dur=".35s" fill="freeze"/>'
                      f'<set attributeName="opacity" to="1" begin="{debut:.2f}s"/><set attributeName="opacity" to="0" begin="{debut + .35:.2f}s"/></rect>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGEUR} {HAUTEUR}" width="{LARGEUR}" height="{HAUTEUR}">
<style>text{{font:{taille:.2f}px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#c9d1d9;letter-spacing:{(LARGEUR - 16) / COLS - taille * .6:.2f}px}}</style>
<rect width="{LARGEUR}" height="{HAUTEUR}" rx="10" fill="#0d1117" stroke="#30363d"/>
<defs>{"".join(defs)}</defs><g transform="translate(8,0)">{"".join(textes)}</g>
</svg>'''


if __name__ == "__main__":
    Path(__file__).resolve().parent.parent.joinpath("daris-ascii.svg").write_text(faire_svg(photo_en_ascii(sys.argv[1])), encoding="utf-8")
