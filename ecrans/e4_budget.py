# -*- coding: utf-8 -*-
"""Écran 4 — Quel pouvoir budgétaire réel a le ministère ?

Textes repris du deck du diagnostic (23 septembre 2026), diapositives budget,
validés par José et par la présidente du CLSE (5,1 % « soit cinq euros sur cent »,
87 % « de l'effort passe par d'autres ministères »).
"""
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import (chiffres_cles, annees, carte, deux_lignes, en_lettres, entete, fond, fr, glossaire, lire, pied, sigle,
                        telecharger, tuile)

RENVOI = "partie « Comment fonctionne le ministère »"       # intitulé définitif à caler sur le rapport

c.css()
fond(["Mayotte", "TAAF"])

cas = lire("budget_cascade.csv")
dpt, mission, marge = cas.haut_eur[0], cas.haut_eur[2], cas.haut_eur[4]
p_mission, p_marge = 100 * mission / dpt, 100 * marge / dpt
contrib = lire("budget_contributeurs.csv")
serie = lire("budget_serie.csv")
fisc = lire("fiscal_serie.csv")
A = lire("fonctionnement_actions.csv")
A["libelle"] = A.action.map(lambda t: deux_lignes(t, 26))
R = lire("restes_serie.csv")
rap_2025 = R.restes_a_payer_m.iloc[-1]
an_rap = int(R.annee.iloc[-1])
mis_rap = R.mission_m.iloc[-1]
rap_2017 = R.set_index("annee").restes_a_payer_m[2017]
# tous les chiffres des phrases viennent des données : rien n'est écrit à la main (José, 24 novembre 2026)
K = lire("chiffres_cites.csv").set_index("cle").valeur
lodeom = A.set_index("code").loc["138-01"]
dot = A.set_index("code").loc["123-06"]
engage = A.contraint_eur.sum() / A.cp_eur.sum()               # part de la mission engagée d'avance

entete("Écran 4 · Le budget", "Quel pouvoir budgétaire réel a le ministère ?",
       "Ce que l'État consacre aux outre-mer, ce que le ministère en porte, et ce qu'il en décide vraiment. "
       "Tous les montants sont en crédits de paiement, l'argent effectivement dépensé dans l'année.")
glossaire(["DPT", "Mission Outre-mer", "P138", "P123", "LODEOM", "CP", "restes à payer", "dépenses fiscales"])

# ───────────────────────────────────────── les quatre chiffres
chiffres_cles()
t = st.columns(4)
tuile(t[0], f"{fr(dpt / 1e9, 2)} Md€", "consacrés par l'État aux outre-mer en 2026, tous ministères confondus")
tuile(t[1], f"{fr(p_mission)} %", f"de cet effort inscrits au budget du ministère des Outre-mer, soit "
      f"{fr(mission / 1e9, 2)} Md€", "bleugris")
tuile(t[2], f"{fr(p_marge)} %", f"<b>soit {en_lettres(p_marge)} euros sur cent</b> : la part que le ministère décide "
      f"vraiment chaque année, le reste de son budget étant engagé d'avance", "orange")
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
          [f"<b>Inscrit n'est pas décidé.</b> Sur 100 euros que l'État consacre aux outre-mer, "
           f"{fr(p_mission, 0)} sont inscrits au budget du ministère ({fr(p_mission)} %). Mais le ministère n'en "
           f"décide vraiment que {fr(p_marge, 0)} ({fr(p_marge)} %).",
           f"La différence est engagée d'avance : la compensation automatique des exonérations de charges "
           f"({sigle('LODEOM')}) et la moitié des dotations aux collectivités. Le ministère la paie, mais ne la "
           f"choisit pas."], "orange")
    fin_f = fisc.iloc[-1]
    carte("Comment c'est calculé, étape par étape",
          [f"<b>1.</b> L'effort total de l'État pour les outre-mer ({sigle('DPT')}) : <b>{fr(dpt / 1e9, 2)} Md€</b>.",
           f"<b>2.</b> Dont le budget du ministère ({sigle('Mission Outre-mer', 'mission Outre-mer')}) : "
           f"<b>{fr(mission / 1e9, 2)} Md€</b>, soit {fr(p_mission)} %.",
           f"<b>3.</b> On retire la compensation des exonérations de charges, fixée par la loi : "
           f"<b>− {fr(lodeom.cp_eur / 1e9, 2)} Md€</b>.",
           f"<b>4.</b> On retire la moitié des dotations aux collectivités, en partie garanties par la loi : "
           f"<b>− {fr(dot.contraint_eur / 1e9, 2)} Md€</b>. Cette moitié est une convention, assumée.",
           f"<b>5.</b> Reste ce que le ministère décide chaque année : <b>{fr(marge / 1e9, 2)} Md€</b>, soit "
           f"{fr(p_marge)} % des {fr(dpt / 1e9, 2)} Md€.",
           f"À côté du budget, l'État renonce aussi à {fr(fin_f.fiscal_m / 1000, 2)} Md€ d'impôts en "
           f"{fin_f.annee} ({sigle('dépenses fiscales')}), {fr(fin_f.ratio, 1)} fois le budget du ministère : "
           f"présentées à part, elles ne s'additionnent pas aux crédits."], "bleugris")
