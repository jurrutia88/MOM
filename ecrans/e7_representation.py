# -*- coding: utf-8 -*-
"""Écran 7 — Comment les outre-mer sont-ils représentés ?

Sièges : onglet E7 du socle (Code électoral, 17e législature). Populations : décret n° 2025-1362 (INSEE) et
instituts des collectivités. Lecture politique reprise de la fiche variable V4 (« Représentativité », v4),
sections 2.1 et 2.2 — sans la ventilation par groupe, qui totalise 28 députés au lieu de 27 dans la fiche.
"""
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import carte, deux_lignes, entete, fr, lire, pied, telecharger, tuile

RENVOI = "partie « Comment fonctionne le ministère »"       # intitulé définitif à caler sur le rapport

c.css()
S = lire("representation_sieges.csv")
S["libelle"] = S.territoire.map(deux_lignes)
K = lire("representation_chiffres.csv").set_index("indicateur").valeur
moy = K["Population des onze territoires habités"] / K["Sièges de députés des outre-mer"]
mini, maxi = S.loc[S.habitants_par_depute.idxmin()], S.loc[S.habitants_par_depute.idxmax()]
SIEGES_OM = K["Sièges de députés des outre-mer"]
SIEGES_AN = K["Sièges de l'Assemblée nationale"]

entete("Écran 7 · La représentation", "Comment les outre-mer sont-ils représentés ?",
       "À l'Assemblée nationale, des sièges proportionnés à la population d'ensemble, mais très inégalement "
       "répartis entre territoires. Et, selon les majorités, un poids qui change du tout au tout.")

t = st.columns(4)
tuile(t[0], f"{SIEGES_OM:.0f} sur {SIEGES_AN:.0f}",
      f"sièges de députés, soit {fr(K['Part des sièges (%)'], 2)} % de l'Assemblée nationale")
tuile(t[1], f"≈ {fr(K['Part de la population (%)'])} %", "de la population de la France vit dans les outre-mer",
      "bleugris")
tuile(t[2], f"{fr(maxi.habitants_par_depute, 0)}", f"habitants par député à {maxi.territoire}, contre "
      f"{fr(mini.habitants_par_depute, 0)} à {mini.territoire}", "orange")
tuile(t[3], "10 députés", "ultramarins ont permis la formation du groupe de la Gauche démocrate et républicaine, "
      "en 2022", "bleu")
st.markdown("")

# ───────────────────────────────────────── 1 · les sièges et la population
st.markdown("### Combien d'habitants pour un député ?")
g, d = st.columns([1.65, 1], gap="large")
with g:
    vue = st.radio("Afficher", ["Habitants par député", "Nombre de députés"], horizontal=True,
                   label_visibility="collapsed")
    if vue == "Habitants par député":
        T = S.sort_values("habitants_par_depute")
        x, txt, titre = (T.habitants_par_depute / 1000, [f"{fr(v, 0)}" for v in T.habitants_par_depute],
                         "Habitants par député (milliers)")
        coul = [c.ORANGE if t_ == maxi.territoire else c.BLEU_GRIS for t_ in T.territoire]
    else:
        T = S.sort_values("deputes")
        x, txt, titre = (T.deputes, [f"{v} · {fr(p, 0)} hab." for v, p in zip(T.deputes, T.population)],
                         "Nombre de députés")
        coul = [c.BLEU_GRIS] * len(T)
    fig = go.Figure(go.Bar(y=T.libelle, x=x, orientation="h", marker=dict(color=coul, line=dict(width=0)),
                           text=txt, textposition="outside", cliponaxis=False, textfont=dict(size=12, color=c.MARINE),
                           hovertemplate="<b>%{y}</b> : %{text}<extra></extra>"))
    if vue == "Habitants par député":
        fig.add_vline(x=moy / 1000, line=dict(color=c.VERT, width=2, dash="dash"), layer="below")
        fig.add_annotation(x=moy / 1000, y=1.0, yref="paper", yanchor="bottom", showarrow=False,
                           text=f"<b>moyenne des outre-mer : {fr(moy, 0)}</b>", font=dict(size=12, color=c.VERT))
    fig.update_layout(height=500, margin=dict(r=60, t=34),
                      xaxis=dict(title=titre, range=[0, x.max() * 1.45], showgrid=True, gridcolor=c.GRILLE, nticks=4),
                      yaxis=dict(showgrid=False, tickfont=dict(size=12, color=c.MARINE)))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          [f"à l'échelle des outre-mer, la représentation est proportionnée : {fr(K['Part des sièges (%)'], 2)} % "
           f"des sièges pour environ {fr(K['Part de la population (%)'])} % de la population.",
           f"Mais d'un territoire à l'autre, un député représente de {fr(mini.habitants_par_depute, 0)} habitants "
           f"({mini.territoire}) à {fr(maxi.habitants_par_depute, 0)} ({maxi.territoire}) : près de "
           f"{fr(maxi.habitants_par_depute / mini.habitants_par_depute, 0)} fois plus."], "orange")
    carte("À lire avec prudence",
          ["Les populations n'ont pas toutes la même date : 2023 pour la métropole et les départements des "
           "Antilles, de Guyane et de La Réunion, 2026 pour Mayotte, de 2022 à 2025 pour les collectivités du "
           "Pacifique. La part de population est donc un ordre de grandeur.",
           "Saint-Martin et Saint-Barthélemy partagent un seul député."], "bleugris")
