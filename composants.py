# -*- coding: utf-8 -*-
"""Les briques d'un écran : en-tête, tuile chiffre, carte de lecture, pied de source,
glossaire et téléchargements. La profondeur est constante d'un écran à l'autre."""
import os
import re
import textwrap
from html import escape

import pandas as pd
import streamlit as st

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
FIGURES = os.path.join(ICI, "figures")
NBSP = " "

# Glossaire : aucun sigle laissé seul (règle de vulgarisation de Priscillia, 19 août).
# Définitions reprises de sa proposition et de la note budgétaire — à valider.
GLOSSAIRE = {
    "DPT": "Document de politique transversale « Outre-mer » : l'annexe au projet de loi de finances qui "
           "additionne tous les crédits que l'État consacre aux outre-mer, tous ministères confondus.",
    "Mission Outre-mer": "La partie du budget de l'État directement portée par le ministère des Outre-mer. "
                         "Elle compte deux programmes : P138 et P123.",
    "P138": "Programme « Emploi outre-mer » : compensation des exonérations de charges des entreprises "
            "(LODEOM), Service militaire adapté (SMA), mobilité (LADOM), financement de l'économie.",
    "P123": "Programme « Conditions de vie outre-mer » : logement, aménagement et équipements, continuité "
            "territoriale, action sanitaire et sociale, dotations aux collectivités.",
    "LODEOM": "Loi pour le développement économique des outre-mer (2009). Le ministère compense aux "
              "organismes sociaux les exonérations de cotisations qu'elle accorde : la dépense suit l'emploi "
              "et la loi, sans arbitrage annuel.",
    "CP": "Crédits de paiement : l'argent effectivement décaissé dans l'année. C'est la mesure retenue partout "
          "dans cette application.",
    "dépenses fiscales": "Impôts que l'État renonce à percevoir (réductions, exonérations, taux réduits). "
                         "Elles soutiennent les outre-mer hors budget : c'est un manque à gagner estimé, pas "
                         "de l'argent versé, et il ne s'additionne donc pas aux crédits.",
    "DGOM": "Direction générale des outre-mer : l'administration centrale du ministère depuis 2013, environ "
            "180 agents répartis en quatre sous-directions.",
    "restes à payer": "Ce que l'État s'est engagé à payer et n'a pas encore payé. Il engage une opération entière "
                      "dès la signature, puis la paie au rythme des travaux.",
    "DROM": "Département et région d'outre-mer (article 73 de la Constitution) : Guadeloupe, Martinique, Guyane, "
            "La Réunion, Mayotte. La Guyane et la Martinique sont organisées en collectivités uniques depuis 2015.",
    "COM": "Collectivité d'outre-mer (article 74) : Saint-Barthélemy, Saint-Martin, Saint-Pierre-et-Miquelon, "
           "Wallis-et-Futuna, Polynésie française. Chacune a un statut sur mesure fixé par une loi organique.",
    "article 73": "Identité législative : les lois et règlements nationaux s'appliquent de plein droit, sauf "
                  "adaptation expresse.",
    "article 74": "Spécialité législative : chaque collectivité a un statut sur mesure, fixé par une loi organique, "
                  "et s'écarte plus largement de la législation nationale.",
    "habilitation": "Depuis 2003 (article 73, alinéa 3), un DROM peut être autorisé par la loi ou le règlement à fixer "
                    "lui-même les règles dans quelques matières. La Réunion en est exclue (alinéa 5).",
    "sui generis": "« De son propre genre » : la Nouvelle-Calédonie ne relève ni de l'article 73 ni de l'article 74, "
                   "mais du titre XIII de la Constitution, qui inscrit les accords de Matignon et de Nouméa.",
    "RUP": "Région ultrapériphérique de l'Union européenne : le droit européen s'y applique, avec des adaptations "
           "(article 349 du traité sur le fonctionnement de l'Union européenne).",
    "PTOM": "Pays et territoire d'outre-mer : associé à l'Union européenne sans en faire partie ; le droit européen ne "
            "s'y applique pas (annexe II du traité).",
    "mandat": "Une nomination dans un gouvernement, du décret de nomination à la fin des fonctions. Une même "
              "personne reconduite dans un nouveau gouvernement ouvre un nouveau mandat.",
    "rang": "La place du ministre dans le gouvernement, du plus élevé au plus modeste : ministre d'État, "
            "ministre, ministre délégué, secrétaire d'État. Les deux premiers siègent de plein droit au Conseil "
            "des ministres ; les deux autres passent par le ministre dont ils relèvent.",
    "rattaché à l'Intérieur": "Le portefeuille des outre-mer n'est pas autonome : il est placé auprès du "
                              "ministre de l'Intérieur, qui en a l'autorité.",
    "seuil de pauvreté national": "Un ménage est pauvre lorsque son niveau de vie est inférieur à 60 % du niveau "
                                  "de vie médian national. Avec ce seuil commun, la pauvreté des outre-mer se "
                                  "compare directement à celle de l'Hexagone.",
    "NEET": "Jeunes de 15 à 29 ans qui ne sont ni en emploi, ni en études, ni en formation (de l'anglais « not in "
            "education, employment or training »).",
    "indice de Gini": "Mesure des inégalités de revenus : 0 si tout le monde a le même revenu, 1 si une seule "
                      "personne a tout. Plus il est élevé, plus les revenus sont inégaux.",
    "PIB par habitant": "La richesse produite sur le territoire en un an, divisée par le nombre d'habitants. Elle ne "
                        "mesure pas le niveau de vie des habitants.",
    "législature": "La période entre deux élections de l'Assemblée nationale, cinq ans au plus. La 17e a commencé "
                   "en juillet 2024.",
    "groupe politique": "Les députés se rassemblent par affinités politiques. Il faut au moins quinze députés pour "
                        "former un groupe, qui donne des moyens et du temps de parole.",
    "ancrage": "Un lien avec un territoire d'outre-mer antérieur à la nomination. « Né outre-mer » : la "
               "naissance. « Autre forme » : ascendance, résidence, activité, mandat ou engagement, d'après la "
               "grille d'ancrage du CLSE.",
}