pied("DPT Outre-mer 2026, p. 10 ; PAP Mission Outre-mer 2026, récapitulation par action ; Voies et Moyens, tome II "
     "(PLF 2026), pour les dépenses fiscales", statut="Calcul", renvoi=RENVOI)

# ───────────────────────────────────────── 2 · la mission, action par action
st.markdown("### Ses crédits, action par action")
g, d = st.columns([1.65, 1], gap="large")
with g:
    choix = st.radio("Programme", ["Les deux programmes", "Emploi outre-mer (P138)", "Conditions de vie (P123)"],
                     horizontal=True, label_visibility="collapsed")
    S = A if choix.startswith("Les deux") else A[A.programme == ("P138" if "138" in choix else "P123")]
    S = S.sort_values("cp_eur")
    # comme le deck : en bleu l'engagé d'avance, en vert l'arbitré ; l'étiquette « montant · part du programme »
    # prend la couleur de la part dominante
    fig = go.Figure()
    cd = S[["programme", "part_programme_pct", "action"]].values
    c.barres(fig, S.libelle, S.contraint_eur / 1e6, c.BLEU, name="engagé d'avance", customdata=cd, width=0.66,
             hover="<b>%{customdata[2]}</b> (%{customdata[0]})<br>engagé d'avance : %{x:,.0f} M€<extra></extra>")
    c.barres(fig, S.libelle, S.pilotable_eur / 1e6, c.VERT, base=S.contraint_eur / 1e6, name="arbitré chaque année",
             customdata=cd, width=0.66,
             hover="<b>%{customdata[2]}</b> (%{customdata[0]})<br>arbitré chaque année : %{x:,.0f} M€<extra></extra>")
    for r in S.itertuples():
        # la plus longue barre porte son étiquette à l'intérieur : sur un téléphone, elle sortirait du cadre
        dedans = r.cp_eur == S.cp_eur.max() and len(S) > 1
        fig.add_annotation(y=r.libelle, x=r.cp_eur / 1e6, xanchor="right" if dedans else "left",
                           xshift=-6 if dedans else 5, showarrow=False,
                           text=f"<b>{fr(r.cp_eur / 1e6, 0)} M€ · {fr(r.part_programme_pct, 0)} %</b>",
                           font=dict(size=12, color="#FFFFFF" if dedans else
                                     (c.BLEU if r.contraint_eur > r.pilotable_eur else c.VERT)))
    fig.update_layout(height=100 + 40 * len(S), margin=dict(r=20),
                      xaxis=dict(title="M€ (crédits de paiement 2026)", range=[0, S.cp_eur.max() / 1e6 * 1.55],
                                 showgrid=True, gridcolor=c.GRILLE, nticks=5),
                      yaxis=dict(showgrid=False, tickfont=dict(size=12, color=c.MARINE)),
                      legend=dict(orientation="h", y=1.02, yanchor="bottom"))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          [f"<b>{en_lettres(10 * engage)} euros sur dix sont engagés d'avance</b> : la compensation des exonérations de charges "
           f"({sigle('LODEOM')}, {fr(lodeom.cp_eur / 1e9, 2)} Md€, {fr(lodeom.part_programme_pct, 0)} % du "
           f"programme emploi), qui suit la masse salariale, et la moitié des dotations aux collectivités "
           f"({fr(dot.contraint_eur / 1e6, 0)} M€ sur {fr(dot.cp_eur / 1e6, 0)}).",
           f"En vert, le reste — {fr(A.pilotable_eur.sum() / 1e9, 2)} Md€ : logement, aménagement, continuité "
           f"territoriale, service militaire adapté et mobilité. C'est la seule part que le ministère arbitre d'une "
           f"année sur l'autre."], "orange")
    carte("Six sur dix, cinq sur cent : deux totaux différents",
          [f"<b>{en_lettres(10 * engage).capitalize()} euros sur dix</b> : la part du budget du ministère "
           f"({fr(mission / 1e9, 2)} Md€) engagée d'avance.",
           f"<b>{en_lettres(p_marge).capitalize()} euros sur cent</b> : la part de l'effort total de l'État "
           f"({fr(dpt / 1e9, 2)} Md€) que le ministère décide.",
           "Le premier chiffre regarde le budget du ministère, le second tout ce que l'État dépense pour les "
           "outre-mer. La dotation aux collectivités y est comptée pour moitié, la convention de la cascade "
           "ci-dessus."], "marine")
