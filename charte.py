# -*- coding: utf-8 -*-
"""Charte du deck du diagnostic (23 septembre 2026), portée dans Streamlit et Plotly.

Lato partout, fond blanc. Les encadrés sont des cartes à fond teinté de leur accent
qui s'éclaircit vers le blanc, avec un filet dégradé en tête ; les intitulés sont
en petites capitales espacées ; un chiffre est souligné d'un dégradé.
L'orange signale ce qui fragilise — ici la part que le ministère décide réellement.
"""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

MARINE = "#1D323F"
BLEU_GRIS = "#465D6C"
VERT = "#2A7C6F"
ORANGE = "#FC5A1F"
BLEU = "#3F6E8C"
BRUN = "#5E4743"
SABLE = "#E6DFD3"
GRIS = "#5B6B77"
FILET = "#C9C4BB"
GRILLE = "#ECEAE6"
BLANC = "#FFFFFF"

# l'éclairci de chaque accent : le bout clair des filets et des barres en dégradé
CLAIR = {VERT: "#A9CEC6", BLEU: "#B7CAD6", ORANGE: "#FDC3AC", MARINE: "#A3ABB2",
         BLEU_GRIS: "#C5CBD0", BRUN: "#CBBAB4"}


def teinte(c, f=0.10):
    """La couleur mêlée de blanc : le fond très clair des cartes."""
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(int(round(x + (255 - x) * (1 - f))) for x in (r, g, b))


def css():
    """À appeler une fois par page, avant tout contenu."""
    blocs = []
    for nom, c in (("vert", VERT), ("orange", ORANGE), ("bleu", BLEU), ("marine", MARINE),
                   ("brun", BRUN), ("bleugris", BLEU_GRIS)):
        blocs.append(f"""
        .carte.{nom} {{ background: linear-gradient(180deg, {teinte(c)} 0%, #FFFFFF 100%); }}
        .carte.{nom}::before {{ background: linear-gradient(90deg, {c}, {CLAIR[c]}); }}
        .carte.{nom} .intitule, .tuile.{nom} .valeur, .entete.{nom} .surtitre {{ color: {c}; }}
        .tuile.{nom} .souligne, .entete.{nom} .filet {{ background: linear-gradient(90deg, {c}, {CLAIR[c]}); }}
        """)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;0,900;1,400&display=swap');
    html, body, .stApp, [class*="css"], .stMarkdown, button, input, select, textarea {{
        font-family: 'Lato', sans-serif !important; color: {MARINE}; }}
    .stApp {{ background: #FFFFFF; }}
    .block-container {{ max-width: 1180px; padding-top: 2.2rem; }}
    h1, h2, h3 {{ font-family: 'Lato', sans-serif !important; color: {MARINE}; font-weight: 700; }}

    .entete .filet {{ width: 56px; height: 3px; margin-bottom: 6px; }}
    .entete .surtitre {{ font-size: .78rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; }}
    .entete h1 {{ font-size: 2rem; line-height: 1.2; margin: .15rem 0 .35rem 0; padding: 0; }}
    .entete .sous {{ color: {GRIS}; font-style: italic; font-size: 1.02rem; line-height: 1.45; margin-bottom: .6rem; }}

    .carte {{ position: relative; padding: 18px 20px 14px 20px; margin: 4px 0 14px 0; }}
    .carte::before {{ content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; }}
    .carte .intitule {{ font-size: .74rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase;
                        margin-bottom: 8px; }}
    .carte p {{ font-size: .97rem; line-height: 1.55; margin: 0 0 .5rem 0; color: {MARINE}; }}
    .carte p:last-child {{ margin-bottom: 0; }}

    .tuile {{ padding: 4px 0 10px 0; }}
    .tuile {{ min-width: 0; }}
    .tuile .valeur {{ font-size: clamp(1.45rem, 2.4vw, 2.35rem); font-weight: 700; line-height: 1.08;
                      overflow-wrap: anywhere; }}
    .tuile .souligne {{ width: 72px; height: 3px; margin: 8px 0 8px 0; }}
    .tuile .legende {{ color: {GRIS}; font-size: .9rem; line-height: 1.4; }}
    .tuile .legende b {{ color: {MARINE}; }}

    .pied {{ color: {GRIS}; font-size: .8rem; line-height: 1.5; font-style: italic;
             border-top: 1px solid {GRILLE}; padding-top: 6px; margin: 2px 0 6px 0; }}
    .pied .statut {{ font-style: normal; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
                     font-size: .7rem; padding: 1px 7px; border: 1px solid {VERT}; color: {VERT}; margin-right: 6px; }}
    .pied .statut.estime {{ border-color: {ORANGE}; color: {ORANGE}; }}
    .pied .renvoi {{ font-style: normal; color: {BLEU}; }}
    abbr {{ text-decoration: underline dotted {FILET}; cursor: help; }}
    {''.join(blocs)}
    @media (max-width: 640px) {{
        .entete h1 {{ font-size: 1.55rem; }}
        .tuile .valeur {{ font-size: 2rem; }}
    }}
    @media (min-width: 641px) and (max-width: 1100px) {{
        .tuile .valeur {{ font-size: 1.55rem; }}
    }}
    </style>
    """, unsafe_allow_html=True)


# ───────────────────────────────────────────── Plotly : le gabarit des figures
pio.templates["clse"] = go.layout.Template(layout=go.Layout(
    font=dict(family="Lato, sans-serif", color=MARINE, size=14),
    paper_bgcolor=BLANC, plot_bgcolor=BLANC,
    colorway=[MARINE, VERT, ORANGE, BLEU, BRUN, BLEU_GRIS],
    margin=dict(l=10, r=20, t=20, b=10),
    xaxis=dict(showgrid=False, showline=True, linecolor=FILET, ticks="", tickfont=dict(color=GRIS), zeroline=False),
    yaxis=dict(showgrid=True, gridcolor=GRILLE, showline=True, linecolor=FILET, ticks="",
               tickfont=dict(color=GRIS), zeroline=False),
    hoverlabel=dict(bgcolor=BLANC, bordercolor=FILET, font=dict(family="Lato, sans-serif", color=MARINE, size=13)),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=GRIS)),
    separators=", ",                      # virgule décimale, espace des milliers
))
pio.templates.default = "clse"

CONFIG = {"displaylogo": False, "locale": "fr",
          "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d", "zoomIn2d", "zoomOut2d"],
          "toImageButtonOptions": {"format": "png", "scale": 2}}