def fr_typo(t):
    """Espaces insécables du français, et un montant ne se coupe jamais."""
    for a, b in ((" »", NBSP + "»"), ("« ", "«" + NBSP), (" :", NBSP + ":"), (" ;", NBSP + ";"),
                 (" ?", NBSP + "?"), (" !", NBSP + "!"), (" %", NBSP + "%")):
        t = t.replace(a, b)
    t = re.sub(r"(\d) (?=\d{3}\b)", r"\1" + NBSP, t)
    t = re.sub(r"(\d) (?=M?d?€)", r"\1" + NBSP, t)
    return t


def fr(x, dec=1):
    """Un nombre à la française : 21,94 · 2 827."""
    s = f"{x:,.{dec}f}".replace(",", NBSP).replace(".", ",")
    return s


def deux_lignes(t, n=20):
    """Un libellé d'axe sur deux lignes au plus : les noms longs débordent sur un écran étroit."""
    return "<br>".join(textwrap.wrap(t, n)[:2]) if len(t) > n else t


def sigle(terme, affiche=None):
    """Un terme avec sa définition au survol."""
    return f'<abbr title="{escape(GLOSSAIRE[terme])}">{affiche or terme}</abbr>'


def _html(t):
    return fr_typo(t)


def entete(surtitre, titre, sous=None, accent="vert"):
    st.markdown(f'<div class="entete {accent}"><div class="filet"></div>'
                f'<div class="surtitre">{_html(surtitre)}</div><h1>{_html(titre)}</h1>'
                + (f'<div class="sous">{_html(sous)}</div>' if sous else "") + "</div>",
                unsafe_allow_html=True)


