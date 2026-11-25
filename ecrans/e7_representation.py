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
from composants import chiffres_cles, carte, deux_lignes, en_lettres, entete, fond, fr, glossaire, lire, pied, telecharger, tuile

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
C = lire("chiffres_cites.csv").set_index("cle").valeur          # groupe GDR et seuil d'un groupe

entete("Écran 7 · La représentation", "Comment les outre-mer sont-ils représentés ?",
       "À l'Assemblée nationale, des sièges très inégalement répartis entre territoires. Et, selon les "
       "majorités, un poids qui change du tout au tout.")
glossaire(["législature", "groupe politique"])

chiffres_cles()
HABITES = len(S) + 1                     # Saint-Martin et Saint-Barthélemy partagent un siège : onze territoires
DELEG = C.get("delegation_om_membres")   # membres de la délégation aux outre-mer, une fois la source vérifiée
t = st.columns(4 if DELEG else 3)
tuile(t[0], f"{SIEGES_OM:.0f} sur {SIEGES_AN:.0f}",
      f"sièges de députés, soit {fr(K['Part des sièges (%)'], 2)} % de l'Assemblée nationale")
tuile(t[1], f"≈ {fr(K['Part de la population (%)'])} %", "de la population de la France vit dans les outre-mer",
      "bleugris")
tuile(t[2], f"{HABITES}", "territoires habités, qui élisent leurs députés ; les TAAF et Clipperton n'ont pas de "
      "population permanente", "bleu")
if DELEG:
    tuile(t[3], f"{fr(DELEG, 0)}", "membres de la délégation aux outre-mer de l'Assemblée nationale, dont les députés "
          "élus outre-mer", "bleugris")
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
          [f"à l'échelle des outre-mer, {fr(K['Part des sièges (%)'], 2)} % "
           f"des sièges pour environ {fr(K['Part de la population (%)'])} % de la population.",
           f"Mais d'un territoire à l'autre, un député représente de {fr(mini.habitants_par_depute, 0)} habitants "
           f"({mini.territoire}) à {fr(maxi.habitants_par_depute, 0)} ({maxi.territoire}) : près de "
           f"{fr(maxi.habitants_par_depute / mini.habitants_par_depute, 0)} fois plus."], "orange")
    carte("Les populations utilisées",
          [f"<b>{r.territoire}</b> : {r.source_population}"
           + (" (population au 1er janvier 2023)" if "2025-1362" in r.source_population else "")
           for r in S.itertuples()]
          + ["Les dates diffèrent d'un territoire à l'autre : la part de population est un ordre de grandeur. "
             "Saint-Martin et Saint-Barthélemy partagent un seul député."], "bleugris", puces=True)
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
      [f"Le groupe de la Gauche démocrate et républicaine doit son existence à ses députés ultramarins : sans eux, "
       f"il n'atteindrait pas les {en_lettres(C['seuil_groupe_an'])} députés nécessaires pour former un groupe. "
       f"De 2022 à 2024, ils étaient {en_lettres(C['gdr_ultramarins_l16'])} sur "
       f"{fr(C['gdr_membres_l16'], 0)}.",
       f"Depuis la dissolution de 2024, ils sont {en_lettres(C['gdr_ultramarins_l17'])} sur "
       f"{fr(C['gdr_membres_l17'], 0)}, soit {fr(100 * C['gdr_ultramarins_l17'] / C['gdr_membres_l17'], 0)} % — un point d'appui pour des majorités sur les questions "
       f"ultramarines, mais aussi sur la sécurité sociale, l'écologie ou le budget."], "bleu", b)
carte("Mais dispersés",
      [f"Les {fr(SIEGES_OM, 0)} députés se répartissent entre plusieurs groupes politiques, sans coordination "
       "systématique : ils "
       "pèsent rarement en bloc sur les grandes décisions."], "bleugris")
pied("Fiche variable V4, « Représentativité politico-territoriale », v4 (2026) : Assemblée nationale, composition "
     "des groupes et de la délégation aux outre-mer (16e et 17e législatures)", renvoi=RENVOI)

