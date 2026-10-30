# -*- coding: utf-8 -*-
"""Écran 4 — Quel pouvoir budgétaire réel a le ministère ?

Textes repris du deck du diagnostic (23 septembre 2026), diapositives budget,
validés par José et par la présidente du CLSE (5,1 % « soit cinq euros sur cent »,
87 % « de l'effort passe par d'autres ministères »).
"""
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import (carte, entete, fr, glossaire, lire, pied, sigle, telecharger, tuile)

RENVOI = "partie « Comment fonctionne le ministère »"       # intitulé définitif à caler sur le rapport

c.css()

cas = lire("budget_cascade.csv")
dpt, mission, marge = cas.haut_eur[0], cas.haut_eur[2], cas.haut_eur[4]
p_mission, p_marge = 100 * mission / dpt, 100 * marge / dpt
contrib = lire("budget_contributeurs.csv")
serie = lire("budget_serie.csv")
fisc = lire("fiscal_serie.csv")

entete("Écran 4 · Le budget", "Quel pouvoir budgétaire réel a le ministère ?",
       "Ce que l'État consacre aux outre-mer, ce que le ministère en porte, et ce qu'il en décide vraiment. "
       "Tous les montants sont en crédits de paiement, l'argent effectivement dépensé dans l'année.")
glossaire(["DPT", "Mission Outre-mer", "P138", "P123", "LODEOM", "CP", "dépenses fiscales"])

# ───────────────────────────────────────── les quatre chiffres
t = st.columns(4)
tuile(t[0], f"{fr(dpt / 1e9, 2)} Md€", "consacrés par l'État aux outre-mer en 2026, tous ministères confondus")
tuile(t[1], f"{fr(p_mission)} %", "portés par le ministère des Outre-mer, soit 2,83 Md€", "bleugris")
tuile(t[2], f"{fr(p_marge)} %", "<b>soit cinq euros sur cent</b> : la part que le ministère décide réellement",
      "orange")
tuile(t[3], f"{fr(100 - p_mission, 0)} %", "de l'effort passe par d'autres ministères, qui le décident selon "
      "leurs propres règles", "orange")

st.markdown("")

# ───────────────────────────────────────── 1 · la cascade
st.markdown("### Sur 100 euros, combien le ministère en décide-t-il ?")
g, d = st.columns([1.65, 1], gap="large")
with g:
    # cascade horizontale, lue de haut en bas : cinq libellés ne tiennent pas côte à côte sur un téléphone
    couleurs = [c.MARINE, c.SABLE, c.BLEU_GRIS, c.SABLE, c.VERT]
    libelles = ["Effort total de l'État", "hors Mission Outre-mer", "Mission Outre-mer",
                "engagements contraints", "Marge réellement arbitrée"]
    fig = go.Figure()
    c.barres(fig, libelles, (cas.haut_eur - cas.bas_eur) / 1e9, couleurs, base=cas.bas_eur / 1e9, width=0.62,
             customdata=cas.part_dpt_pct, hover="%{x:.2f} Md€ · %{customdata:.1f} % de l'effort<extra></extra>")
    # les valeurs, au bout des barres pleines (le texte « outside » ne suit pas une base décalée)
    for i, (h, col) in enumerate(zip(cas.haut_eur, [c.MARINE, None, c.BLEU_GRIS, None, c.VERT])):
        if col:
            fig.add_annotation(y=libelles[i], x=h / 1e9, text=f"<b>{fr(h / 1e9, 2)}</b>", xanchor="left", xshift=6,
                               showarrow=False, font=dict(size=14, color=col))
    fig.add_annotation(y=libelles[4], x=marge / 1e9, text=f"<b>soit {fr(p_marge)} %</b>", xanchor="left",
                       xshift=46, showarrow=False, font=dict(size=18, color=c.ORANGE))
    fig.update_layout(height=380, margin=dict(r=12),
                      xaxis=dict(title="Md€ (crédits de paiement)", range=[0, 30], dtick=5, showgrid=True,
                                             gridcolor=c.GRILLE),
                      yaxis=dict(tickfont=dict(size=12, color=c.MARINE), showgrid=False,
                                 categoryorder="array", categoryarray=libelles[::-1]), bargap=0.3)
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          [f"sur 100 euros que l'État consacre aux outre-mer, le ministère en porte près de 13, et n'en "
           f"décide réellement que 5.",
           f"Le reste de sa {sigle('Mission Outre-mer', 'mission')} est engagé d'avance : la compensation "
           f"automatique des exonérations de charges ({sigle('LODEOM')}, 1,48 Md€) et la moitié des dotations "
           f"aux collectivités. Restent 1,12 Md€ que le ministère arbitre chaque année."], "orange")
    carte("Comment c'est calculé",
          [f"Mission Outre-mer 2,83 Md€ − compensation LODEOM 1,48 − moitié des dotations aux collectivités "
           f"0,23 = 1,12 Md€, rapportés aux 21,94 Md€ du {sigle('DPT')}.",
           "La moitié des dotations est une convention : elles sont en partie garanties par la loi."], "bleugris")
