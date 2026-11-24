# -*- coding: utf-8 -*-
"""Écran 3 — Qui a dirigé le ministère des Outre-mer ?

Textes repris du deck du diagnostic (23 septembre 2026), diapositives « Les ministres » et
« Qui occupe le poste », validés par José. Règle d'ancrage du 17 septembre 2026 : seul compte
l'ancrage antérieur à la nomination ; « autre forme » jamais confondue avec la naissance.
Règle de comptage du 19 novembre 2026 : le titulaire du portefeuille ; le ministre de l'Intérieur seulement
quand personne d'autre ne le tient. Tous les chiffres des textes sont calculés depuis donnees/.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import NBSP, carte, en_lettres, entete, fond, fr, glossaire, lire, pied, sigle, telecharger, tuile

RENVOI = "partie « Rôle et histoire du ministère »"        # intitulé définitif à caler sur le rapport

c.css()
fond(["Saint-Martin", "Saint-Barthélemy", "Martinique"])
M = lire("ministres_mandats.csv")
P = lire("ministres_presidents.csv")
K = lire("ministres_chiffres.csv").set_index("indicateur").valeur
ARRET = pd.Timestamp(K["Date d'arrêt de la base"])
SOURCE = f"Journal officiel — base des {K['Mandats']} mandats arrêtée au {ARRET:%d/%m/%Y}"
REGLE = ("Un mandat = une nomination dans un gouvernement. On compte le membre du gouvernement chargé des outre-mer ; "
         "le ministre de l'Intérieur seulement quand personne d'autre ne tient le portefeuille. Non comptés : "
         + K["Titres « outre-mer » non comptés"])
PRES = list(P.president)
# libellés courts : huit colonnes doivent tenir sur un téléphone
LIB = [f"{p.replace(' d' + chr(39) + 'Estaing', '')}<br>{a}-{str(int(b))[2:]}" if pd.notna(b)
       else f"{p}<br>depuis {a}" for p, a, b in zip(P.president, P.debut, P.fin)]

n, pers = len(M), M.ministre.nunique()
moy, med = M.duree_jours.mean(), M.duree_jours.median()
courts = int((M.duree_jours < 183).sum())
AN0 = int(M.debut.min()[:4])                                         # 1959, première nomination de la base
PREMIERE_FEMME = int(M[M.sexe == "F"].debut.min()[:4])
PREMIER_ANCRE = int(M[M.ancrage != "aucun"].debut.min()[:4])
ordre = M.sort_values("debut").drop_duplicates("ministre")
NOMS_NES = list(ordre[ordre.ancrage == "né outre-mer"].ministre)
NOMS_AUTRES = list(ordre[ordre.ancrage == "autre forme"].ministre)
NOM_PRES = {"de Gaulle": "de Gaulle", "Pompidou": "Georges Pompidou", "Giscard d'Estaing": "Valéry Giscard d'Estaing",
            "Mitterrand": "François Mitterrand", "Chirac": "Jacques Chirac", "Sarkozy": "Nicolas Sarkozy",
            "Hollande": "François Hollande", "Macron": "Emmanuel Macron"}
CHIDO = pd.Timestamp("2024-12-14")                                   # passage du cyclone Chido sur Mayotte


def et(noms):
    n = list(noms)
    return n[0] if len(n) == 1 else ", ".join(n[:-1]) + " et " + n[-1]


SE = M[M.rang == "Secrétaire d'État"]
DELEGUES = M[(M.rang == "Ministre délégué") & (M.debut >= "2017")]
ETAT = M[M.rang == "Ministre d'État"]
ETAT_ANCIENS = ETAT[ETAT.debut < "2017"]
ETAT_RECENT = ETAT[ETAT.debut >= "2017"].sort_values("debut").iloc[0]
nes = M[M.ancrage == "né outre-mer"]

entete("Écran 3 · Les ministres", "Qui a dirigé le ministère des Outre-mer ?",
       f"{pers} personnes et {n} mandats depuis {AN0}. À quel rang, combien de temps elles restent, et qui elles sont.")
glossaire(["mandat", "rang", "rattaché à l'Intérieur", "ancrage"])

t = st.columns(4)
tuile(t[0], f"{pers}", f"ministres depuis {AN0}, pour <b>{n} mandats</b> : une même personne peut être nommée "
      f"dans plusieurs gouvernements")
tuile(t[1], f"{fr(moy, 0)} jours", f"durée moyenne d'un mandat, soit environ {round(moy / 30.44)} mois — la moitié dure moins de "
      f"{fr(med, 0)} jours", "bleugris")
tuile(t[2], f"1 sur {round(n / courts)}", f"des mandats dure moins de six mois ({courts} sur {n})", "orange")
tuile(t[3], f"{nes.ministre.nunique()}", f"ministres nés outre-mer en {ARRET.year - AN0} ans, tous entre "
      f"{nes.debut.min()[:4]} et {nes.fin.max()[:4]} — aucun depuis", "orange")
st.markdown("")

# ───────────────────────────────────────── 1 · un portefeuille qui tourne
st.markdown("### Un portefeuille qui tourne de plus en plus vite")
g, d = st.columns([1.65, 1], gap="large")
with g:
    vue = st.radio("Afficher", ["Le nombre de mandats", "La durée moyenne", "Le rythme des nominations"],
                   horizontal=True, label_visibility="collapsed")
    # présidents en lignes, du plus ancien en haut : huit colonnes ne tiennent pas sur un téléphone.
    # Le rang et le rattachement sont à l'écran 1 : ici, seulement la rotation.
    col, unite, titre, fmt = {
        "Le nombre de mandats": ("mandats", "", "mandats", lambda v: f"{v:.0f}"),
        "La durée moyenne": ("duree_moyenne_j", " j", "jours", lambda v: fr(v, 0)),
        "Le rythme des nominations": ("mandats_par_an", "", "mandats par année de présidence", lambda v: fr(v, 2)),
    }[vue]
    coul = [c.ORANGE if p == "Macron" else c.BLEU_GRIS for p in PRES]
    fig = go.Figure()
    c.barres(fig, LIB, P[col], coul, width=0.6, text=[f"<b>{fmt(v)}{unite}</b>" for v in P[col]], textsize=13,
             hover="%{x}" + unite + "<extra></extra>")
    fig.update_layout(xaxis=dict(title=titre, range=[0, P[col].max() * 1.25], showgrid=True,
                                 gridcolor=c.GRILLE, nticks=5), showlegend=False)
    fig.update_layout(height=470, bargap=0.28, margin=dict(r=24),
                      yaxis=dict(tickfont=dict(size=12, color=c.MARINE), showgrid=False,
                                 categoryorder="array", categoryarray=LIB[::-1]),
                      legend=dict(traceorder="normal", orientation="h", y=1.1))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    mac = P[P.president == "Macron"].iloc[0]
    ans = (ARRET - pd.Timestamp(f"{mac.debut}-05-14")).days / 365.25
    autres = P[P.president != "Macron"]
    plus_rapide = mac.mandats_par_an > autres.mandats_par_an.max()
    plus_court = mac.duree_moyenne_j < autres.duree_moyenne_j.min()
    long_ = autres.loc[autres.duree_moyenne_j.idxmax()]
    carte("Ce graphique montre que…",
          [f"sous Emmanuel Macron, le portefeuille change de titulaire "
           + ("plus vite que jamais" if plus_rapide else "très vite") +
           f" : {mac.mandats} mandats et {mac.ministres} ministres en {fr(ans, 1)} ans, "
           f"{fr(mac.mandats_par_an, 2)} mandat par année de présidence"
           + (" — le rythme le plus rapide de la Ve République." if plus_rapide else "."),
           f"La durée moyenne " + ("tombe à son plus bas, " if plus_court else "est de ") +
           f"{mac.duree_moyenne_j} jours, contre {long_.duree_moyenne_j} sous "
           + {"Giscard d'Estaing": "Valéry Giscard d'Estaing"}.get(long_.president, long_.president) + "."],
          "orange")
pied(SOURCE + ". " + REGLE, renvoi=RENVOI)

# ───────────────────────────────────────── 2 · le rang et le rattachement, mandat après mandat
st.markdown("### Un statut qui oscille, mandat après mandat")
g, d = st.columns([1.65, 1], gap="large")
RANGS = ["Ministre d'État", "Ministre", "Ministre délégué", "Secrétaire d'État"]
with g:
    fig = go.Figure()
    # un axe de dates lit les nombres en millisecondes : chaque mandat est une barre en dégradé, de sa nomination
    # à sa fin, qui commence claire et finit pleine
    for ratt, coul in (("plein exercice", c.BLEU_GRIS), ("rattaché à l'Intérieur", c.ORANGE)):
        S = M[M.rattachement == ratt]
        debut, fin = pd.to_datetime(S.debut), pd.to_datetime(S.fin)
        ms = lambda d: (d - pd.Timestamp("1970-01-01")).dt.total_seconds() * 1000
        c.barres(fig, S.rang, ms(fin) - ms(debut), coul, base=ms(debut), width=0.62, name=ratt, n=10,
                 customdata=S[["ministre", "gouvernement", "duree_jours"]].values,
                 hover="<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]} jours<extra></extra>")
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
           f"sous {et(NOM_PRES[p] for p in dict.fromkeys(ETAT_ANCIENS.president))}, secrétaire d'État par "
           f"intermittence jusqu'en {SE.fin.max()[:4]}, plus aucun depuis, des ministres délégués de "
           f"{DELEGUES.debut.min()[:4]} à {DELEGUES.fin.max()[:4]}, de nouveau ministre d'État avec "
           f"{ETAT_RECENT.ministre}, {en_lettres((pd.Timestamp(ETAT_RECENT.debut) - CHIDO).days)} jours après le "
           f"cyclone Chido.",
           f"En orange, les mandats rattachés à l'Intérieur : {K['Périodes de rattachement']}."], "orange")
    carte("En chiffres",
          [f"Sur {K['Mandats']} mandats : {K['Mandats de ministre d' + chr(39) + 'État']} de ministre d'État, "
           f"{K['Mandats de ministre']} de ministre, {K['Mandats de ministre délégué']} de ministre délégué, "
           f"{K['Mandats de secrétaire d' + chr(39) + 'État']} de secrétaire d'État.",
           f"{K['Mandats de plein exercice']} sont de plein exercice, {K['Mandats rattachés à l' + chr(39) + 'Intérieur']} "
           "rattachés à l'Intérieur. Les deux premiers rangs siègent au Conseil des ministres ; les deux autres "
           "passent par le ministre dont ils relèvent."], "bleu")
pied(SOURCE + ". Une barre = un mandat, de la nomination à la fin des fonctions", renvoi=RENVOI)

# ───────────────────────────────────────── 3 · qui occupe le poste
st.markdown("### Qui occupe le poste ?")
g, d = st.columns([1.65, 1], gap="large")
cs = [d, d, g]
# la figure du deck (« Quatre ministres nés outre-mer… ») : une colonne par président, une case par mandat dans
# l'ordre chronologique (de gauche à droite, puis de bas en haut), la couleur de l'ancrage, un point pour une femme.
# Le survol donne le nom et les années.
ANCRAGE = {"né outre-mer": c.ORANGE, "autre forme": "#B8AA96", "aucun": "#DAD5CC"}
with g:
    M = M.sort_values("debut")
    der = M.debut.max()

    def annees(r):
        a_, b_ = r.debut[:4], r.fin[:4]
        return f"depuis {a_}" if r.debut == der else (a_ if a_ == b_ else f"{a_}-{b_}")

    def case(x0, y0, x1, y1, r=0.1):
        return (f"M {x0 + r},{y0} L {x1 - r},{y0} Q {x1},{y0} {x1},{y0 + r} L {x1},{y1 - r} Q {x1},{y1} {x1 - r},{y1} "
                f"L {x0 + r},{y1} Q {x0},{y1} {x0},{y1 - r} L {x0},{y0 + r} Q {x0},{y0} {x0 + r},{y0} Z")

    fig = go.Figure()
    cx, cy, info, fem = [], [], [], []
    for i_, p in enumerate(PRES):
        for k, r in enumerate(M[M.president == p].itertuples()):
            x = 4 * i_ + k % 3
            y = k // 3
            fig.add_shape(type="path", path=case(x - 0.42, y - 0.44, x + 0.42, y + 0.44), line=dict(width=0),
                          fillcolor=ANCRAGE[r.ancrage], layer="below")
            cx.append(x)
            cy.append(y)
            info.append(f"<b>{r.ministre}</b> ({annees(r)})<br>{r.fonction}<br>{r.duree_jours} jours")
            if r.sexe == "F":
                fem.append((x, y))
    fig.add_trace(go.Scatter(x=cx, y=cy, mode="markers", marker=dict(size=18, opacity=0), hovertext=info,
                             hoverinfo="text", showlegend=False))
    fig.add_trace(go.Scatter(x=[a for a, _ in fem], y=[b for _, b in fem], mode="markers", name="une femme",
                             hoverinfo="skip",
                             marker=dict(size=9, color=c.MARINE, line=dict(color="#FFFFFF", width=1.5))))
    for anc, col in ANCRAGE.items():                       # la légende : une pastille par ancrage
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
                                 name={"aucun": "aucun ancrage", "autre forme": "autre forme d'ancrage"}.get(anc, anc),
                                 marker=dict(symbol="square", size=13, color=col)))
    # sous chaque colonne, la part des mandats : une femme, né outre-mer, autre forme d'ancrage
    LIGNES = [("part_femmes_pct", "une femme", -1.55), ("part_nes_om_pct", "né outre-mer", -2.2),
              ("part_autre_forme_pct", "autre forme", -2.85)]
    for i_, row in P.iterrows():
        for col, _, yy in LIGNES:
            fig.add_annotation(x=4 * i_ + 1, y=yy, text=f"<b>{row[col]:.0f}{NBSP}%</b>", showarrow=False,
                               font=dict(size=11, color=c.ORANGE if col == "part_nes_om_pct" and row[col]
                                         else c.MARINE))
    COURT_P = {"Giscard d'Estaing": "Giscard"}
    fig.update_layout(
        height=540, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=-0.02, yanchor="top", x=0),
        xaxis=dict(range=[-0.7, 4 * len(PRES) - 1.3], showgrid=False, showline=False, zeroline=False,
                   tickvals=[4 * i_ + 1 for i_ in range(len(PRES))], side="top",
                   ticktext=[f"{COURT_P.get(p, p)}<br>{a_}-{str(int(b_))[2:] if pd.notna(b_) else ''}"
                             for p, a_, b_ in zip(P.president, P.debut, P.fin)],
                   tickfont=dict(size=11, color=c.MARINE)),
        yaxis=dict(range=[-3.25, M.groupby("president").size().max() // 3 + 0.6], showgrid=False, showline=False,
                   zeroline=False, tickvals=[yy for *_, yy in LIGNES], ticktext=[t for _, t, _ in LIGNES],
                   tickfont=dict(size=11, color=c.GRIS)))
    fig.add_hline(y=-1.05, line=dict(color=c.FILET, width=1))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
carte("Ce graphique montre que…",
      [(f"aucune femme et aucun ministre lié à l'outre-mer avant {PREMIERE_FEMME}. Les " if PREMIERE_FEMME == PREMIER_ANCRE
        else f"aucune femme avant {PREMIERE_FEMME} et aucun ministre lié à l'outre-mer avant {PREMIER_ANCRE}. Les ")
       + f"{en_lettres(len(NOMS_NES))} ministres nés outre-mer se succèdent tous entre {nes.debut.min()[:4]} et "
       f"{nes.fin.max()[:4]}, sous des majorités de droite puis de gauche ; depuis, plus aucun.",
       f"Les femmes restent présentes, mais leur part recule : "
       f"{P.set_index('president').part_femmes_pct['Hollande']} % des mandats sous François Hollande, "
       f"{P.set_index('president').part_femmes_pct['Macron']} % depuis."], "orange", cs[0])
carte("Ce que ces dates suivent",
      [f"<b>{PREMIERE_FEMME}</b> — la première femme, {ordre[ordre.sexe == 'F'].ministre.iloc[0]}, arrive deux ans après la loi sur la parité, un an "
       "après la loi Taubira et la loi du 16 novembre 2001 contre les discriminations.",
       f"<b>{nes.debut.min()[:4]}</b> — la première ministre née outre-mer, {NOMS_NES[0]}, est nommée un mois "
       f"après le décret du 27 mai 2009 qui clôt la grève générale de Guadeloupe, "
       f"{en_lettres(int(nes.debut.min()[:4]) - AN0)} ans après la création du portefeuille.",
       f"<b>{nes.fin.max()[:4]}</b> — la parenthèse se ferme trois semaines après l'accord qui clôt le conflit guyanais.",
       "La coïncidence est de date, non de cause."], "bleugris", cs[1])
carte("Qui, et de quel ancrage",
      [f"<b>Nés outre-mer</b> : {', '.join(NOMS_NES)}.",
       f"<b>Autre forme d'{sigle('ancrage')}</b> : {', '.join(NOMS_AUTRES)} — "
       "activité, enfance ou fonctions outre-mer antérieures à la nomination."], "bleu", cs[2])
pied(SOURCE + " ; grille d'ancrage ultramarin du CLSE, v4 (naissance, ascendance, résidence, activité, mandat, "
     "engagement)", renvoi=RENVOI)

# ───────────────────────────────────────── 4 · retrouver un ministre
st.markdown("### Retrouver un ministre")
choix = st.selectbox("Présidence", ["Toutes les présidences"] + PRES, label_visibility="collapsed")
T = M if choix.startswith("Toutes") else M[M.president == choix]
T = T.sort_values("debut", ascending=False)
st.dataframe(pd.DataFrame({
    "Ministre": T.ministre, "Fonction": T.fonction, "Gouvernement": T.gouvernement,
    "Début": pd.to_datetime(T.debut).dt.strftime("%d/%m/%Y"), "Fin": pd.to_datetime(T.fin).dt.strftime("%d/%m/%Y"),
    "Jours": T.duree_jours, "Ancrage": T.ancrage}), hide_index=True, width="stretch",
    height=min(38 + 35 * len(T), 420))
pied(SOURCE + ". Fin du dernier mandat : date d'arrêt de la base, la ministre étant toujours en fonction")

st.markdown("##### Télécharger")
# les figures du deck portent encore l'ancien décompte : on ne propose que les données (le bouton appareil photo
# de chaque graphique en donne l'image)
b = st.columns(2)
telecharger(b[0], f"Données · les {K['Mandats']} mandats", "ministres_mandats.csv")
telecharger(b[1], "Données · par présidence", "ministres_presidents.csv")
