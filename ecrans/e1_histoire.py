# -*- coding: utf-8 -*-
"""Écran 1 — D'où vient le ministère des Outre-mer ?

Jalons de l'onglet E1 du socle, complétés par la frise du deck du diagnostic (diapositive « D'où il vient »,
validée). Un jalon qui ne s'appuie pas sur un texte (loi, décret) est marqué « source secondaire ».
"""
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import carte, entete, fr_typo, glossaire, lire, pied, sigle, tuile

RENVOI = "partie « Rôle et histoire du ministère »"        # intitulé définitif à caler sur le rapport

c.css()
J = lire("histoire_jalons.csv")
M = lire("ministres_mandats.csv")

entete("Écran 1 · L'histoire", "D'où vient le ministère des Outre-mer ?",
       "Un héritage colonial, un statut qui oscille : de 1894 à 2025, le portefeuille change de nom, de rang et de "
       "tutelle.")
glossaire(["rang", "rattaché à l'Intérieur", "mandat", "DGOM"])

t = st.columns(4)
tuile(t[0], "1894", "un ministère des Colonies sort de la tutelle de la Marine")
tuile(t[1], "1946", "la Guadeloupe, la Martinique, la Guyane et La Réunion deviennent des départements", "bleugris")
tuile(t[2], "4 périodes", f"où le portefeuille est {sigle('rattaché à l' + chr(39) + 'Intérieur')}", "orange")
tuile(t[3], "1 décret", "fixe aujourd'hui son périmètre, et le Premier ministre le réécrit à chaque gouvernement",
      "orange")
st.markdown("")

# ───────────────────────────────────────── 1 · la frise
st.markdown("### De la Marine au ministère des Outre-mer")
TYPES = {"Tout": None, "L'administration coloniale": ("colonial", "contexte"),
         "Le statut du portefeuille": ("statut", "intérieur"), "L'administration centrale": ("administration",)}
COUL = {"colonial": c.BRUN, "contexte": "#A3ABB2", "statut": c.MARINE, "intérieur": c.ORANGE,
        "administration": c.VERT}
g, d = st.columns([1.65, 1], gap="large")
with g:
    choix = st.radio("Afficher", list(TYPES), horizontal=True, label_visibility="collapsed")
    S = J if TYPES[choix] is None else J[J.type.isin(TYPES[choix])]
    items = []
    for j in S.itertuples():
        coul = c.VERT if j.annee == 2025 else COUL[j.type]
        sec = (f' <span style="font-style:normal;font-size:.68rem;letter-spacing:.05em;text-transform:uppercase;'
               f'border:1px solid {c.FILET};padding:0 5px;color:{c.GRIS}">source secondaire</span>'
               if j.statut != "Confirmé" else "")
        items.append(f"""
        <div style="display:flex;gap:14px;align-items:flex-start;position:relative;padding-bottom:16px">
          <div style="flex:0 0 14px;display:flex;flex-direction:column;align-items:center;align-self:stretch">
            <div style="width:14px;height:14px;border-radius:50%;background:{coul};border:2px solid #fff;
                        box-shadow:0 0 0 1px {coul};margin-top:3px"></div>
            <div style="flex:1;width:2px;background:{c.GRILLE};margin-top:2px"></div>
          </div>
          <div style="min-width:0">
            <div style="font-weight:700;color:{coul};font-size:1.02rem">{escape(fr_typo(j.date))}</div>
            <div style="font-weight:700;color:{c.MARINE};margin:1px 0 3px 0">{escape(fr_typo(j.fait))}</div>
            <div style="color:{c.MARINE};font-size:.94rem;line-height:1.5">{escape(fr_typo(j.explication))}</div>
            <div style="color:{c.GRIS};font-size:.78rem;font-style:italic;margin-top:3px">
              {escape(fr_typo(j.source))}{sec}</div>
          </div>
        </div>""")
    st.markdown("<div>" + "".join(items) + "</div>", unsafe_allow_html=True)
