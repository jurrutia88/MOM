# -*- coding: utf-8 -*-
"""Écran 3 — Qui a dirigé le ministère des Outre-mer ?

Textes repris du deck du diagnostic (23 septembre 2026), diapositives « Les ministres » et
« Qui occupe le poste », validés par José. Règle d'ancrage du 17 septembre 2026 : seul compte
l'ancrage antérieur à la nomination ; « autre forme » jamais confondue avec la naissance.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import carte, entete, fr, glossaire, lire, pied, sigle, telecharger, tuile

RENVOI = "partie « Rôle et histoire du ministère »"        # intitulé définitif à caler sur le rapport
SOURCE = "Journal officiel — base des 63 mandats arrêtée au 23 juin 2026"

c.css()
M = lire("ministres_mandats.csv")
P = lire("ministres_presidents.csv")
PRES = list(P.president)
# libellés courts : huit colonnes doivent tenir sur un téléphone
LIB = [f"{p.replace(' d' + chr(39) + 'Estaing', '')}<br>{a}-{str(int(b))[2:]}" if pd.notna(b)
       else f"{p}<br>depuis {a}" for p, a, b in zip(P.president, P.debut, P.fin)]

n, pers = len(M), M.ministre.nunique()
moy, med = M.duree_jours.mean(), M.duree_jours.median()
courts = int((M.duree_jours < 183).sum())
nes = M[M.ancrage == "né outre-mer"]

entete("Écran 3 · Les ministres", "Qui a dirigé le ministère des Outre-mer ?",
       f"{pers} personnes et {n} mandats depuis 1959. Combien de temps elles restent, à quel rang, et qui elles sont.")

t = st.columns(4)
tuile(t[0], f"{pers}", f"ministres depuis 1959, pour <b>{n} mandats</b> : une même personne peut être nommée "
      f"dans plusieurs gouvernements")
tuile(t[1], f"{fr(moy, 0)} jours", f"durée moyenne d'un mandat, soit environ 13 mois — la moitié dure moins de "
      f"{fr(med, 0)} jours", "bleugris")
tuile(t[2], "1 sur 3", f"des mandats dure moins de six mois ({courts} sur {n})", "orange")
tuile(t[3], f"{nes.ministre.nunique()}", "ministres nés outre-mer en 67 ans, tous entre 2009 et 2017 — "
      "aucun depuis", "orange")
st.markdown("")

# ───────────────────────────────────────── 1 · un portefeuille qui tourne
st.markdown("### Un portefeuille qui tourne de plus en plus vite")
g, d = st.columns([1.65, 1], gap="large")
RANGS = [("Ministre d'État", c.MARINE), ("Ministre", c.VERT), ("Ministre délégué", "#93B3C8"),
         ("Secrétaire d'État", "#D8C6A6")]
with g:
    vue = st.radio("Afficher", ["Les mandats, par rang", "La durée moyenne", "Le rythme des nominations"],
                   horizontal=True, label_visibility="collapsed")
    # présidents en lignes, du plus ancien en haut : huit colonnes ne tiennent pas sur un téléphone
    fig = go.Figure()
    if vue == "Les mandats, par rang":
        # une case par mandat, empilées par rang ; le survol nomme le ministre
        for rang, coul in RANGS:
            S = M[M.rang == rang]
            fig.add_trace(go.Bar(
                y=[LIB[PRES.index(p)] for p in S.president], x=[1] * len(S), name=rang, orientation="h",
                marker=dict(color=coul, line=dict(color="#FFFFFF", width=1.5)),
                customdata=S[["ministre", "gouvernement", "duree_jours"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>" + rang + " · %{customdata[1]}<br>"
                              "%{customdata[2]} jours<extra></extra>"))
        for i, row in P.iterrows():
            fig.add_annotation(y=LIB[i], x=row.mandats, text=f"<b>{row.mandats}</b>", xshift=14,
                               showarrow=False, font=dict(size=14, color=c.MARINE))
        fig.update_layout(barmode="stack", xaxis=dict(range=[0, 15], showgrid=False, showticklabels=False,
                                                      showline=False, title="mandats"))
    else:
        col, unite, titre, fmt = (("duree_moyenne_j", " j", "jours", lambda v: fr(v, 0)) if vue == "La durée moyenne"
                                  else ("mandats_par_an", "", "mandats par année de présidence", lambda v: fr(v, 2)))
        coul = [c.ORANGE if p == "Macron" else c.BLEU_GRIS for p in PRES]
        fig.add_trace(go.Bar(y=LIB, x=P[col], orientation="h", marker=dict(color=coul, line=dict(width=0)),
                             width=0.6, text=[f"<b>{fmt(v)}{unite}</b>" for v in P[col]], textposition="outside",
                             cliponaxis=False, textfont=dict(size=13, color=coul),
                             hovertemplate="%{x}" + unite + "<extra></extra>"))
        fig.update_layout(xaxis=dict(title=titre, range=[0, P[col].max() * 1.25], showgrid=True,
                                     gridcolor=c.GRILLE), showlegend=False)
    fig.update_layout(height=470, bargap=0.28, margin=dict(r=24),
                      yaxis=dict(tickfont=dict(size=12, color=c.MARINE), showgrid=False,
                                 categoryorder="array", categoryarray=LIB[::-1]),
                      legend=dict(traceorder="normal", orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True, config=c.CONFIG)
with d:
    mac = P[P.president == "Macron"].iloc[0]
    carte("Ce graphique montre que…",
          [f"sous Emmanuel Macron, le portefeuille change de titulaire plus vite que jamais : {mac.mandats} "
           f"mandats et {mac.ministres} ministres en neuf ans, {fr(mac.mandats_par_an, 2)} mandat par année de "
           f"présidence — le rythme le plus rapide de la Ve République.",
           f"La durée moyenne tombe à {mac.duree_moyenne_j} jours, contre 634 sous Valéry Giscard d'Estaing."],
          "orange")
    carte("Le rang et le rattachement oscillent aussi",
          [f"Neuf mandats de ministre d'État, trente de ministre, sept de ministre délégué, dix-sept de "
           f"secrétaire d'État ; depuis 2012, plus aucun secrétaire d'État.",
           f"48 mandats sur 63 sont de plein exercice ; quinze sont "
           f"{sigle('rattaché à l' + chr(39) + 'Intérieur', 'rattachés à l’Intérieur')} — 1976-1986, "
           f"2000-2002, 2007-2012, 2022-2024. Les deux premiers {sigle('rang', 'rangs')} siègent au Conseil des "
           f"ministres ; les deux autres passent par le ministre dont ils relèvent."], "bleu")
pied(SOURCE + ". Un mandat = une nomination dans un gouvernement ; 2022-2024 : deux titulaires simultanés",
     renvoi=RENVOI)

# ───────────────────────────────────────── 2 · qui occupe le poste
st.markdown("### Qui occupe le poste ?")
g, d = st.columns([1.65, 1], gap="large")
ANCRAGE = {"né outre-mer": c.ORANGE, "autre forme": "#A08F76", "aucun": "#E2DDD4"}
with g:
    # une ligne par président, une case par mandat dans l'ordre chronologique
    M = M.sort_values("debut")
    pos = {}
    for p in PRES:
        for k, idx in enumerate(M[M.president == p].index):
            pos[idx] = (k + 1, LIB[PRES.index(p)])
    M["x"] = [pos[i][0] for i in M.index]
    M["y"] = [pos[i][1] for i in M.index]
    fig = go.Figure()
    for anc, coul in ANCRAGE.items():
        S = M[M.ancrage == anc]
        fig.add_trace(go.Scatter(
            x=S.x, y=S.y, mode="markers", name=anc if anc != "aucun" else "aucun ancrage",
            marker=dict(symbol="square", size=17, color=coul, line=dict(width=0)),
            customdata=S[["ministre", "fonction", "duree_jours"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} jours<extra></extra>"))
    F = M[M.sexe == "F"]
    fig.add_trace(go.Scatter(x=F.x, y=F.y, mode="markers", name="une femme", hoverinfo="skip",
                             marker=dict(symbol="circle", size=6, color=c.MARINE,
                                         line=dict(color="#FFFFFF", width=1))))
    fig.update_layout(height=430, xaxis=dict(range=[0.3, 13.7], showgrid=False, showline=False,
                                             showticklabels=False),
                      yaxis=dict(showgrid=False, showline=False, tickfont=dict(size=12, color=c.MARINE),
                                 categoryorder="array", categoryarray=LIB[::-1]),
                      legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True, config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          ["aucune femme et aucun ministre lié à l'outre-mer avant 2002. Les quatre ministres nés outre-mer se "
           "succèdent tous entre 2009 et 2017, sous des majorités de droite puis de gauche ; depuis, plus aucun.",
           "Les femmes restent présentes, mais leur part recule : 67 % des mandats sous François Hollande, 38 % "
           "depuis."], "orange")
    carte("Ce que ces dates suivent",
          ["<b>2002</b> — la première femme, Brigitte Girardin, arrive deux ans après la loi sur la parité, un an "
           "après la loi Taubira et la loi du 16 novembre 2001 contre les discriminations.",
           "<b>2009</b> — la première ministre née outre-mer, Marie-Luce Penchard, est nommée un mois après le "
           "décret du 27 mai 2009 qui clôt la grève générale de Guadeloupe, cinquante ans après la création du "
           "portefeuille.",
           "<b>2017</b> — la parenthèse se ferme trois semaines après l'accord qui clôt le conflit guyanais.",
           "La coïncidence est de date, non de cause."], "bleugris")
with g:
    carte("Qui, et de quel ancrage",
          ["<b>Nés outre-mer</b> : Marie-Luce Penchard, Victorin Lurel, George Pau-Langevin, Ericka Bareigts.",
           f"<b>Autre forme d'{sigle('ancrage')}</b> : Brigitte Girardin, Annick Girardin, Jean-François Carenco — "
           "activité, enfance ou fonctions outre-mer antérieures à la nomination."], "bleu")
pied(SOURCE + " ; grille d'ancrage ultramarin du CLSE, v4 (naissance, ascendance, résidence, activité, mandat, "
     "engagement)", renvoi=RENVOI)

# ───────────────────────────────────────── 3 · retrouver un ministre
st.markdown("### Retrouver un ministre")
choix = st.selectbox("Présidence", ["Toutes les présidences"] + PRES, label_visibility="collapsed")
T = M if choix.startswith("Toutes") else M[M.president == choix]
T = T.sort_values("debut", ascending=False)
st.dataframe(pd.DataFrame({
    "Ministre": T.ministre, "Fonction": T.fonction, "Gouvernement": T.gouvernement,
    "Début": pd.to_datetime(T.debut).dt.strftime("%d/%m/%Y"), "Fin": pd.to_datetime(T.fin).dt.strftime("%d/%m/%Y"),
    "Jours": T.duree_jours, "Ancrage": T.ancrage}), hide_index=True, use_container_width=True,
    height=min(38 + 35 * len(T), 420))
pied(SOURCE + ". Fin du dernier mandat : date d'arrêt de la base, la ministre étant toujours en fonction")

glossaire(["mandat", "rang", "rattaché à l'Intérieur", "ancrage"])
st.markdown("##### Télécharger")
b = st.columns(3)
telecharger(b[0], "Figure · mandats par président", "mandats_par_president.png", figure=True)
telecharger(b[1], "Figure · qui occupe le poste", "representativite_des_ministres.png", figure=True)
telecharger(b[2], "Données · les 63 mandats", "ministres_mandats.csv")