pied("Code électoral (17e législature) ; Assemblée nationale ; décret n° 2025-1362 du 26 décembre 2025 (INSEE, "
     "populations au 1er janvier 2023) ; INSEE (Mayotte, 2026) ; ISEE (2025) ; ISPF (2022) ; STSEE (2023)",
     statut="Estimé", renvoi=RENVOI)

# ───────────────────────────────────────── 2 · le poids politique
st.markdown("### Peu nombreux, parfois décisifs")
a, b = st.columns(2, gap="large")
carte("Un poids qui dépend des majorités",
      ["La représentation ultramarine est numériquement restreinte mais politiquement influente lorsque les "
       "majorités sont étroites.",
       "Avec une majorité absolue confortable — les deux quinquennats de Jacques Chirac, le premier d'Emmanuel "
       "Macron —, les députés ultramarins pèsent peu. Sans majorité absolue, depuis 2022, leur poids devient "
       "stratégique."], "orange", a)
carte("Un groupe qui existe grâce à eux",
      ["Le groupe de la Gauche démocrate et républicaine doit son existence aux dix députés ultramarins qui en sont "
       "membres : sans eux, il n'atteindrait pas les quinze députés nécessaires pour former un groupe.",
       "Depuis la dissolution de 2024, ils en sont la moitié — un point d'appui pour des majorités sur les "
       "questions ultramarines, mais aussi sur la sécurité sociale, l'écologie ou le budget."], "bleu", b)
carte("Mais dispersés",
      ["Les 27 députés se répartissent entre plusieurs groupes politiques, sans coordination systématique : ils "
       "pèsent rarement en bloc sur les grandes décisions."], "bleugris")
pied("Fiche variable V4, « Représentativité politico-territoriale », v4 (2026) : Assemblée nationale, composition "
     "des groupes et de la délégation aux outre-mer (16e et 17e législatures)", renvoi=RENVOI)

# ───────────────────────────────────────── 3 · et dans l'administration
st.markdown("### Et dans l'administration ?")
g, d = st.columns([1.65, 1], gap="large")
with g:
    carte("Les directeurs généraux des outre-mer",
          ["Les directeurs généraux successifs de l'administration centrale du ministère ont un profil très "
           "homogène : haut fonctionnaire issu de l'ENA, carrière préfectorale, passage par le ministère de "
           "l'Intérieur, sans ancrage biographique ultramarin.",
           "Le Sénat appelle à faire émerger une « élite administrative locale » : des cadres « qui les connaissent, "
           "qui s'y engagent, qui ne font pas que passer »."], "bleugris")
with d:
    carte("Les dispositifs de retour",
          ["Le concours national à affectation locale, lancé en 2020 : 46 concours, environ 1 800 postes par an — "
           "prometteur, mais marginal à l'échelle de la fonction publique ultramarine.",
           "Les ministres eux-mêmes : voir l'écran 3."], "orange")
pied("Fiche variable V4, v4 (2026) ; Sénat, rapport n° 264 (2025), Philippe Bas et Victorin Lurel, « L'action de "
     "l'État outre-mer : pour un choc régalien »", renvoi=RENVOI)

st.markdown("##### Télécharger")
telecharger(st.columns(2)[0], "Données · sièges et population par territoire", "representation_sieges.csv")