pied("DPT Outre-mer 2026, p. 10 ; PAP Mission Outre-mer 2026, récapitulation par action", renvoi=RENVOI)

# ───────────────────────────────────────── 2 · qui porte l'effort
st.markdown("### Qui porte l'effort de l'État outre-mer ?")
g, d = st.columns([1.65, 1], gap="large")
with g:
    # noms courts à l'écran (le téléphone n'a pas la place), nom officiel au survol
    COURT = {"Outre-mer": "Outre-mer (le ministère)",
             "Relations avec les collectivités territoriales": "Collectivités territoriales",
             "Solidarité, insertion et égalité des chances": "Solidarité",
             "Recherche et enseignement supérieur": "Recherche, enseignement sup.",
             "Gestion des finances publiques": "Finances publiques",
             "Écologie, développement et mobilité durables": "Écologie",
             "Administration générale et territoriale de l'État": "Administration territoriale",
             "Agriculture, alimentation, forêt et affaires rurales": "Agriculture"}
    seuil = 1.0
    grandes = contrib[contrib.part_pct >= seuil].sort_values("part_pct")
    petites = contrib[contrib.part_pct < seuil]
    noms = [f"Les {len(petites)} autres"] + [COURT.get(n, n) for n in grandes.mission]
    officiels = [f"{len(petites)} missions sous 1 %"] + list(grandes.mission)
    parts = [petites.part_pct.sum()] + list(grandes.part_pct)
    montants = [petites.cp_eur.sum()] + list(grandes.cp_eur)
    coul = [c.CLAIR[c.MARINE]] + [c.VERT if n == "Outre-mer" else c.MARINE for n in grandes.mission]
    fig = go.Figure()
    c.barres(fig, noms, parts, coul, text=[f"<b>{fr(p)} %</b>" for p in parts],
             textcolor=[c.VERT if "ministère" in n else c.MARINE for n in noms],
             customdata=[[o, fr(m / 1e9, 2)] for o, m in zip(officiels, montants)],
             hover="<b>%{customdata[0]}</b><br>%{x:.1f} % de l'effort · %{customdata[1]} Md€<extra></extra>")
    fig.update_layout(height=520, margin=dict(r=30),
                      xaxis=dict(title="% de l'effort de l'État", range=[0, 36], dtick=10,
                                             showgrid=True, gridcolor=c.GRILLE),
                      yaxis=dict(showgrid=False, tickfont=dict(size=12, color=c.MARINE)), bargap=0.3)
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          ["l'enseignement scolaire porte presque un tiers de l'effort, deux fois et demie plus que le ministère "
           "des Outre-mer lui-même.",
           "Trente missions budgétaires se partagent les 21,94 Md€ : le ministère coordonne une politique dont "
           "il ne tient pas les crédits."], "orange")
    carte("À quoi correspondent ces crédits",
          ["<b>Enseignement scolaire, 30 %</b> : pour l'essentiel, les salaires des enseignants des écoles, "
           "collèges et lycées.",
           "<b>Relations avec les collectivités, 11 %</b> : les dotations de l'État aux collectivités d'outre-mer.",
           "<b>Solidarité, 9 %</b> : des prestations versées par l'État — prime d'activité, allocation aux adultes "
           "handicapés, RSA repris par l'État en Guyane, à Mayotte et à La Réunion.",
           "<b>Sécurités, 8 %, et Défense, 5 %</b> : police, gendarmerie, forces armées stationnées outre-mer."],
          "bleugris")
pied("DPT Outre-mer 2026, annexe « Synthèse tous crédits », p. 229-232, PLF 2026 ; 30 missions, 104 programmes",
     renvoi=RENVOI)