# ───────────────────────────────────────── 3 · les couleurs politiques, 1958-2026
st.markdown("### Quelles couleurs politiques, territoire par territoire, de 1958 à 2026 ?")
PT = lire("politique_territoires.csv")
PM = lire("politique_mandats.csv")
PP = lire("politique_positions.csv").sort_values("ordre")
CH = lire("politique_chiffres.csv")
# couleurs : celles de la grille des positions (18 novembre 2026) — rouge à gauche, du plus foncé (autonomiste ou
# indépendantiste) au plus clair (réformiste) ; bleu à droite, du centre (clair) à l'extrême droite (foncé) ; jaune
# pour le composite et le non déterminé. Un code dans chaque case double la couleur.
FAM = {r.position: (r.couleur, r.code) for r in PP.itertuples()}
FAM.update({"Partagé": (c.SABLE, "="), "Pas de député propre": ("#E4E1DB", "–")})
FAMILLE = dict(zip(PP.position, PP.famille))
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
                zl.append(noms.index(r.position_dominante))
                tl.append(FAM[r.position_dominante][1])
                deps = PM[(PM.territoire == t) & (PM.legislature == leg)].sort_values("debut")
                fam = FAMILLE.get(r.position_dominante)
                il.append(f"<b>{t}</b> · {leg}<sup>e</sup> législature ({AN_LEG[leg]})<br>"
                          f"{r.position_dominante}" + (f" · famille : {fam.lower()}" if fam else "") + "<br>" +
                          "<br>".join(f"{x.depute} — {x.groupe} · {x.position} ({x.jours} j)"
                                      for x in deps.itertuples()))
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
        # une légende lisible : une pastille par position, dans l'ordre de l'axe
        for f in noms:
            fig.add_trace(go.Bar(x=[None], y=[None], name=f"{FAM[f][1]} {f[0].lower() + f[1:]}",
                                 marker=dict(color=FAM[f][0], line=dict(color=c.FILET, width=1))))
        fig.update_layout(height=600, margin=dict(l=10, r=10, t=10, b=10), barmode="overlay",
                          legend=dict(orientation="h", y=-0.3, yanchor="top", x=0, font=dict(size=10),
                                      entrywidth=225, itemwidth=30),
                          xaxis=dict(type="category", title="législature (période)", showgrid=False,
                                     tickfont=dict(size=9), tickangle=-90, showline=False),
                          yaxis=dict(autorange="reversed", showgrid=False, showline=False,
                                     tickfont=dict(size=11, color=c.MARINE)))
    else:
        A = PM.groupby(["legislature", "position"]).jours.sum().unstack(fill_value=0)
        A = A.div(A.sum(axis=1), axis=0) * 100
        base = pd.Series(0.0, index=A.index)
        for f in PP.position:                            # dans l'ordre de l'axe, de la gauche à la droite
            if f not in A:
                continue
            fig.add_trace(go.Bar(x=[AN_LEG[l] for l in A.index], y=A[f], base=base, width=0.78,
                                 marker=dict(color=FAM[f][0], line=dict(color=c.FILET, width=0.5)),
                                 name=f"{FAM[f][1]} {f[0].lower() + f[1:]}", customdata=[f] * len(A),
                                 hovertemplate="%{x} · %{customdata} : %{y:.0f} %<extra></extra>"))
            base = base + A[f]
        fig.update_layout(height=520, margin=dict(t=10), barmode="overlay",
                          legend=dict(orientation="h", y=-0.15, yanchor="top", x=0, font=dict(size=10),
                                      entrywidth=225, itemwidth=30),
                          xaxis=dict(type="category", tickangle=-90, tickfont=dict(size=10), showgrid=False),
                          yaxis=dict(title="% des jours de siège", range=[0, 100], dtick=25, showgrid=True,
                                     gridcolor=c.GRILLE, ticksuffix=" %"))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    def part(zone, periode, niveau, valeur):
        x = CH[(CH.zone == zone) & (CH.periode == periode) & (CH.niveau == niveau) & (CH.valeur == valeur)]
        return float(x.part_jours_pct.iloc[0]) if len(x) else 0.0

    def tete(zone, periode, niveau="famille"):
        x = CH[(CH.zone == zone) & (CH.periode == periode) & (CH.niveau == niveau)]
        x = x.sort_values("part_jours_pct", ascending=False).iloc[0]
        return x.valeur, float(x.part_jours_pct)

    DOM, PAC = "Antilles, Guyane, La Réunion", "Pacifique"
    AI = "Gauche autonomiste / indépendantiste"
    f1, p1 = tete(DOM, "1958-1981")
    f2, p2 = tete(DOM, "1981-2017")
    f3, p3 = tete(DOM, "2017-2026")
    q1, q2 = part(PAC, "1958-1981", "famille", "Droite"), part(PAC, "1981-2017", "famille", "Droite")
    n_ed = int(CH[(CH.niveau == "nombre") & (CH.valeur == "Extrême droite")].part_jours_pct.iloc[0])
    carte("Ce graphique montre que…",
          [f"dans les Antilles, en Guyane et à La Réunion, les députés siègent surtout à {f1.lower()} de 1958 à 1981 "
           f"({fr(p1, 0)} % des jours de siège), à {f2.lower()} de 1981 à 2017 ({fr(p2, 0)} %), et plus encore "
           f"depuis 2017 ({fr(p3, 0)} %). Depuis 2017, les élus autonomistes ou indépendantistes y tiennent "
           f"{fr(part(DOM, '2017-2026', 'position', AI), 0)} % des jours de siège, contre "
           f"{fr(part(DOM, '1981-2017', 'position', AI), 0)} % avant.",
           f"Dans le Pacifique, la droite et le centre tiennent {fr(q1, 0)} % des jours de siège jusqu'en 1981 et "
           f"{fr(q2, 0)} % jusqu'en 2017 ; depuis 2017, les indépendantistes polynésiens et calédoniens en tiennent "
           f"{fr(part(PAC, '2017-2026', 'position', AI), 0)} %.",
           f"En 2024, pour la première fois, {n_ed} députés ultramarins siègent à l'extrême droite : à La Réunion "
           f"et à Mayotte."], "orange")
    carte("À lire avec prudence",
          ["Chaque député est rangé d'après le groupe auquel il s'inscrit à Paris, sauf au groupe de la Gauche "
           "démocrate et républicaine, où beaucoup d'élus ultramarins viennent de partis locaux autonomistes ou "
           "indépendantistes : ceux-là sont rangés d'après leur parti. Le rattachement financier déclaré à "
           "l'Assemblée sert de recoupement, pas de critère : plusieurs élus indépendantistes déclarent certaines "
           "années le Parti communiste français.",
           "Le classement en positions et en familles est un codage du CLSE ; le centre est rangé au bout clair de "
           "la droite. Chaque case pèse les jours de siège : un suppléant compte le temps qu'il a siégé. « = » : deux "
           "positions à égalité. « ND » : non-inscrit ou groupe non renseigné.",
           "« – » : pas de député propre. Mayotte, partie du territoire des Comores, élit son premier député en "
           "1977 ; Saint-Barthélemy et Saint-Martin votent dans une circonscription de la Guadeloupe jusqu'en "
           "2012."], "bleugris")
