# -*- coding: utf-8 -*-
"""Écran 5 — Pourquoi les 13 outre-mer n'ont-ils pas tous le même statut ?

Statuts et régimes européens : onglet E5 du socle. Explications reprises de la fiche variable V5
(« Diversité institutionnelle », v4, socle 2026), sections 1.3 et 2.1.
"""
from html import escape

import streamlit as st

import charte as c
from composants import carte, entete, fr_typo, glossaire, lire, pied, sigle, tuile

RENVOI = "partie « Comment fonctionne le ministère »"       # intitulé définitif à caler sur le rapport

c.css()
S = lire("statuts.csv")

entete("Écran 5 · Les statuts", "Pourquoi les 13 outre-mer n'ont-ils pas tous le même statut ?",
       "Trois régimes constitutionnels, deux statuts particuliers, deux régimes européens : un même ministère pour "
       "des territoires que le droit ne traite pas de la même façon.")

t = st.columns(4)
tuile(t[0], "13", f"territoires, dont {int((S.habite == 'oui').sum())} habités — les TAAF et Clipperton n'ont pas "
      f"de population permanente")
tuile(t[1], "3 régimes", f"dans la Constitution : {sigle('article 73')}, {sigle('article 74')}, titre XIII — plus "
      f"deux statuts particuliers", "bleugris")
tuile(t[2], f"{int((S.regime_europeen == 'RUP').sum())} sur 13", f"font partie de l'Union européenne ({sigle('RUP')}) ; "
      f"{int((S.regime_europeen == 'PTOM').sum())} y sont seulement associés ({sigle('PTOM')})", "bleu")
tuile(t[3], "21 ans", f"avant le premier projet de loi d'{sigle('habilitation')} dédié, pour la Martinique, en 2024",
      "orange")
st.markdown("")

# ───────────────────────────────────────── 1 · les treize territoires
st.markdown("### Treize territoires, rangés de trois façons")
COUL = {"Article 73": c.VERT, "Article 74": c.BLEU, "Titre XIII": c.MARINE, "Statut particulier": c.BRUN,
        "RUP": c.VERT, "PTOM": c.BLEU, "aucun": c.BRUN,
        "Atlantique": c.BLEU, "Indien": c.VERT, "Indien et austral": c.BRUN, "Pacifique": c.MARINE}
LIB = {"Article 73": "Article 73 — départements et régions d'outre-mer",
       "Article 74": "Article 74 — collectivités d'outre-mer",
       "Titre XIII": "Titre XIII — la Nouvelle-Calédonie, sui generis",
       "Statut particulier": "Statuts particuliers",
       "RUP": "Régions ultrapériphériques — dans l'Union européenne",
       "PTOM": "Pays et territoires d'outre-mer — associés à l'Union",
       "aucun": "Ni l'un ni l'autre",
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
        f'<div style="border:1px solid {c.GRILLE};border-left:3px solid {k};background:#fff;padding:7px 11px;'
        f'min-width:150px;flex:1 1 150px">'
        f'<div style="font-weight:700;color:{c.MARINE}">{escape(t.territoire)}</div>'
        f'<div style="font-size:.8rem;color:{c.GRIS};line-height:1.35">{escape(fr_typo(t.statut))}'
        f'{" · " + escape(t.regime_europeen) if t.regime_europeen != "aucun" else ""}'
        f'{"" if t.habite == "oui" else " · sans population permanente"}</div></div>'
        for t in T.itertuples())
    blocs.append(
        f'<div class="carte" style="background:linear-gradient(180deg,{c.teinte(k)} 0%,#fff 100%)">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{k},'
        f'{c.CLAIR.get(k, k)})"></div>'
        f'<div class="intitule" style="color:{k}">{escape(LIB[gr])} · {len(T)}</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:8px">{puces}</div></div>')
st.markdown("".join(blocs), unsafe_allow_html=True)
pied("Constitution, articles 72-3, 73, 74, 76 et 77 ; traité sur le fonctionnement de l'Union européenne, article 349 "
     "et annexe II ; loi n° 55-1052 (TAAF) ; loi du 21 février 2007 (Clipperton)", renvoi=RENVOI)

# ───────────────────────────────────────── 2 · ce que chaque régime change
st.markdown("### Ce que chaque régime change")
a, b, d = st.columns(3, gap="medium")
carte("Article 73 · l'identité législative",
      [f"Dans les cinq {sigle('DROM')}, les lois nationales s'appliquent de plein droit, sauf adaptation expresse.",
       f"Depuis 2003, une {sigle('habilitation')} permet à la collectivité de fixer elle-même les règles dans "
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
pied("Fiche variable V5, « Diversité institutionnelle », v4 (2026) : Constitution, code général des collectivités "
     "territoriales, rapports parlementaires", renvoi=RENVOI)

# ───────────────────────────────────────── 3 · un levier peu utilisé
st.markdown("### Un levier ouvert en 2003, resté sous-utilisé")
g, d = st.columns([1.65, 1], gap="large")
with g:
    st.markdown(f"""
    <div style="display:flex;align-items:stretch;gap:0;margin:8px 0 14px 0">
      <div style="flex:0 0 auto;text-align:center;padding:0 10px">
        <div style="font-size:1.9rem;font-weight:700;color:{c.MARINE}">2003</div>
        <div style="font-size:.85rem;color:{c.GRIS};max-width:150px">la Constitution ouvre l'habilitation</div></div>
      <div style="flex:1;display:flex;align-items:center;min-width:40px">
        <div style="flex:1;height:3px;background:linear-gradient(90deg,{c.MARINE},{c.ORANGE})"></div></div>
      <div style="flex:0 0 auto;text-align:center;padding:0 10px">
        <div style="font-size:1.9rem;font-weight:700;color:{c.ORANGE}">2024</div>
        <div style="font-size:.85rem;color:{c.GRIS};max-width:170px">premier projet de loi d'habilitation dédié,
        pour la Martinique</div></div>
    </div>""", unsafe_allow_html=True)
    carte("Ce que montre cette frise",
          ["Il faut vingt et un ans pour qu'un premier projet de loi d'habilitation dédié soit adopté par le Sénat, le "
           "31 mars 2024 : il autorise l'Assemblée de Martinique à fixer les règles en matière d'énergie, d'eau et "
           "d'assainissement.",
           "Trois raisons à cette sous-utilisation : une procédure lourde, que les collectivités « hésitent à "
           "utiliser » ; l'exclusion de La Réunion, qui ne laisse que quatre collectivités ; une lecture restrictive "
           "du Conseil constitutionnel."], "orange")
with d:
    carte("Et le ministère ?",
          ["Sa sous-direction des affaires juridiques prépare les textes et tient l'articulation entre les régimes.",
           "Mais aux moments décisifs — Matignon en 1988, Nouméa en 1998 — les accords ont été portés par le Premier "
           "ministre ou le président de la République. Bougival, en 2025, fait exception : le ministre d'État chargé "
           "des Outre-mer l'a signé."], "bleugris")
pied("Fiche variable V5, v4 (2026) ; rapport du Sénat n° 713 (2020) ; projet de loi d'habilitation pour la "
     "Martinique, adopté par le Sénat le 31 mars 2024", renvoi=RENVOI)

glossaire(["DROM", "COM", "article 73", "article 74", "habilitation", "sui generis", "RUP", "PTOM"])
