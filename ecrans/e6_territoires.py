# -*- coding: utf-8 -*-
"""Écran 6 — Quels impacts concrets selon les territoires ?

Indicateurs : onglet DATA_Territorial_PIV du socle (Partie IV du rapport, Sénat 2026, INSEE, IEOM…).
Richesse et effort : onglet DATA_PIB_hab_13terr et annexe territoriale du DPT 2026 ; textes repris de la
diapositive « Des réalités très hétérogènes » du deck du diagnostic (validée).
L'indicateur 14 (PIB en % de la moyenne nationale, série Sénat) n'est pas proposé : il contredit la série en
euros pour la Polynésie ; le PIB est traité en euros, comme dans le deck.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import charte as c
from composants import carte, entete, fond, fr, glossaire, lire, pied, telecharger, tuile

RENVOI = "partie IV « Des droits aux réalités »"            # intitulé de travail de la Partie IV du rapport

c.css()
fond(["Mayotte", "Guyane"])
I = lire("territoires_indicateurs.csv")
I = I[I.num != 14]
E = lire("territoires_pib_effort.csv")


def val(num, terr):
    return I[(I.num == num) & (I.territoire == terr)].valeur.iloc[0]


def silhouettes(T):
    """La diapositive du deck (23 septembre) : en haut, l'effort de l'État par habitant ; en dessous, chaque
    territoire par sa silhouette, dont la surface est proportionnelle au PIB par habitant. L'axe des silhouettes est
    verrouillé à l'échelle de l'axe horizontal : les formes gardent leurs proportions à toutes les largeurs."""
    F = lire("territoires_silhouettes.csv")
    ordre = list(dict.fromkeys(F.territoire))                       # du PIB par habitant le plus haut au plus bas
    D = T.set_index("territoire").loc[ordre]
    larg = F.groupby("territoire").x_px.agg(lambda s: s.max() - s.min()).max()
    k = 0.95 / larg                                                 # la plus large tient dans une colonne
    n = len(ordre)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32], vertical_spacing=0.02)
    c.barres(fig, list(range(n)), D.effort_hab_eur, c.BLEU, orientation="v", width=0.56,
             text=[f"<b>{fr(v, 0)} €</b>" for v in D.effort_hab_eur], textcolor=c.MARINE,
             name="effort de l'État par habitant (barre)", customdata=ordre,
             hover="<b>%{customdata}</b><br>effort de l'État : %{y:,.0f} € par habitant<extra></extra>")
    for i, t in enumerate(ordre):
        extreme = t in ("Mayotte", "Saint-Barthélemy")
        trait = c.VERT if extreme else c.BLEU_GRIS
        for j, (_p, P_) in enumerate(F[F.territoire == t].groupby("partie")):
            fig.add_trace(go.Scatter(
                x=i + P_.x_px * k, y=P_.y_px * k, mode="lines", fill="toself", line=dict(color=trait, width=1.6),
                fillcolor=c.teinte(trait, 0.45), hoveron="fills", hoverinfo="text",
                text=f"<b>{t}</b><br>PIB par habitant : {fr(D.loc[t, 'pib_hab_eur'], 0)} € "
                     f"({str(D.loc[t, 'annee_pib'])[:4]})",
                name="PIB par habitant (surface)", legendgroup="pib",
                showlegend=(i == 0 and j == 0)), row=2, col=1)
    fig.update_xaxes(range=[-0.6, n - 0.4], showgrid=False, showline=False, tickvals=list(range(n)),
                     ticktext=[f"{t} · <b>{fr(D.loc[t, 'pib_hab_eur'], 0)} €</b>" for t in ordre],
                     tickangle=-35, tickfont=dict(size=11, color=c.MARINE), row=2, col=1)
    fig.update_xaxes(showticklabels=False, showline=False, row=1, col=1)
    fig.update_yaxes(title="€ par habitant", range=[0, D.effort_hab_eur.max() * 1.18], showgrid=True,
                     tickformat=",d", ticksuffix=" €",
                     gridcolor=c.GRILLE, nticks=4, row=1, col=1)
    fig.update_yaxes(scaleanchor="x2", scaleratio=1, range=[-0.5, 0.5], visible=False, row=2, col=1)
    fig.update_layout(height=600, margin=dict(r=10, t=40, b=10),
                      legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)


entete("Écran 6 · Les territoires", "Quels impacts concrets selon les territoires ?",
       "Pauvreté, prix, emploi, santé, éducation : ce que le fonctionnement actuel produit, territoire par "
       "territoire, comparé à la moyenne nationale.")
glossaire(["seuil de pauvreté national", "NEET", "indice de Gini", "PIB par habitant"])

DROM = ["Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte"]
alim = [val(3, x) for x in DROM]
pib = E.set_index("territoire").pib_hab_eur
t = st.columns(4)
tuile(t[0], f"{fr(val(1, 'Mayotte'), 0)} %", f"de la population de Mayotte sous le seuil de pauvreté national, "
      f"contre {fr(val(1, 'France (réf.)'))} % en France", "orange")
tuile(t[1], f"+{fr(min(alim), 0)} à +{fr(max(alim), 0)} %", "de prix alimentaires dans les départements d'outre-mer "
      "par rapport à l'Hexagone")
tuile(t[2], f"{fr(val(5, 'Mayotte'), 0)} %", f"de chômage à Mayotte en 2024 ; de {fr(val(5, 'Martinique'))} à "
      f"{fr(val(5, 'La Réunion'))} % dans les autres départements ; {fr(val(5, 'France (réf.)'))} % en France",
      "bleugris")
tuile(t[3], f"de 1 à {fr(pib['Saint-Barthélemy'] / pib['Mayotte'])}", "l'écart de richesse produite par habitant, "
      "de Mayotte à Saint-Barthélemy", "orange")
st.markdown("")

# ───────────────────────────────────────── 1 · un indicateur, tous les territoires
st.markdown("### Comparer les territoires, indicateur par indicateur")
noms = I.drop_duplicates("num").set_index("num")
etiq = {n: f"{r.indicateur} ({r.unite})" for n, r in noms.iterrows()}
g, d = st.columns([1.65, 1], gap="large")
with g:
    choix_ind = st.selectbox("Indicateur", list(etiq.values()), label_visibility="collapsed")
    num = next(n for n, e in etiq.items() if e == choix_ind)
    S = I[I.num == num]
    ref = S[S.reference == "oui"]
    V = S[(S.reference == "non") & S.valeur.notna()].sort_values("valeur")
    nd = S[(S.reference == "non") & S.valeur.isna()]
    unite = noms.loc[num, "unite"]
    pct = unite.endswith("%") or unite.startswith("%")
    fmt = (lambda v: fr(v, 2)) if num == 13 else (lambda v: fr(v, 0) if v >= 100 or v == int(v) else fr(v))
    coul = [c.BLEU_GRIS if comp == "O" else c.CLAIR[c.BLEU_GRIS] for comp in V.comparable]
    txt = [f"{m if isinstance(m, str) else ''}{fmt(v)}{' %' if pct else ''}"
           + ("" if comp == "O" else f" ({mil})") for v, m, comp, mil in zip(V.valeur, V.marque, V.comparable,
                                                                             V.millesime)]
    fig = go.Figure()
    c.barres(fig, V.territoire, V.valeur, coul, text=txt, textcolor=c.MARINE,
             customdata=V[["millesime", "source"]].values,
             hover="<b>%{y}</b> : %{x}<br>%{customdata[0]} · %{customdata[1]}<extra></extra>")
    haut = max(V.valeur.max(), ref.valeur.max() if len(ref) else 0)
    if len(ref):
        r0 = ref.iloc[0]
        fig.add_vline(x=r0.valeur, line=dict(color=c.ORANGE, width=2, dash="dash"), layer="below")
        fig.add_annotation(x=r0.valeur, y=1.0, yref="paper", yanchor="bottom", showarrow=False,
                           text=f"<b>France : {fmt(r0.valeur)}{' %' if pct else ''}</b>",
                           font=dict(size=12, color=c.ORANGE))
    fig.update_layout(height=110 + 38 * len(V), margin=dict(r=40, t=34),
                      xaxis=dict(range=[0, haut * 1.3], showgrid=True, gridcolor=c.GRILLE, title=unite),
                      yaxis=dict(showgrid=False, tickfont=dict(size=12, color=c.MARINE)))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
    if len(nd):
        st.caption("Non disponible : " + " ; ".join(f"{r.territoire}" + (f" ({r.commentaire})" if r.commentaire
                                                                        else "") for r in nd.itertuples()))
with d:
    # la lecture ne compare que des valeurs comparables entre elles (même millésime, même méthode)
    comparables = (V.comparable == "O").sum() >= 2
    Vc = V[V.comparable == "O"] if comparables else V
    lo, hi = Vc.iloc[0], Vc.iloc[-1]
    u = " %" if pct else ""
    m = lambda r: r.marque if isinstance(r.marque, str) else ""
    lect = [("parmi les territoires comparables" if comparables else "parmi les territoires renseignés — dont les "
             "chiffres ne sont pas strictement comparables entre eux")
            + f", l'indicateur va de <b>{m(lo)}{fmt(lo.valeur)}{u}</b> ({lo.territoire}) "
            f"à <b>{m(hi)}{fmt(hi.valeur)}{u}</b> ({hi.territoire})"
            + (f", pour une moyenne nationale de {fmt(ref.iloc[0].valeur)}{u}." if len(ref) else ".")]
    carte("Ce graphique montre que…", lect, "orange")
    reserves = []
    if (V.comparable == "N").any():
        reserves.append("Les barres claires ne sont pas strictement comparables aux autres : millésime ancien, "
                        "seuil ou méthode différents. Leur année est indiquée.")
    if V.marque.eq("≈").any():
        reserves.append("« ≈ » : valeur lue sur un graphique de la source, à quelques points près.")
    if V.marque.eq(">").any():
        reserves.append("« > » : la source ne donne qu'un minimum.")
    reserves.append("Une moyenne territoriale ne dit pas comment l'écart se répartit entre les habitants d'un "
                    "même territoire.")
    carte("À lire avec prudence", reserves, "bleugris")
pied(" ; ".join(dict.fromkeys(S.source)) + f" — millésime de référence : {S.millesime.mode().iloc[0]}",
     renvoi=RENVOI)

# ───────────────────────────────────────── 2 · un territoire, tous les indicateurs
st.markdown("### Un territoire, tous ses indicateurs")
terrs = [t for t in dict.fromkeys(I[(I.reference == "non") & I.valeur.notna()].territoire)
         if "/" not in t and t not in ("COM", "Ensemble outre-mer")]
choix = st.selectbox("Territoire", terrs, label_visibility="collapsed")
lignes = []
for n, r in noms.iterrows():
    x = I[(I.num == n) & (I.territoire == choix)]
    f_ = I[(I.num == n) & (I.reference == "oui")]
    if x.empty or pd.isna(x.valeur.iloc[0]):
        continue
    xv, fv = x.valeur.iloc[0], (f_.valeur.iloc[0] if len(f_) else None)
    lignes.append({"Indicateur": f"{r.indicateur} ({r.unite})",
                   choix: f"{x.marque.iloc[0] if isinstance(x.marque.iloc[0], str) else ''}{fr(xv, 2 if n == 13 else 1)}",
                   "France": fr(fv, 2 if n == 13 else 1) if fv is not None else "—",
                   "Écart": (f"× {fr(xv / fv, 1)}" if fv else "—"),
                   "Année": str(x.millesime.iloc[0]),
                   "Comparable": "oui" if x.comparable.iloc[0] == "O" else "non"})
st.dataframe(pd.DataFrame(lignes), hide_index=True, width="stretch")
st.caption("« Écart » : la valeur du territoire divisée par la moyenne nationale. Au-dessus de 1, le territoire est "
           "plus haut que la moyenne — ce qui est un retard pour la pauvreté ou le chômage, une avance pour la "
           "densité de médecins ou l'accueil de la petite enfance.")
pied("Socle « chiffres clés » de la Partie IV : Sénat, commission d'enquête sur les inégalités systémiques outre-mer "
     "(2026), d'après INSEE, DEPP, DGS, DREES, CNAF, Assurance maladie, ISEE, ISPF, STSEE", renvoi=RENVOI)

# ───────────────────────────────────────── 3 · l'indice intégré de précarité
st.markdown("### Un indice pour comparer les cinq départements")
X = lire("territoires_precarite.csv")
XD = lire("territoires_precarite_detail.csv")
DIMS = ["Revenus", "Emploi", "Éducation", "Santé", "Vie chère"]
ind = X[X.dimension == "Indice intégré"].set_index("territoire").indice
g, d = st.columns([1.65, 1], gap="large")
with g:
    vue_i = st.radio("Afficher", ["L'indice", "Ses cinq dimensions", "Le classement"], horizontal=True,
                     label_visibility="collapsed")
    fig = go.Figure()
    boucle = DROM + DROM[:1]
    if vue_i == "Le classement":
        R = ind.sort_values()
        c.barres(fig, R.index, R.values, [c.ORANGE if t == R.index[-1] else c.BLEU_GRIS for t in R.index],
                 width=0.6, text=[f"<b>{fr(v, 2)}</b>" for v in R.values], textcolor=c.MARINE, textsize=13,
                 hover="<b>%{y}</b> : %{x:.2f} fois la situation nationale<extra></extra>")
        fig.add_vline(x=1, line=dict(color=c.VERT, width=2, dash="dash"), layer="below")
        fig.add_annotation(x=1, y=1.0, yref="paper", yanchor="bottom", showarrow=False,
                           text="<b>France = 1</b>", font=dict(size=12, color=c.VERT))
        fig.update_layout(height=360, margin=dict(r=40, t=34), showlegend=False,
                          xaxis=dict(range=[0, R.max() * 1.25], showgrid=True, gridcolor=c.GRILLE,
                                     title="indice intégré (1 = la situation nationale)"),
                          yaxis=dict(showgrid=False, tickfont=dict(size=13, color=c.MARINE)))
    else:
        if vue_i == "L'indice":
            r = [ind[t] for t in boucle]
            fig.add_trace(go.Scatterpolar(r=r, theta=boucle, mode="lines+markers+text", fill="toself",
                                          name="indice intégré", line=dict(color=c.ORANGE, width=3),
                                          fillcolor=c.teinte(c.ORANGE, 0.22), marker=dict(size=7),
                                          text=[f"<b>{fr(v, 2)}</b>" for v in r[:-1]] + [""],
                                          textposition="top center", textfont=dict(size=13, color=c.ORANGE),
                                          hovertemplate="<b>%{theta}</b> : %{r:.2f}<extra></extra>"))
            rmax = 3.0
        else:
            # cinq séries : la couleur ne suffit pas, chaque dimension a aussi son marqueur
            STYLE = {"Revenus": (c.MARINE, "circle"), "Emploi": (c.ORANGE, "square"),
                     "Éducation": (c.VERT, "diamond"), "Santé": (c.BLEU, "triangle-up"),
                     "Vie chère": (c.BRUN, "x")}
            for dim in DIMS:
                v = X[X.dimension == dim].set_index("territoire").indice
                col, sym = STYLE[dim]
                fig.add_trace(go.Scatterpolar(r=[v[t] for t in boucle], theta=boucle, mode="lines+markers",
                                              name=dim, line=dict(color=col, width=2.2),
                                              marker=dict(size=8, symbol=sym, color=col),
                                              hovertemplate="<b>%{theta}</b> · " + dim + " : %{r:.2f}<extra></extra>"))
            rmax = 5.6
        fig.add_trace(go.Scatterpolar(r=[1] * len(boucle), theta=boucle, mode="lines", name="France = 1",
                                      line=dict(color=c.VERT, width=2, dash="dash"), hoverinfo="skip"))
        fig.update_layout(height=470, margin=dict(l=40, r=40, t=50, b=30),
                          legend=dict(orientation="h", y=1.08, yanchor="bottom", x=0),
                          polar=dict(bgcolor=c.BLANC,
                                     radialaxis=dict(range=[0, rmax], showline=False, gridcolor=c.GRILLE,
                                                     tickfont=dict(size=10, color=c.GRIS), angle=54,
                                                     tickangle=54, nticks=4),
                                     angularaxis=dict(direction="clockwise", rotation=90, gridcolor=c.GRILLE,
                                                      linecolor=c.FILET,
                                                      tickfont=dict(size=13, color=c.MARINE))))
    st.plotly_chart(fig, width="stretch", config=c.CONFIG)
with d:
    pire = ind.idxmax()
    carte("Ce graphique montre que…",
          [f"dans les cinq départements, la précarité dépasse partout la situation nationale : de "
           f"{fr(ind.min(), 1)} fois ({ind.idxmin()}) à {fr(ind.max(), 1)} fois ({pire}).",
           "Mayotte et la Guyane se détachent ; la Guadeloupe, La Réunion et la Martinique sont proches. Le plus "
           "grand écart est l'éducation : l'illettrisme y est deux à cinq fois plus fréquent qu'en moyenne."],
          "orange")
    carte("Comment c'est calculé",
          ["Neuf indicateurs, chacun rapporté à la situation nationale (pour les prix, à l'Hexagone) : pauvreté et inégalités (revenus) ; chômage, "
           "chômage des jeunes, jeunes sans emploi ni formation (emploi) ; illettrisme (éducation) ; mortalité "
           "infantile, incapacités des 65 ans et plus (santé) ; prix alimentaires (vie chère).",
           "Moyenne géométrique dans chaque dimension, puis entre les cinq dimensions, à poids égaux. 1 = la "
           "situation nationale ; 2 = deux fois plus défavorable."], "bleugris")
    carte("Pourquoi seulement cinq territoires",
          ["Les collectivités du Pacifique, Saint-Martin, Saint-Barthélemy, Saint-Pierre-et-Miquelon et "
           "Wallis-et-Futuna n'ont que deux à six de ces indicateurs, souvent mesurés autrement : un indice les "
           "comparerait à tort.",
           "Dans un radar, l'aire dépend de l'ordre des pointes : le classement reste la lecture exacte."], "bleu")
pied("Calcul du CLSE à partir du socle « chiffres clés » de la Partie IV (Sénat 2026, d'après INSEE, DEPP, DGS, "
     "DREES). Millésimes 2019 à 2026 ; jeunes sans emploi ni formation lus sur un graphique ; inégalités de la Guyane "
     "en 2017", statut="Reconstitué", renvoi=RENVOI)

# ───────────────────────────────────────── 4 · richesse et effort
st.markdown("### Des réalités très hétérogènes, un effort qui ne suit pas les besoins")
T = E[E.cp_2026_eur.notna()].copy()
vue = st.radio("Afficher", ["Les territoires", "La richesse produite", "L'effort de l'État", "Pour 1 € dépensé"],
               horizontal=True, label_visibility="collapsed")
# les silhouettes demandent toute la largeur ; les trois autres vues gardent la colonne et les cartes à droite
if vue == "Les territoires":
    g, d = st.container(), None
else:
    g, d = st.columns([1.65, 1], gap="large")
with g:
    # l'axe est gradué en milliers d'euros (le graphique fait 280 px sur un écran moyen) ; les étiquettes gardent
    # les montants exacts
    if vue == "Les territoires":
        silhouettes(T)
    elif vue == "La richesse produite":
        T = T.sort_values("pib_hab_eur")
        x, txt, coul, titre = (T.pib_hab_eur / 1000,
                               [f"{fr(v, 0)} € ({a[:4]})" for v, a in zip(T.pib_hab_eur, T.annee_pib)],
                               c.BLEU_GRIS, "PIB par habitant (milliers d'€, dernier millésime)")
        fr_ref = E[E.territoire.str.startswith("France")].pib_hab_eur.iloc[0]
    elif vue == "L'effort de l'État":
        T = T.sort_values("effort_hab_eur")
        x, txt, coul, titre = (T.effort_hab_eur / 1000, [f"{fr(v, 0)} €" for v in T.effort_hab_eur], c.BLEU,
                               "Crédits de l'État par habitant, 2026 (milliers d'€)")
        fr_ref = None
    else:
        T = T.sort_values("richesse_pour_1_euro")
        x, txt, coul, titre = (T.richesse_pour_1_euro, [f"{fr(v, 1)} €" for v in T.richesse_pour_1_euro], c.ORANGE,
                               "Richesse produite pour 1 € dépensé par l'État")
        fr_ref = None
    if vue != "Les territoires":
        fig = go.Figure()
        c.barres(fig, T.territoire, x, coul, text=txt, textcolor=c.MARINE,
                 hover="<b>%{y}</b> : %{text}<extra></extra>")
        if fr_ref:
            fig.add_vline(x=fr_ref / 1000, line=dict(color=c.ORANGE, width=2, dash="dash"), layer="below")
            fig.add_annotation(x=fr_ref / 1000, y=1.0, yref="paper", yanchor="bottom", showarrow=False,
                               text=f"<b>France : {fr(fr_ref, 0)} €</b>", font=dict(size=12, color=c.ORANGE))
        fig.update_layout(height=520, margin=dict(r=60, t=34),
                          xaxis=dict(title=titre, range=[0, x.max() * 1.5], showgrid=True, gridcolor=c.GRILLE,
                                     nticks=5),
                          yaxis=dict(showgrid=False, tickfont=dict(size=12, color=c.MARINE)))
        st.plotly_chart(fig, width="stretch", config=c.CONFIG)
cs = st.columns(3, gap="medium") if d is None else [d, d, d]
carte("De 1 à 7,5 — l'écart de richesse",
      ["De 11 977 € de PIB par habitant à Mayotte à 90 103 € à Saint-Barthélemy : il n'y a pas « un » "
       "outre-mer, mais des réalités très hétérogènes. Le PIB par habitant mesure la richesse produite sur le "
       "territoire, pas le niveau de vie de ses habitants."], "bleugris", cs[0])
carte("En euros par habitant",
      ["Mayotte, le territoire le plus pauvre, reçoit 6 435 € par habitant : moins que La Réunion (7 949 €), la "
       "Guadeloupe (7 681 €) ou la Martinique (7 512 €), plus de deux fois plus riches. Seule la Guyane, parmi "
       "les départements, reçoit davantage (10 173 €)."], "bleu", cs[1])
carte("Pour 1 € dépensé par l'État",
      ["le territoire produit 1,1 € de richesse à Wallis-et-Futuna, 1,9 € à Mayotte, 23,6 € à "
       "Saint-Barthélemy.",
       "<b>Plus ce nombre est bas, plus l'économie tient à la dépense publique.</b> Ce n'est pas un meilleur "
       "service rendu : c'est une dépendance."], "orange", cs[2])
pied("DPT Outre-mer 2026, annexe territoriale (CP) ; INSEE, ISEE, ISPF, populations ; INSEE, CEROM, IEOM, IEDOM, PIB "
     "par habitant. Millésimes du PIB différents (2015 à 2024) : écarts indicatifs. L'INSEE compte Saint-Martin "
     "avec la Guadeloupe ; crédits non répartis et Terres australes hors calcul", statut="Estimé", renvoi=RENVOI)

st.markdown("##### Télécharger")
b = st.columns(3)
telecharger(b[0], "Données · 15 indicateurs par territoire", "territoires_indicateurs.csv")
telecharger(b[1], "Données · l'indice de précarité", "territoires_precarite_detail.csv")
telecharger(b[2], "Données · richesse et effort", "territoires_pib_effort.csv")
