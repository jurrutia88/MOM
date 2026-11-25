# -*- coding: utf-8 -*-
"""Écran 5 — Pourquoi les 13 outre-mer n'ont-ils pas tous le même statut ?

Statuts et régimes européens : onglet E5 du socle. Explications reprises de la fiche variable V5
(« Diversité institutionnelle », v4, socle 2026), sections 1.3 et 2.1.
"""
from html import escape

import streamlit as st

import charte as c
from composants import chiffres_cles, carte, en_lettres, entete, fond, fr, fr_typo, glossaire, lire, pied, sigle, silhouette, tuile

RENVOI = "partie « Comment fonctionne le ministère »"       # intitulé définitif à caler sur le rapport

c.css()
fond(["Nouvelle-Calédonie", "Polynésie française", "Clipperton"])
S = lire("statuts.csv")
NB = len(S)
# quatre cadres constitutionnels : article 73, article 74, titre XIII, régimes particuliers (article 72-3)
CADRES = S.groupe.nunique()
PARTICULIERS = int((S.groupe == "Statut particulier").sum())
POP = lire("representation_chiffres.csv").set_index("indicateur").valeur["Population des onze territoires habités"]
EUROPE = S[S.regime_europeen != "aucun"].regime_europeen.nunique()  # RUP, PTOM
DROM = int((S.groupe == "Article 73").sum())
REVISION = 2003                          # révision constitutionnelle du 28 mars 2003

entete("Écran 5 · Les statuts", f"Pourquoi les {NB} outre-mer n'ont-ils pas tous le même statut ?",
       f"{en_lettres(CADRES).capitalize()} cadres dans la Constitution, {en_lettres(EUROPE)} régimes européens : un "
       f"même ministère pour des territoires que le droit ne traite pas de la même façon.")
glossaire(["DROM", "COM", "article 73", "article 74", "habilitation", "sui generis", "RUP", "PTOM"])

chiffres_cles()
t = st.columns(4)
HAB = int((S.habite == 'oui').sum())
tuile(t[0], f"{NB}", f"territoires, dont {HAB} habités — les TAAF et Clipperton n'ont pas de population permanente")
tuile(t[1], f"≈ {fr(POP / 1e6, 2)} millions", f"d'habitants dans les {HAB} territoires habités", "bleugris")
tuile(t[2], f"{CADRES} cadres", f"dans la Constitution : {sigle('article 73')}, {sigle('article 74')}, titre XIII "
      f"(Nouvelle-Calédonie) et régimes particuliers (TAAF, Clipperton)", "bleugris")
tuile(t[3], f"{int((S.regime_europeen == 'RUP').sum())} sur {NB}", f"font partie de l'Union européenne ({sigle('RUP')}) ; "
      f"{int((S.regime_europeen == 'PTOM').sum())} y sont seulement associés ({sigle('PTOM')})", "bleu")
st.markdown("")

# ───────────────────────────────────────── 1 · les treize territoires
st.markdown(f"### {en_lettres(NB).capitalize()} territoires, rangés de trois façons")
COUL = {"Article 73": c.VERT, "Article 74": c.BLEU, "Titre XIII": c.MARINE, "Statut particulier": c.BRUN,
        "RUP": c.VERT, "PTOM": c.BLEU, "aucun": c.BRUN,
        "Atlantique": c.BLEU, "Indien": c.VERT, "Indien et austral": c.BRUN, "Pacifique": c.MARINE}
LIB = {"Article 73": "Article 73 — départements et régions d'outre-mer",
       "Article 74": "Article 74 — collectivités d'outre-mer",
       "Titre XIII": "Titre XIII — la Nouvelle-Calédonie, sui generis",
       "Statut particulier": "Régimes particuliers — fixés par la loi (article 72-3)",
       "RUP": "Régions ultrapériphériques — dans l'Union européenne",
       "PTOM": "Pays et territoires d'outre-mer — associés à l'Union",
       "aucun": "Ni région ultrapériphérique, ni pays et territoire d'outre-mer",
       "Atlantique": "Atlantique et Caraïbes", "Indien": "Océan Indien", "Indien et austral": "Indien et austral",
       "Pacifique": "Pacifique"}
vue = st.radio("Ranger par", ["Statut dans la Constitution", "Régime européen", "Océan"], horizontal=True,
               label_visibility="collapsed")
