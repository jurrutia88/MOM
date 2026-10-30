# -*- coding: utf-8 -*-
"""Écran 2 — Comment fonctionne le ministère aujourd'hui ?

Textes repris du deck du diagnostic (23 septembre 2026), diapositives « D'où il vient » (attributions),
« Ce qu'il est » (organisation et coût) et « La mission Outre-mer », validés par José.
"""
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import carte, entete, fr, glossaire, lire, pied, sigle, telecharger, tuile

RENVOI = "partie « Comment fonctionne le ministère »"       # intitulé définitif à caler sur le rapport

import textwrap


def deux_lignes(t, n=26):
    """Un libellé d'axe sur deux lignes au plus : les noms d'actions débordent sur un téléphone."""
    return "<br>".join(textwrap.wrap(t, n)[:2]) if len(t) > n else t


c.css()
A = lire("fonctionnement_actions.csv")
A["libelle"] = A.action.map(deux_lignes)
R = lire("restes_serie.csv")
K = lire("fonctionnement_chiffres.csv").set_index("indicateur").valeur
mission = A.cp_eur.sum()
part_contrainte = 100 * A.contraint_eur.sum() / mission
rap_2025 = R.restes_a_payer_m.iloc[-1]

entete("Écran 2 · Le fonctionnement", "Comment fonctionne le ministère aujourd'hui ?",
       "Une petite administration, deux programmes budgétaires, et des attributions qui tiennent à un décret.")
glossaire(["DGOM", "P138", "P123", "LODEOM", "CP", "restes à payer"])

t = st.columns(4)
tuile(t[0], f"≈ {K['Agents de la direction générale des outre-mer']:.0f}",
      f"agents dans sa {sigle('DGOM', 'direction générale')}, répartis en quatre sous-directions")
tuile(t[1], f"{fr(mission / 1e9, 2)} Md€", "de crédits en propre en 2026, en deux programmes", "bleugris")
tuile(t[2], f"{fr(part_contrainte / 10, 0)} € sur 10", "de ces crédits sont engagés d'avance, par la loi ou par "
      "des dotations garanties", "orange")
tuile(t[3], f"{fr(rap_2025 / 1000, 2)} Md€", f"d'engagements pris et non payés fin 2025 : plus que le budget "
      f"d'une année", "orange")
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
                                    "agents</b>, quatre sous-directions, créée en 2013."], "vert", o2)
    carte("Ce que portent ses quatre sous-directions",
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

# ───────────────────────────────────────── 3 · les deux programmes
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
    lodeom = A.set_index("code").loc["138-01"]
    dot = A.set_index("code").loc["123-06"]
    carte("Ce graphique montre que…",
          [f"<b>six euros sur dix sont engagés d'avance</b> : la compensation des exonérations de charges "
           f"({sigle('LODEOM')}, {fr(lodeom.cp_eur / 1e9, 2)} Md€, {fr(lodeom.part_programme_pct, 0)} % du "
           f"programme emploi), qui suit la masse salariale, et la moitié des dotations aux collectivités "
           f"({fr(dot.contraint_eur / 1e6, 0)} M€ sur {fr(dot.cp_eur / 1e6, 0)}).",
           f"En vert, le reste — {fr(A.pilotable_eur.sum() / 1e9, 2)} Md€ : logement, aménagement, continuité "
           f"territoriale, service militaire adapté et mobilité. C'est la seule part que le ministère arbitre d'une "
           f"année sur l'autre."], "orange")
    carte("À savoir", ["La dotation aux collectivités est comptée pour moitié : c'est l'hypothèse, explicite et "
                       "auditée, de la cascade budgétaire de l'écran 4."], "marine")
pied(f"PAP Mission Outre-mer 2026, récapitulation des crédits par programme et action ({sigle('CP')})",
     renvoi=RENVOI)

# ───────────────────────────────────────── 4 · les restes à payer
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
          [f"<b>fin 2025, {fr(rap_2025 / 1000, 2)} Md€ d'engagements pris et non payés : plus que le budget "
           f"d'une année, + 76 % depuis 2017.</b>",
           f"Pourquoi : l'État engage l'opération entière dès la signature et paie au rythme des travaux. Or 62 % "
           f"de ces {sigle('restes à payer')} sont des interventions au profit des collectivités : le paiement suit "
           f"leur ingénierie et leurs chantiers, pas la décision budgétaire.",
           "Et pas seulement : la Cour des comptes relève des projets mal calibrés et des engagements devenus sans "
           "objet, jamais soldés — 534 M€ d'écart pour la seule année 2025."], "orange")
pied("Cour des comptes, notes d'exécution budgétaire de la mission Outre-mer 2013-2025 (tableau n° 13 pour 2025). "
     "2016 et 2022 : montant non publié", renvoi=RENVOI)

st.markdown("##### Télécharger")
b = st.columns(3)
telecharger(b[0], "Figure · la mission par action", "mission_outre_mer_par_action.png", figure=True)
telecharger(b[1], "Figure · les restes à payer", "restes_a_payer.png", figure=True)
telecharger(b[2], "Données · les 12 actions", "fonctionnement_actions.csv")