def tuile(col, valeur, legende, accent="marine"):
    col.markdown(f'<div class="tuile {accent}"><div class="valeur">{_html(valeur)}</div>'
                 f'<div class="souligne"></div><div class="legende">{_html(legende)}</div></div>',
                 unsafe_allow_html=True)


def carte(intitule, paragraphes, accent="vert", conteneur=st):
    if isinstance(paragraphes, str):
        paragraphes = [paragraphes]
    corps = "".join(f"<p>{_html(p)}</p>" for p in paragraphes)
    conteneur.markdown(f'<div class="carte {accent}"><div class="intitule">{_html(intitule)}</div>{corps}</div>',
                       unsafe_allow_html=True)


def pied(source, statut="Confirmé", renvoi=None):
    """Source officielle, statut de fiabilité (Confirmé / Estimé / Reconstitué), renvoi au rapport."""
    cls = "statut" + ("" if statut == "Confirmé" else " estime")
    r = f' · <span class="renvoi">Dans le rapport : {_html(renvoi)}</span>' if renvoi else ""
    st.markdown(f'<div class="pied"><span class="{cls}">{statut}</span>Source : {_html(source)}{r}</div>',
                unsafe_allow_html=True)


def glossaire(termes):
    """En tête d'écran, juste sous le titre : un bandeau teinté qui annonce combien de mots il explique."""
    from charte import VERT, teinte
    st.markdown(f"""<style>
    [data-testid="stExpander"] details {{ border: none; border-left: 4px solid {VERT};
        background: linear-gradient(90deg, {teinte(VERT, 0.12)} 0%, #FFFFFF 100%); border-radius: 0; }}
    [data-testid="stExpander"] summary {{ padding: 12px 16px; }}
    [data-testid="stExpander"] summary p {{ font-weight: 700; color: {VERT}; font-size: 1rem; }}
    [data-testid="stExpander"] summary:hover p {{ color: {VERT}; text-decoration: underline; }}
    </style>""", unsafe_allow_html=True)
    with st.expander(f"📖  Les {len(termes)} mots de cet écran — sigles et notions, expliqués en une phrase"):
        for t in termes:
            st.markdown(f"**{t}** — {fr_typo(GLOSSAIRE[t])}")


# Le fond de l'application : les vrais contours des treize territoires (Natural Earth), chacun dans son propre cadre,
# rangés par océan — Atlantique à gauche, océan Indien au centre, Pacifique à droite. (x, y, taille) dans un cadre
# de 1200 × 800. Chaque écran en met quelques-uns en avant (José, 30 octobre).
CONSTELLATION = {
    "Saint-Pierre-et-Miquelon": (70, 40, 105), "Saint-Martin": (250, 95, 70), "Saint-Barthélemy": (345, 140, 55),
    "Guadeloupe": (95, 225, 150), "Martinique": (290, 280, 110), "Guyane": (120, 470, 190),
    "Mayotte": (555, 95, 105), "La Réunion": (500, 300, 150), "TAAF": (585, 530, 175),
    "Clipperton": (860, 60, 55), "Polynésie française": (985, 150, 175), "Wallis-et-Futuna": (820, 360, 110),
    "Nouvelle-Calédonie": (900, 545, 225),
}