# ───────────────────────────────────────── 3 · la trajectoire
st.markdown("### Depuis 2007, l'effort grossit ailleurs")
g, d = st.columns([1.65, 1], gap="large")
with g:
    vue = st.radio("Afficher", ["La part du ministère", "Les montants"], horizontal=True,
                   label_visibility="collapsed")
    fig = go.Figure()
    if vue == "La part du ministère":
        fig.add_trace(go.Scatter(x=serie.annee, y=serie.part_pct, mode="lines+markers", connectgaps=False,
                                 line=dict(color=c.BLEU_GRIS, width=3), marker=dict(size=6),
                                 fill="tozeroy", fillcolor=c.teinte(c.BLEU_GRIS, 0.10),
                                 hovertemplate="%{x} : %{y:.1f} %<extra></extra>"))
        for an, v in ((2007, serie.part_pct.iloc[0]), (2026, serie.part_pct.iloc[-1])):
            fig.add_annotation(x=an, y=v, text=f"<b>{fr(v)} %</b>", yshift=16, showarrow=False,
                               font=dict(color=c.BLEU_GRIS, size=14))
        fig.update_layout(yaxis=dict(title="% de l'effort de l'État", range=[0, 20]))
    else:
        fig.add_trace(go.Scatter(x=serie.annee, y=serie.dpt_md, name="Effort de l'État (DPT)", mode="lines+markers",
                                 line=dict(color=c.MARINE, width=3), marker=dict(size=6), connectgaps=False,
                                 hovertemplate="%{x} : %{y:.2f} Md€<extra>Effort de l'État</extra>"))
        fig.add_trace(go.Scatter(x=serie.annee, y=serie.mission_m / 1000, name="Mission Outre-mer",
                                 mode="lines+markers", line=dict(color=c.VERT, width=3), marker=dict(size=6),
                                 hovertemplate="%{x} : %{y:.2f} Md€<extra>Mission Outre-mer</extra>"))
        fig.update_layout(yaxis=dict(title="Md€", range=[0, 25]))
    fig.update_layout(height=360, xaxis=dict(dtick=2))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          ["la part du ministère dans l'effort de l'État recule : 16,4 % en 2007, 12,9 % en 2026.",
           "Ce n'est pas que sa mission baisse — elle passe de 1,96 à 2,83 Md€ — mais que l'effort de l'État "
           "outre-mer croît beaucoup plus vite, et ailleurs : de 12,0 à 21,94 Md€."], "bleugris")
    carte("À savoir", ["2008 n'est pas renseigné : le document de politique transversale de cette année-là ne "
                       "donne pas l'effort global en crédits de paiement."], "marine")
pied("Documents de politique transversale « Outre-mer » 2007-2026 ; PLF, État B (Mission Outre-mer, CP)",
     renvoi=RENVOI)

# ───────────────────────────────────────── 4 · les dépenses fiscales, à part
st.markdown("### À côté du budget : les impôts auxquels l'État renonce")
g, d = st.columns([1.65, 1], gap="large")
with g:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=fisc.annee, y=fisc.fiscal_m / 1000, name="Dépenses fiscales outre-mer",
                         marker=dict(color=c.BLEU, line=dict(width=0)),
                         hovertemplate="%{x} : %{y:.2f} Md€<extra>Dépenses fiscales</extra>"))
    fig.add_trace(go.Scatter(x=fisc.annee, y=fisc.mission_m / 1000, name="Mission Outre-mer (pour comparaison)",
                             mode="lines", line=dict(color=c.VERT, width=3, dash="dot"),
                             hovertemplate="%{x} : %{y:.2f} Md€<extra>Mission Outre-mer</extra>"))
    pic = fisc.loc[fisc.fiscal_m.idxmax()]
    fig.add_annotation(x=pic.annee, y=pic.fiscal_m / 1000, text=f"<b>{fr(pic.fiscal_m / 1000, 2)} Md€</b>",
                       yshift=14, showarrow=False, font=dict(color=c.BLEU, size=14))
    fig.update_layout(height=360, yaxis=dict(title="Md€", range=[0, 8]), xaxis=dict(dtick=2), bargap=0.25)
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    fin = fisc.iloc[-1]
    carte("Ce graphique montre que…",
          [f"une part importante du soutien de l'État passe hors budget, par l'impôt : "
           f"{fr(fin.fiscal_m / 1000, 2)} Md€ en 2026, {fr(fin.ratio, 2)} fois la mission du ministère. Ces "
           f"{sigle('dépenses fiscales')} ont culminé à 7,09 Md€ en 2023."], "bleu")
    carte("Pourquoi ne pas les additionner au budget ?",
          ["Un crédit, c'est de l'argent que l'État verse. Une dépense fiscale, c'est un impôt qu'il ne perçoit pas.",
           "Son montant est une estimation, qui dépend de ce que font les contribuables et qui est souvent révisée "
           "après coup. Les additionner reviendrait à mélanger un paiement et un manque à gagner : c'est pourquoi "
           "le budget de l'État les présente à part."], "bleugris")
pied("Voies et Moyens, tome II (annexe au PLF), 2009-2026 ; 2020 : note d'exécution de la Cour des comptes",
     renvoi=RENVOI)

# ───────────────────────────────────────── glossaire et téléchargements
st.markdown("##### Télécharger")
b = st.columns(4)
telecharger(b[0], "Figure · la cascade", "cascade_budgetaire_2026.png", figure=True)
telecharger(b[1], "Figure · qui porte l'effort", "missions_contributrices_2026.png", figure=True)
telecharger(b[2], "Données · missions 2026", "budget_contributeurs.csv")
telecharger(b[3], "Données · série 2007-2026", "budget_serie.csv")