pied("Assemblée nationale, base Sycomore des députés (fiches consultées le 29 octobre 2026) et listes annuelles de "
     "rattachement des députés aux partis ; codage des positions politiques : CLSE (grille du 18 novembre 2026). "
     "Saint-Barthélemy et Saint-Martin : circonscription propre depuis 2012. Méthode : onglet POL_Methode de la base",
     statut="Calcul", renvoi=RENVOI)
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
          [f"Le concours national à affectation locale (CNAL) permet de passer un concours de la fonction publique "
           f"en choisissant d'être affecté dans son territoire. Lancé en 2020 : {fr(C['cnal_concours_2020_2025'], 0)} "
           f"concours jusqu'en 2025, environ {fr(C['cnal_postes_par_an'], 0)} postes par an — prometteur, mais "
           f"marginal à l'échelle de la fonction publique ultramarine.",
           "Les ministres eux-mêmes : voir l'écran 3."], "orange")
pied("Fiche variable V4, v4 (2026) ; Sénat, rapport n° 264 (2025), Philippe Bas et Victorin Lurel, « L'action de "
     "l'État outre-mer : pour un choc régalien »", renvoi=RENVOI)

st.markdown("##### Télécharger")
b = st.columns(2)
telecharger(b[0], "Données · sièges et population par territoire", "representation_sieges.csv")
telecharger(b[1], "Données · les députés ultramarins depuis 1958", "politique_mandats.csv")
