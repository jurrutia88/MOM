# -*- coding: utf-8 -*-
"""Écran 7 — Comment les outre-mer sont-ils représentés ?

Sièges : onglet E7 du socle (Code électoral, 17e législature). Populations : décret n° 2025-1362 (INSEE) et
instituts des collectivités. Lecture politique reprise de la fiche variable V4 (« Représentativité », v4),
sections 2.1 et 2.2 — sans la ventilation par groupe, qui totalise 28 députés au lieu de 27 dans la fiche.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import carte, deux_lignes, entete, fond, fr, glossaire, lire, pied, telecharger, tuile

RENVOI = "partie « Comment fonctionne le ministère »"       # intitulé définitif à caler sur le rapport

c.css()
fond(["La Réunion", "Guadeloupe", "Nouvelle-Calédonie"])
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
glossaire(["législature", "groupe politique"])

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
    fig = go.Figure()
    c.barres(fig, T.libelle, x, coul, text=txt, textcolor=c.MARINE, hover="<b>%{y}</b> : %{text}<extra></extra>")
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

# ───────────────────────────────────────── 3 · les couleurs politiques, 1958-2026
st.markdown("### Quelles couleurs politiques, territoire par territoire, de 1958 à 2026 ?")
PT = lire("politique_territoires.csv")
PM = lire("politique_mandats.csv")
# couleurs : la convention politique (gauche rouge, centre or, droite bleue) plutôt que la palette du deck ;
# une lettre dans chaque case double la couleur
FAM = {"Gauche": ("#C2553D", "G"), "Centre": ("#D9A441", "C"), "Droite": (c.BLEU, "D"),
       "Extrême droite": (c.MARINE, "ED"), "Hors groupe ou groupe charnière": ("#A39C90", "H"),
       "Partagé": (c.SABLE, "="), "Groupe non renseigné": ("#F2F0EC", "?"),
       "Pas de député propre": ("#E4E1DB", "–")}
# avant leur propre circonscription, ces territoires n'élisaient pas de député à eux
SANS_DEPUTE = {"Mayotte": "Mayotte fait alors partie du territoire des Comores ; son premier député est élu en 1977",
               "Saint-Barthélemy et Saint-Martin": "Saint-Barthélemy et Saint-Martin votent alors dans une "
                                                   "circonscription de la Guadeloupe ; leur propre député est élu "
                                                   "en 2012"}
TERR = ["Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte", "Saint-Pierre-et-Miquelon",
        "Saint-Barthélemy et Saint-Martin", "Polynésie française", "Nouvelle-Calédonie", "Wallis-et-Futuna"]
COURT_T = {"Saint-Pierre-et-Miquelon": "St-Pierre-et-Miquelon", "Saint-Barthélemy et Saint-Martin":
           "St-Barth. et St-Martin", "Polynésie française": "Polynésie", "Nouvelle-Calédonie": "Nouv.-Calédonie"}
LEGS = sorted(PM.legislature.unique())
# chaque législature par sa période : de la première élection à la dernière fin de mandat (la 17e court jusqu'à
# la date d'arrêt de la collecte, octobre 2026)
_deb = PM.groupby("legislature").debut.min().str[:4]
_fin = PM.groupby("legislature").fin.max().str[:4]
AN_LEG = {l: f"{_deb[l]}-{_fin[l][2:]}" for l in _deb.index}
g, d = st.columns([1.65, 1], gap="large")
with g:
    vue_p = st.radio("Afficher", ["Territoire par territoire", "L'ensemble des outre-mer"], horizontal=True,
                     label_visibility="collapsed")
    fig = go.Figure()
    if vue_p == "Territoire par territoire":
        noms = list(FAM)
        idx = PT.set_index(["territoire", "legislature"])
        z, txt, info = [], [], []
        for t in TERR:
            zl, tl, il = [], [], []
            for leg in LEGS:
                if (t, leg) not in idx.index:
                    zl.append(noms.index("Pas de député propre"))
                    tl.append(FAM["Pas de député propre"][1])
                    il.append(f"<b>{t}</b> · {leg}<sup>e</sup> législature ({AN_LEG[leg]})<br>Pas de député "
                              f"propre<br>{SANS_DEPUTE.get(t, '')}")
                    continue
                r = idx.loc[(t, leg)]
                zl.append(noms.index(r.famille_dominante))
                tl.append(FAM[r.famille_dominante][1])
                deps = PM[(PM.territoire == t) & (PM.legislature == leg)].sort_values("debut")
                il.append(f"<b>{t}</b> · {leg}<sup>e</sup> législature ({AN_LEG[leg]})<br>"
                          f"{r.famille_dominante}<br>" +
                          "<br>".join(f"{x.depute} — {x.groupe} ({x.jours} j)" for x in deps.itertuples()))
            z.append(zl)
            txt.append(tl)
            info.append(il)
        n = len(noms)
        echelle = []
        for i, f in enumerate(noms):                    # une couleur franche par famille
            echelle += [[i / n, FAM[f][0]], [(i + 1) / n, FAM[f][0]]]
        fig.add_trace(go.Heatmap(z=z, x=[AN_LEG[l] for l in LEGS], y=[COURT_T.get(t, t) for t in TERR],
                                 zmin=-0.5, zmax=n - 0.5, colorscale=echelle, showscale=False, xgap=2, ygap=2,
                                 text=txt, texttemplate="%{text}", textfont=dict(size=10),   # couleur du texte : contraste automatique
                                 customdata=info, hovertemplate="%{customdata}<extra></extra>"))
        # une légende lisible : une pastille par famille
        for f in noms:
            fig.add_trace(go.Bar(x=[None], y=[None], name=f"{FAM[f][1]} {f.lower()}", marker=dict(color=FAM[f][0])))
        fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), barmode="overlay",
                          legend=dict(orientation="h", y=-0.2, yanchor="top", x=0, font=dict(size=10),
                                      entrywidth=150, itemwidth=30),
                          xaxis=dict(type="category", title="législature (période)", showgrid=False,
                                     tickfont=dict(size=9), tickangle=-90, showline=False),
                          yaxis=dict(autorange="reversed", showgrid=False, showline=False,
                                     tickfont=dict(size=11, color=c.MARINE)))
    else:
        A = PM.groupby(["legislature", "famille"]).jours.sum().unstack(fill_value=0)
        A = A.div(A.sum(axis=1), axis=0) * 100
        base = pd.Series(0.0, index=A.index)
        for f in ["Gauche", "Centre", "Droite", "Extrême droite", "Hors groupe ou groupe charnière",
                  "Groupe non renseigné"]:
            if f not in A:
                continue
            c.barres(fig, [AN_LEG[l] for l in A.index], A[f], FAM[f][0], base=base, orientation="v", width=0.78,
                     name=f.lower(), customdata=[f] * len(A),
                     hover="%{x} · %{customdata} : %{y:.0f} %<extra></extra>")
            base = base + A[f]
        fig.update_layout(height=430, margin=dict(t=10),
                          legend=dict(orientation="h", y=-0.15, yanchor="top", x=0, font=dict(size=11)),
                          xaxis=dict(type="category", tickangle=-90, tickfont=dict(size=10), showgrid=False),
                          yaxis=dict(title="% des jours de siège", range=[0, 100], dtick=25, showgrid=True,
                                     gridcolor=c.GRILLE, ticksuffix=" %"))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    carte("Ce graphique montre que…",
          ["de 1958 à 1981, les députés des Antilles, de la Guyane et de La Réunion siègent surtout dans les groupes "
           "de droite (54 % des jours de siège) ; de 1981 à 2017, surtout à gauche (56 %), et plus encore depuis "
           "2017 (66 %).",
           "Dans le Pacifique, le centre domine jusqu'en 1981, la droite de 1981 à 2017, de nouveau le centre "
           "depuis 2017 (68 %).",
           "En 2024, pour la première fois, deux députés ultramarins siègent à l'extrême droite : à La Réunion et "
           "à Mayotte."], "orange")
    carte("À lire avec prudence",
          ["On lit le groupe auquel le député s'inscrit à Paris, pas son étiquette locale. Les partis "
           "autonomistes ou indépendantistes (PPM, PCR, Tavini, FLNKS…) se rattachent à un groupe national ou "
           "restent non inscrits : leur position ne se range pas sur l'axe gauche-droite de l'Hexagone.",
           "Le classement des groupes en familles est un codage du CLSE. Chaque case pèse les jours de siège : un "
           "suppléant compte le temps qu'il a siégé. « = » : deux familles à égalité.",
           "« – » : pas de député propre. Mayotte, partie du territoire des Comores, élit son premier député en "
           "1977 ; Saint-Barthélemy et Saint-Martin votent dans une circonscription de la Guadeloupe jusqu'en "
           "2012."], "bleugris")
pied("Assemblée nationale, base Sycomore des députés (fiches consultées le 29 octobre 2026) ; regroupement des "
     "groupes parlementaires en familles politiques : CLSE. Saint-Barthélemy et Saint-Martin : circonscription "
     "propre depuis 2012", statut="Reconstitué", renvoi=RENVOI)

# ───────────────────────────────────────── 4 · et dans l'administration
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
b = st.columns(2)
telecharger(b[0], "Données · sièges et population par territoire", "representation_sieges.csv")
telecharger(b[1], "Données · les députés ultramarins depuis 1958", "politique_mandats.csv")