pied(f"PAP Mission Outre-mer 2026, récapitulation des crédits par programme et action ({sigle('CP')})",
     renvoi=RENVOI)

# ───────────────────────────────────────── 3 · les restes à payer
st.markdown("### Voté n'est pas dépensé")
g, d = st.columns([1.65, 1], gap="large")
with g:
    vue = st.radio("Afficher", ["Où, fin 2025", "Depuis 2013"], horizontal=True, label_visibility="collapsed")
    fig = go.Figure()
    if vue == "Où, fin 2025":
        S = A[A.restes_a_payer_m >= 10].sort_values("restes_a_payer_m")
        c.barres(fig, S.libelle, S.restes_a_payer_m, c.BLEU, width=0.62,
                 text=[f"<b>{fr(v, 0)} M€</b>" for v in S.restes_a_payer_m],
                 hover="<b>%{y}</b><br>%{x:,.0f} M€ restant à payer<extra></extra>")
        fig.update_layout(height=380, margin=dict(r=40), showlegend=False,
                          xaxis=dict(title="M€ restant à payer au 31 décembre 2025", range=[0, 1150],
                                     showgrid=True, gridcolor=c.GRILLE, nticks=5),
                          yaxis=dict(showgrid=False, tickfont=dict(size=12, color=c.MARINE)))
    else:
        # la figure du deck : des barres bleues, la dernière en orange, le budget de la mission en vert
        Rv = R.dropna(subset=["restes_a_payer_m"])
        coul = [c.ORANGE if a == Rv.annee.max() else c.BLEU for a in Rv.annee]
        c.barres(fig, Rv.annee, Rv.restes_a_payer_m / 1000, coul, orientation="v", width=0.62,
                 name="Restes à payer en fin d'année",
                 hover="%{x} : %{y:.2f} Md€<extra>Restes à payer</extra>")
        for a in R[R.restes_a_payer_m.isna()].annee:
            fig.add_annotation(x=a, y=0, yanchor="bottom", yshift=4, text="n.d.", showarrow=False,
                               font=dict(size=11, color=c.GRIS))
        for a, col in ((Rv.annee.min(), c.BLEU), (Rv.annee.max(), c.ORANGE)):
            v = Rv.set_index("annee").restes_a_payer_m[a] / 1000
            fig.add_annotation(x=a, y=v, yanchor="bottom", yshift=4, text=f"<b>{fr(v, 2)} Md€</b>",
                               showarrow=False, font=dict(size=13, color=col))
        fig.add_trace(go.Scatter(x=R.annee, y=R.mission_m / 1000, name="Budget annuel de la mission",
                                 mode="lines", line=dict(color=c.VERT, width=4),
                                 hovertemplate="%{x} : %{y:.2f} Md€<extra>Budget de la mission</extra>"))
        fig.update_layout(height=360, xaxis=dict(dtick=2, showgrid=False),
                          yaxis=dict(title="Md€", range=[0, 3.3], showgrid=True, gridcolor=c.GRILLE),
                          legend=dict(orientation="h", y=1.02, yanchor="bottom"))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          [f"<b>fin {an_rap}, l'État doit encore {fr(rap_2025 / 1000, 2)} Md€ pour des opérations déjà décidées "
           f"outre-mer</b> : {'plus' if rap_2025 > mis_rap else 'moins'} que le budget d'une année du ministère "
           f"({fr(mis_rap / 1000, 2)} Md€), et {fr(100 * (rap_2025 / rap_2017 - 1), 0)} % de plus qu'en 2017.",
           f"Pourquoi : quand l'État lance une opération — un collège, un réseau d'eau, des logements —, il "
           f"s'engage sur la totalité dès la signature, puis paie au fur et à mesure des travaux. "
           f"{fr(K['rap_interventions_collectivites_2025'], 0)} % de ces sommes concernent des opérations menées "
           f"par les collectivités : le paiement suit leurs chantiers.",
           f"Et la somme grossit : en 2025, le Parlement a autorisé {fr(K['ecart_ae_cp_p123_2025'], 0)} M€ "
           f"d'engagements de plus que de paiements sur le programme « Conditions de vie outre-mer »."], "orange")
    carte("Comment c'est calculé",
          [f"Les {sigle('restes à payer')} = tout ce que l'État s'est engagé à payer depuis le lancement des "
           "opérations, moins ce qu'il a déjà payé, au 31 décembre de chaque année. Le chiffre est publié par la Cour "
           "des comptes ; il n'est pas recalculé ici."], "bleugris")