col = {"Statut dans la Constitution": "groupe", "Régime européen": "regime_europeen", "Océan": "ocean"}[vue]
ordre = list(dict.fromkeys(S[col]))
blocs = []
for gr in ordre:
    T = S[S[col] == gr]
    k = COUL[gr]
    puces = "".join(
        f'<div style="border:1px solid {c.GRILLE};border-left:3px solid {k};background:#fff;padding:7px 10px;'
        f'min-width:170px;flex:1 1 170px;display:flex;gap:10px;align-items:center">'
        f'{silhouette(t.territoire, 46, k)}<div>'
        f'<div style="font-weight:700;color:{c.MARINE}">{escape(t.territoire)}</div>'
        f'<div style="font-size:.8rem;color:{c.GRIS};line-height:1.35">{escape(fr_typo(t.statut))}'
        f'{" · " + escape(t.regime_europeen) if t.regime_europeen != "aucun" else ""}'
        f'{"" if t.habite == "oui" else " · sans population permanente"}</div></div></div>'
        for t in T.itertuples())
    blocs.append(
        f'<div class="carte" style="background:linear-gradient(180deg,{c.teinte(k)} 0%,#fff 100%)">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{k},'
        f'{c.CLAIR.get(k, k)})"></div>'
        f'<div class="intitule" style="color:{k}">{escape(LIB[gr])} · {len(T)}</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:8px">{puces}</div></div>')
st.markdown("".join(blocs), unsafe_allow_html=True)
pied("Constitution, articles 72-3, 73, 74, 76 et 77 ; traité sur le fonctionnement de l'Union européenne, article 349 "
     "et annexe II ; loi n° 55-1052 (TAAF) ; loi du 21 février 2007 (Clipperton). Contours : Natural Earth, chaque "
     "territoire à sa propre échelle", renvoi=RENVOI)

# ───────────────────────────────────────── 2 · ce que chaque régime change
st.markdown("### Ce que chaque régime change")
a, b, d = st.columns(3, gap="medium")
carte("Article 73 · l'identité législative",
      [f"Dans les {en_lettres(DROM)} {sigle('DROM')}, les lois nationales s'appliquent de plein droit, sauf adaptation expresse.",
       f"Depuis {REVISION}, une {sigle('habilitation')} permet à la collectivité de fixer elle-même les règles dans "
       "quelques matières. La Réunion en est exclue par la Constitution elle-même."], "vert", a)
carte("Article 74 · la spécialité législative",
      [f"Chaque {sigle('COM')} a un statut sur mesure, fixé par une loi organique, et s'écarte plus largement de la "
       "législation nationale.",
       "La Polynésie française et Saint-Barthélemy disposent d'une autonomie substantielle — en Polynésie, une "
       "assemblée qui vote des lois du pays, un gouvernement, des compétences fiscales et douanières."], "bleu", b)
carte("Titre XIII · la Nouvelle-Calédonie",
      [f"Un statut {sigle('sui generis')}, qui inscrit dans la Constitution les accords de Matignon (1988) et de "
       "Nouméa (1998) : compétences transférées irréversibles, citoyenneté calédonienne, corps électoral "
       "spécifique.",
       "L'accord de Bougival (2025) devait s'y ajouter. Sa traduction constitutionnelle a été rejetée par "
       "l'Assemblée nationale le 2 avril 2026 : le cadre reste celui de Nouméa."], "marine", d)
a, b = st.columns(2, gap="medium")
carte("Régimes particuliers · les TAAF et Clipperton",
      ["Ces deux territoires n'ont pas de population permanente. La Constitution renvoie à la loi le soin de fixer "
       "leur régime (article 72-3).",
       "Les Terres australes et antarctiques françaises sont administrées par un préfet. Clipperton, île du "
       "Pacifique, est placée sous l'autorité directe du Gouvernement ; elle n'est ni région ultrapériphérique ni "
       "pays et territoire d'outre-mer de l'Union européenne."], "brun", a)
carte("Dépasser le couple des articles 73 et 74 ?",
      ["Plusieurs tentatives ont voulu ouvrir une autre voie. Le projet de révision constitutionnelle de 2018, qui "
       "élargissait la différenciation, n'a pas abouti. En mai 2022, l'appel de Fort-de-France des présidents "
       "d'exécutifs d'outre-mer a demandé une refondation de la relation avec l'État et un droit plus différencié.",
       "Pour la Nouvelle-Calédonie, l'accord de Bougival (2025) prévoyait un « État de la Nouvelle-Calédonie » ; "
       "adoptée par le Sénat, sa traduction constitutionnelle a été rejetée par l'Assemblée nationale le 2 avril "
       "2026, par la gauche et le Rassemblement national pour des raisons opposées.",
       "Pourquoi elles butent : toute sortie du cadre passe par une révision de la Constitution, donc par une "
       "majorité des trois cinquièmes du Parlement réuni en Congrès, ou par un référendum."], "orange", b)
pied("Fiche variable V5, « Diversité institutionnelle », v4.1 (2026) : Constitution, code général des collectivités "
     "territoriales, rapports parlementaires ; Assemblée nationale, séance du 2 avril 2026 ; loi n° 2007-224 du "
     "21 février 2007 (Clipperton)", renvoi=RENVOI)