with d:
    carte("Ce que cette frise montre",
          ["le ministère des Outre-mer descend d'une administration coloniale : d'abord un service de la Marine, "
           "puis un ministère des Colonies en 1894.",
           "Sous la Ve République, le portefeuille change de nom, de rang et de tutelle — il est rattaché à "
           "l'Intérieur pendant quatre périodes. Depuis 2025, il est de plein exercice, mais par un décret que le "
           "Premier ministre écrit seul."], "orange")
    carte("Ce que cela veut dire",
          ["<b>Ce qui s'obtient par décret se perd par décret</b> : c'est la première fragilité du portefeuille."],
          "bleugris")
    carte("Sur les sources",
          ["Les jalons fondés sur un texte — loi, décret — sont confirmés. Ceux qui reposent sur des travaux "
           "d'histoire ou des ouvrages de référence sont signalés « source secondaire »."], "marine")
pied("Décret du 20 mars 1894 ; loi n° 46-451 du 19 mars 1946 ; décrets n° 2008-687, n° 2013-728 et n° 2025-1018 ; "
     "base des 63 mandats (Journal officiel) ; sources secondaires signalées jalon par jalon", renvoi=RENVOI)

# ───────────────────────────────────────── 2 · le statut, mandat après mandat
st.markdown("### Un statut qui oscille, mandat après mandat")
g, d = st.columns([1.65, 1], gap="large")
RANGS = ["Ministre d'État", "Ministre", "Ministre délégué", "Secrétaire d'État"]
with g:
    fig = go.Figure()
    for ratt, coul in (("plein exercice", c.BLEU_GRIS), ("rattaché à l'Intérieur", c.ORANGE)):
        S = M[M.rattachement == ratt]
        debut, fin = pd.to_datetime(S.debut), pd.to_datetime(S.fin)
        fig.add_trace(go.Bar(
            y=S.rang, base=debut, x=(fin - debut).dt.total_seconds() * 1000, orientation="h", name=ratt,
            marker=dict(color=coul, line=dict(color="#FFFFFF", width=0.6)), width=0.62,
            customdata=S[["ministre", "gouvernement", "duree_jours"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]} jours<extra></extra>"))
    fig.update_layout(height=330, barmode="overlay",
                      xaxis=dict(type="date", range=["1958-06-01", "2027-01-01"], dtick="M120", tickformat="%Y",
                                 showgrid=True, gridcolor=c.GRILLE),
                      yaxis=dict(categoryorder="array", categoryarray=RANGS[::-1], showgrid=False,
                                 tickfont=dict(size=12, color=c.MARINE)),
                      legend=dict(orientation="h", y=1.04, yanchor="bottom"))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          [f"le {sigle('rang', 'rang')} du portefeuille monte et descend au gré des gouvernements : ministre d'État "
           "sous de Gaulle, secrétaire d'État sous Valéry Giscard d'Estaing et François Mitterrand, ministre depuis "
           "2012 — plus aucun secrétaire d'État depuis —, de nouveau ministre d'État avec Manuel Valls, neuf jours "
           "après le cyclone Chido.",
           "En orange, les mandats rattachés à l'Intérieur : 1976-1986, 2000-2002, 2007-2012, 2022-2024."], "orange")
    carte("En chiffres",
          ["Sur 63 mandats : neuf de ministre d'État, trente de ministre, sept de ministre délégué, dix-sept de "
           "secrétaire d'État.",
           "48 sont de plein exercice, quinze rattachés à l'Intérieur. Les deux premiers rangs siègent au Conseil des "
           "ministres ; les deux autres passent par le ministre dont ils relèvent."], "bleu")
pied("Journal officiel — base des 63 mandats arrêtée au 23 juin 2026. Une barre = un mandat, de la nomination "
     "à la fin des fonctions", renvoi=RENVOI)