pied(f"Cour des comptes, notes d'exécution budgétaire de la mission Outre-mer {R.annee.min()}-{an_rap} (exécution "
     f"2025 : p. 6 et 31, tableau n° 13). {annees(R[R.restes_a_payer_m.isna()].annee)} : montant non publié",
     renvoi=RENVOI)

# ───────────────────────────────────────── 4 · qui porte l'effort
st.markdown("### Qui porte l'effort de l'État outre-mer ?")
g, d = st.columns([1.65, 1], gap="large")
with g:
    # noms courts à l'écran (le téléphone n'a pas la place), nom officiel au survol
    # intitulés compréhensibles par tous (retour du CLSE) ; le nom officiel de la mission reste au survol
    COURT = {"Enseignement scolaire": "Écoles, collèges, lycées",
             "Outre-mer": "Le ministère des Outre-mer",
             "Relations avec les collectivités territoriales": "Dotations aux collectivités",
             "Solidarité, insertion et égalité des chances": "Aides sociales",
             "Sécurités": "Police et gendarmerie",
             "Défense": "Armées",
             "Cohésion des territoires": "Logement et villes",
             "Recherche et enseignement supérieur": "Universités et recherche",
             "Justice": "Justice",
             "Travail et emploi": "Emploi",
             "Gestion des finances publiques": "Impôts et douanes",
             "Écologie, développement et mobilité durables": "Environnement et transports",
             "Administration générale et territoriale de l'État": "Préfectures",
             "Agriculture, alimentation, forêt et affaires rurales": "Agriculture"}
    seuil = 1.0
    part = lambda m: contrib.set_index("mission").part_pct[m]        # noqa: E731 — part d'une mission, en %
    grandes = contrib[contrib.part_pct >= seuil].sort_values("part_pct")
    petites = contrib[contrib.part_pct < seuil]
    noms = [f"Les {len(petites)} autres"] + [COURT.get(n, n) for n in grandes.mission]
    officiels = [f"{len(petites)} missions sous {fr(seuil, 0)} %"] + list(grandes.mission)
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
          [f"les écoles, collèges et lycées portent {fr(part('Enseignement scolaire'), 0)} % de l'effort, "
           f"{fr(part('Enseignement scolaire') / part('Outre-mer'), 1)} fois plus que le ministère des Outre-mer "
           f"lui-même.",
           f"{en_lettres(len(contrib)).capitalize()} missions budgétaires se partagent les {fr(dpt / 1e9, 2)} Md€ : "
           f"le ministère coordonne une politique dont il ne tient pas les crédits."], "orange")
    carte("À quoi correspondent ces crédits",
          [f"<b>Enseignement scolaire, {fr(part('Enseignement scolaire'), 0)} %</b> : pour l'essentiel, les "
           f"salaires des enseignants des écoles, collèges et lycées.",
           f"<b>Relations avec les collectivités, {fr(part('Relations avec les collectivités territoriales'), 0)} %"
           f"</b> : les dotations de l'État aux collectivités d'outre-mer.",
           f"<b>Solidarité, {fr(part('Solidarité, insertion et égalité des chances'), 0)} %</b> : des prestations "
           f"versées par l'État — prime d'activité, allocation aux adultes handicapés, RSA repris par l'État en "
           f"Guyane, à Mayotte et à La Réunion.",
           f"<b>Sécurités, {fr(part('Sécurités'), 0)} %, et Défense, {fr(part('Défense'), 0)} %</b> : police, "
           f"gendarmerie, forces armées stationnées outre-mer."],
          "bleugris")
