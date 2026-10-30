# -*- coding: utf-8 -*-
"""Écran 3 — Qui a dirigé le ministère des Outre-mer ?

Textes repris du deck du diagnostic (23 septembre 2026), diapositives « Les ministres » et
« Qui occupe le poste », validés par José. Règle d'ancrage du 17 septembre 2026 : seul compte
l'ancrage antérieur à la nomination ; « autre forme » jamais confondue avec la naissance.
"""
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import charte as c
from composants import carte, entete, fond, fr, glossaire, lire, pied, sigle, telecharger, tuile

RENVOI = "partie « Rôle et histoire du ministère »"        # intitulé définitif à caler sur le rapport
SOURCE = "Journal officiel — base des 63 mandats arrêtée au 23 juin 2026"

c.css()
fond(["Saint-Martin", "Saint-Barthélemy", "Martinique"])
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
       f"{pers} personnes et {n} mandats depuis 1959. À quel rang, combien de temps elles restent, et qui elles sont.")
glossaire(["mandat", "rang", "rattaché à l'Intérieur", "ancrage"])

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
    carte("Ce graphique montre que…",
          [f"sous Emmanuel Macron, le portefeuille change de titulaire plus vite que jamais : {mac.mandats} "
           f"mandats et {mac.ministres} ministres en neuf ans, {fr(mac.mandats_par_an, 2)} mandat par année de "
           f"présidence — le rythme le plus rapide de la Ve République.",
           f"La durée moyenne tombe à {mac.duree_moyenne_j} jours, contre 634 sous Valéry Giscard d'Estaing."],
          "orange")
pied(SOURCE + ". Un mandat = une nomination dans un gouvernement ; 2022-2024 : deux titulaires simultanés",
     renvoi=RENVOI)

# ───────────────────────────────────────── 2 · le rang et le rattachement, mandat après mandat
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

# ───────────────────────────────────────── 3 · qui occupe le poste
st.markdown("### Qui occupe le poste ?")
g, d = st.columns([1.65, 1], gap="large")
ANCRAGE = {"né outre-mer": c.ORANGE, "autre forme": "#A08F76", "aucun": c.FILET}
with g:
    # une ligne par président, une étiquette par mandat dans l'ordre chronologique : le nom et les années
    M = M.sort_values("debut")
    der = M.debut.max()

    def annees(r):
        a, b = r.debut[:4], r.fin[:4]
        if r.debut == der:                       # la ministre en fonction à la date d'arrêt de la base
            return f"depuis {a}"
        return a if a == b else f"{a}-{b}"

    def puce(r):
        col = ANCRAGE[r.ancrage]
        femme = f'<span class="f" style="color:{c.MARINE}">●</span>' if r.sexe == "F" else ""
        info = escape(f"{r.fonction} · gouvernement {r.gouvernement} · {r.duree_jours} jours")
        return (f'<span class="puce" title="{info}" style="background:{c.teinte(col, 0.16)};'
                f'border-left:4px solid {col}">{femme}{escape(r.ministre)} <i>({annees(r)})</i></span>')

    legende = " ".join(f'<span class="puce" style="background:{c.teinte(k, 0.16)};border-left:4px solid {k}">'
                       f'{"aucun ancrage" if a == "aucun" else a}</span>' for a, k in ANCRAGE.items())
    lignes = "".join(
        f'<div class="poste"><div class="pres">{p}<span>{a}–{"" if pd.isna(b) else int(b)}</span></div>'
        f'<div>{"".join(puce(r) for r in M[M.president == p].itertuples())}</div></div>'
        for p, a, b in zip(P.president, P.debut, P.fin))
    st.markdown(f"""<style>
        .postes .puce {{ display:inline-block; font-size:.84rem; line-height:1.3; padding:3px 8px; margin:0 5px 5px 0;
                         color:{c.MARINE}; cursor:help; }}
        .postes .puce i {{ color:{c.GRIS}; font-style:normal; white-space:nowrap; }}
        .postes .puce .f {{ font-size:.7rem; margin-right:4px; vertical-align:1px; }}
        .postes .poste {{ display:grid; grid-template-columns:118px 1fr; gap:10px; padding:7px 0;
                          border-top:1px solid {c.GRILLE}; }}
        .postes .pres {{ font-weight:700; font-size:.9rem; color:{c.MARINE}; }}
        .postes .pres span {{ display:block; font-weight:400; font-size:.78rem; color:{c.GRIS}; }}
        .postes .leg {{ margin-bottom:6px; font-size:.8rem; color:{c.GRIS}; }}
        @media (max-width:640px) {{ .postes .poste {{ grid-template-columns:1fr; gap:4px; }} }}
        </style>""", unsafe_allow_html=True)
    # sans retour à la ligne : une ligne indentée deviendrait un bloc de code pour le Markdown
    st.markdown(f'<div class="postes"><div class="leg">{legende} <span class="puce" style="background:#fff">'
                f'<span class="f" style="color:{c.MARINE}">●</span>une femme</span></div>{lignes}</div>',
                unsafe_allow_html=True)
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
b = st.columns(3)
telecharger(b[0], "Figure · mandats par président", "mandats_par_president.png", figure=True)
telecharger(b[1], "Figure · qui occupe le poste", "representativite_des_ministres.png", figure=True)
telecharger(b[2], "Données · les 63 mandats", "ministres_mandats.csv")