@st.cache_data(show_spinner=False)
def _svg_fond(en_avant):
    from urllib.parse import quote
    from charte import BLEU_GRIS, VERT, teinte
    K = lire("territoires_contours.csv")
    formes, noms = [], []
    for t, (x0, y0, s) in CONSTELLATION.items():
        T = K[K.territoire == t]
        fort = t in en_avant
        trait = VERT if fort else BLEU_GRIS
        style = (f'fill="{teinte(VERT, 0.18)}" stroke="{trait}" stroke-opacity="0.75" stroke-width="1.6"' if fort else
                 f'fill="{teinte(BLEU_GRIS, 0.06)}" stroke="{trait}" stroke-opacity="{0.5 if not en_avant else 0.32}" '
                 f'stroke-width="1.1"')
        for _, P in T.groupby("partie"):
            pts = " ".join(f"{x0 + x * s:.1f},{y0 + y * s:.1f}" for x, y in zip(P.x, P.y))
            formes.append(f'<polygon points="{pts}" {style}/>')
        op = 0.9 if fort else (0.55 if not en_avant else 0.35)
        noms.append(f'<text x="{x0 + T.x.max() * s / 2:.0f}" y="{y0 + T.y.max() * s + 16:.0f}" fill="{trait}" '
                    f'fill-opacity="{op}" font-weight="{700 if fort else 400}">{t.upper()}</text>')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><g stroke-linejoin="round">' +
           "".join(formes) + '</g><g font-family="Lato, sans-serif" font-size="9.5" letter-spacing="1.4" '
           'text-anchor="middle">' + "".join(noms) + "</g></svg>")
    # sur un écran étroit, le fond est recadré : on le centre sur les territoires mis en avant
    if en_avant:
        cx = sum(CONSTELLATION[t][0] + CONSTELLATION[t][2] / 2 for t in en_avant) / len(en_avant) / 1200
        cy = sum(CONSTELLATION[t][1] + CONSTELLATION[t][2] / 2 for t in en_avant) / len(en_avant) / 800
    else:
        cx = cy = 0.5
    return "data:image/svg+xml;utf8," + quote(svg), round(100 * cx), round(100 * cy)


@st.cache_data(show_spinner=False)
def silhouette(territoire, taille=46, couleur="#465D6C"):
    """Le contour réel d'un territoire (Natural Earth), en SVG en ligne, dans un carré de `taille` pixels."""
    from charte import teinte
    K = lire("territoires_contours.csv")
    T = K[K.territoire == territoire]
    if T.empty:
        return ""
    w, h = T.x.max(), T.y.max()
    # archipels étendus : à cette taille leurs îles ne seraient que des points ; un trait épais les rend visibles
    trait = 0.07 if territoire in ("Polynésie française", "Wallis-et-Futuna", "TAAF") else 0.022
    formes = "".join(
        '<polygon points="' + " ".join(f"{x:.4f},{y:.4f}" for x, y in zip(P.x, P.y)) + '"/>'
        for _, P in T.groupby("partie"))
    return (f'<svg viewBox="-0.04 -0.04 {w + 0.08:.3f} {h + 0.08:.3f}" width="{taille}" height="{taille}" '
            f'preserveAspectRatio="xMidYMid meet" style="flex:0 0 auto" aria-hidden="true">'
            f'<g fill="{teinte(couleur, 0.22)}" stroke="{couleur}" stroke-width="{trait}" stroke-linejoin="round">'
            f'{formes}</g></svg>')


def fond(en_avant=(), voile=0.70):
    """Le fond de l'écran : dégradé clair et contours des territoires, `en_avant` soulignés en vert."""
    url, px, py = _svg_fond(tuple(en_avant))
    st.markdown(f"""<style>
    .stApp {{ background: url("{url}") {px}% {py}% / cover no-repeat fixed,
                          linear-gradient(165deg, #FFFFFF 0%, #F7F3EC 55%, #EEF2F3 100%) fixed; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    /* un voile blanc sous le contenu : les territoires restent visibles autour, le texte reste lisible */
    .block-container {{ background: rgba(255,255,255,{voile}); backdrop-filter: blur(1.5px);
                        padding-left: 2rem; padding-right: 2rem; }}
    @media (max-width: 640px) {{ .block-container {{ padding-left: 1rem; padding-right: 1rem; }} }}
    </style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def lire(nom):
    return pd.read_csv(os.path.join(DONNEES, nom), sep=";", decimal=",", encoding="utf-8-sig")


def telecharger(col, libelle, fichier, figure=False):
    """Un bouton de téléchargement : une figure-phare (PNG) ou les données (CSV)."""
    chemin = os.path.join(FIGURES if figure else DONNEES, fichier)
    with open(chemin, "rb") as f:
        col.download_button(libelle, f.read(), file_name=fichier,
                            mime="image/png" if figure else "text/csv", width="stretch")
