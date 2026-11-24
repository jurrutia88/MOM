# -*- coding: utf-8 -*-
"""Écran 2 — Comment fonctionne le ministère aujourd'hui ?

Ses crédits (action par action, restes à payer) sont à l'écran 4, le budget (José, 30 octobre).

Textes repris du deck du diagnostic (23 septembre 2026), diapositives « D'où il vient » (attributions),
« Ce qu'il est » (organisation et coût) et « La mission Outre-mer », validés par José.
"""
import streamlit as st

import charte as c
from composants import carte, en_lettres, entete, fond, fr, glossaire, lire, pied, sigle, tuile

RENVOI = "partie « Comment fonctionne le ministère »"       # intitulé définitif à caler sur le rapport


c.css()
fond(["Saint-Pierre-et-Miquelon", "Wallis-et-Futuna"])
A = lire("fonctionnement_actions.csv")
K = lire("fonctionnement_chiffres.csv").set_index("indicateur").valeur
IND = lire("indicateurs.csv").set_index("indicateur")
SOUS_DIR = int(str(IND.valeur["Sous-directions DGOM"]).split(":")[0])         # « 4 : SDPEEDD, … »
CREATION = str(IND.millesime["DéGéOM → DGOM"]).split("/")[-1].strip()       # « 2008 / 2013 »
mission = A.cp_eur.sum()
part_contrainte = 100 * A.contraint_eur.sum() / mission

entete("Écran 2 · Le fonctionnement", "Comment fonctionne le ministère aujourd'hui ?",
       "Une petite administration, deux programmes budgétaires, et des attributions qui tiennent à un décret.")
glossaire(["DGOM", "P138", "P123", "CP"])

t = st.columns(4)
tuile(t[0], f"≈ {K['Agents de la direction générale des outre-mer']:.0f}",
      f"agents dans sa {sigle('DGOM', 'direction générale')}, répartis en {en_lettres(SOUS_DIR)} sous-directions")
tuile(t[1], f"{fr(mission / 1e9, 2)} Md€", "de crédits en propre en 2026, en deux programmes", "bleugris")
tuile(t[2], f"{fr(part_contrainte / 10, 0)} € sur 10", "de ces crédits sont engagés d'avance, par la loi ou par "
      "des dotations garanties", "orange")
tuile(t[3], f"{fr(K['Emplois du service militaire adapté'], 0)}", f"emplois du service militaire adapté, dont "
      f"{fr(K['dont volontaires'], 0)} volontaires : le seul plafond d'emplois de la mission", "bleu")
st.markdown("")

# ───────────────────────────────────────── 1 · l'organisation
st.markdown("### Une petite administration, payée par l'Intérieur")
g, d = st.columns([1.65, 1], gap="large")
with g:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:0;margin:6px 0 4px 0">
      <div style="background:linear-gradient(90deg,{c.MARINE},{c.BLEU_GRIS});color:#fff;font-weight:700;
                  padding:12px 26px;text-align:center;min-width:240px">Le ou la ministre des Outre-mer</div>
      <div style="width:2px;height:14px;background:{c.BLEU_GRIS}"></div>
    </div>
    <div style="margin:0 25%;height:2px;background:{c.BLEU_GRIS}"></div>
    <div style="display:flex;margin-bottom:2px">
      <div style="flex:1;display:flex;justify-content:center"><div style="width:2px;height:12px;background:{c.BLEU_GRIS}"></div></div>
      <div style="flex:1;display:flex;justify-content:center"><div style="width:2px;height:12px;background:{c.BLEU_GRIS}"></div></div>
    </div>""", unsafe_allow_html=True)
    o1, o2 = st.columns(2)
    carte("Le cabinet", [f"<b>{K['Membres du cabinet']:.0f} membres</b> et {K['Personnels support du cabinet']:.0f} "
                         "personnes en fonctions support, au 1er juillet 2025."], "vert", o1)
    carte("La direction générale", [f"<b>Environ {K['Agents de la direction générale des outre-mer']:.0f} "
                                    f"agents</b>, {en_lettres(SOUS_DIR)} sous-directions, créée en {CREATION}."], "vert", o2)
    carte(f"Ce que portent ses {en_lettres(SOUS_DIR)} sous-directions",
          ["Politiques économiques, de l'emploi et du développement durable.",
           "Politiques internationales, sociales et agricoles.",
           "Affaires juridiques et institutionnelles.",
           "Évaluation, prospective et dépense de l'État."], "bleugris")
with d:
    carte("Payé par l'Intérieur",
          ["Depuis 2012, une convention de gestion confie les personnels du ministère au programme 216 du "
           "ministère de l'Intérieur : sa masse salariale n'apparaît pas dans sa propre mission."], "orange")
    est, bas, haut = (K["Masse salariale cabinet + DGOM, estimation (€)"], K["Masse salariale, borne basse (€)"],
                      K["Masse salariale, borne haute (€)"])
    carte("Combien coûte son administration",
          [f"<b>≈ {fr(est / 1e6, 0)} M€ par an</b> pour le cabinet et la direction générale, hors cotisations de "
           f"retraite — entre {fr(bas / 1e6, 0)} et {fr(haut / 1e6, 0)} M€ selon la composition des effectifs.",
           "Effectifs du cabinet et de la direction générale, multipliés par les coûts moyens publiés par "
           "l'Intérieur pour chaque catégorie d'agent. Un ordre de grandeur, pas un montant comptable."], "bleu")
pied("Jaune « Personnels affectés dans les cabinets ministériels », PLF 2026 ; PAP 2026, programme 216 ; "
     "organigramme de la DGOM, mai 2026. Le coût de l'administration est une estimation", statut="Estimé",
     renvoi=RENVOI)

# ───────────────────────────────────────── 2 · les attributions
st.markdown("### Ce que le décret lui donne")
g, d = st.columns([1.65, 1], gap="large")
with g:
    carte("Ses attributions légales aujourd'hui",
          ["<b>Décret n° 2025-1018 du 29 octobre 2025.</b> Le ministre coordonne l'action du Gouvernement dans les "
           "départements et régions d'outre-mer ; il conduit la politique du Gouvernement à Saint-Barthélemy, "
           "Saint-Martin, Saint-Pierre-et-Miquelon, en Polynésie française, à Wallis-et-Futuna, dans les Terres "
           "australes et antarctiques et en Nouvelle-Calédonie ; il administre Clipperton.",
           "Il a autorité sur la direction générale des outre-mer, partage avec l'Intérieur l'autorité sur son "
           "secrétariat général, et ne dispose des autres administrations qu'« en tant que de besoin »."], "bleugris")
with d:
    carte("Ce que cela veut dire",
          ["<b>Le rang et le périmètre du ministère tiennent à un décret que le Premier ministre écrit seul, et "
           "qu'il réécrit à chaque gouvernement.</b>",
           "Ce qui s'obtient par décret se perd par décret : c'est la première fragilité du portefeuille."], "orange")
pied("Décret n° 2025-1018 du 29 octobre 2025 relatif aux attributions du ministre des Outre-mer (Légifrance)",
     renvoi=RENVOI)