pied(f"DPT Outre-mer 2026, annexe « Synthèse tous crédits », p. 229-232, PLF 2026 ; {len(contrib)} missions, "
     f"{fr(K['programmes_dpt_2026'], 0)} programmes dont {fr(K['psr_dpt_2026'], 0)} prélèvements sur recettes "
     f"(DPT, p. 10)", renvoi=RENVOI)

# ───────────────────────────────────────── 5 · la trajectoire, en version simple
st.markdown("### Depuis 2007, l'effort grandit ailleurs")
s0, s1 = serie.iloc[0], serie.iloc[-1]
g, d = st.columns([1.65, 1], gap="large")
with g:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=serie.annee, y=serie.part_pct, mode="lines+markers", connectgaps=False,
                             line=dict(color=c.BLEU_GRIS, width=3), marker=dict(size=6),
                             fill="tozeroy", fillcolor=c.teinte(c.BLEU_GRIS, 0.10),
                             hovertemplate="%{x} : %{y:.1f} % de l'effort de l'État<extra></extra>"))
    for an_, v in ((s0.annee, s0.part_pct), (s1.annee, s1.part_pct)):
        fig.add_annotation(x=an_, y=v, text=f"<b>{fr(v)} %</b>", yshift=16, showarrow=False,
                           font=dict(color=c.BLEU_GRIS, size=14))
    fig.update_layout(height=320, xaxis=dict(dtick=2), showlegend=False,
                      yaxis=dict(title="part du ministère dans l'effort de l'État (%)", range=[0, 20]))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    trous = serie[serie.dpt_md.isna()].annee
    carte("Ce graphique montre que…",
          [f"la part du ministère dans l'effort de l'État passe de {fr(s0.part_pct)} % en {s0.annee} à "
           f"{fr(s1.part_pct)} % en {s1.annee} : son budget augmente ({fr(s0.mission_m / 1000, 2)} puis "
           f"{fr(s1.mission_m / 1000, 2)} Md€), mais l'effort de l'État grandit plus vite, dans les autres "
           f"ministères ({fr(s0.dpt_md, 1)} puis {fr(s1.dpt_md, 2)} Md€)."]
          + ([f"{annees(trous)} : le document de l'année ne donne pas l'effort global en crédits de paiement."]
             if len(trous) else []), "bleugris")
pied(f"Documents de politique transversale « Outre-mer » {s0.annee}-{s1.annee} ; PLF, état B (mission Outre-mer, CP)",
     renvoi=RENVOI)

# ───────────────────────────────────────── glossaire et téléchargements
st.markdown("##### Télécharger")
b = st.columns(4)
telecharger(b[0], "Figure · la cascade", "cascade_budgetaire_2026.png", figure=True)
telecharger(b[1], "Figure · la mission par action", "mission_outre_mer_par_action.png", figure=True)
telecharger(b[2], "Figure · les restes à payer", "restes_a_payer.png", figure=True)
telecharger(b[3], "Figure · qui porte l'effort", "missions_contributrices_2026.png", figure=True)
b = st.columns(4)
telecharger(b[0], f"Données · les {len(A)} actions", "fonctionnement_actions.csv")
telecharger(b[1], f"Données · restes à payer {R.annee.min()}-{an_rap}", "restes_serie.csv")
telecharger(b[2], "Données · missions 2026", "budget_contributeurs.csv")
telecharger(b[3], f"Données · série {s0.annee}-{s1.annee}", "budget_serie.csv")
