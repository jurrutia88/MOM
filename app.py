# -*- coding: utf-8 -*-
"""CLSE_MOM — le compagnon numérique du rapport du CLSE sur le ministère des Outre-mer.

Huit écrans, ceux de l'architecture de Priscillia Ludosky (19 août 2026), formulés
comme des questions. Données : `donnees/`, écrites par `_scripts/exporter_socle.py`.

Lancement local :  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Le ministère des Outre-mer en chiffres — CLSE", page_icon="🌊",
                   layout="wide", initial_sidebar_state="auto")     # replié sur téléphone

import charte as c                      # noqa: E402  (après set_page_config)
from composants import NBSP, entete, fond, fr, fr_typo, lire    # noqa: E402

# (adresse, mot du menu, question de Priscillia, contenu prévu)
ECRANS = [
    ("histoire", "L'histoire", "D'où vient le ministère des Outre-mer ?",
     "Une frise historique et quelques chiffres de contexte."),
    ("fonctionnement", "Le fonctionnement", "Comment fonctionne le ministère aujourd'hui ?",
     "Son administration, ses attributions, et ce qu'il reste à payer."),
    ("ministres", "Les ministres", "Qui a dirigé le ministère ?",
     "Rang, rattachement, durée des mandats, femmes, ancrage ultramarin."),
    ("budget", "Le budget", "Quel pouvoir budgétaire réel a le ministère ?",
     "De l'effort de l'État aux crédits que le ministère décide vraiment, action par action."),
    ("statuts", "Les statuts", "Pourquoi les 13 outre-mer n'ont-ils pas tous le même statut ?",
     "La carte des statuts français, puis la lecture européenne."),
    ("territoires", "Les territoires", "Quels impacts concrets selon les territoires ?",
     "Pauvreté, prix alimentaires, importations, chômage — territoire par territoire."),
    ("representation", "La représentation", "Comment les outre-mer sont-ils représentés ?",
     "Les sièges à l'Assemblée nationale, rapportés à la population."),
    ("transformer", "Transformer", "Que faut-il transformer ?",
     "Les constats qui comptent, les scénarios et les organes."),
]


def accueil():
    c.css()
    fond(voile=0.42)
    cas = lire("budget_cascade.csv").set_index("etape")
    n_terr = len(lire("statuts.csv"))
    effort, marge = cas.loc[1, "haut_eur"] / 1e9, cas.loc[5, "part_dpt_pct"]
    st.markdown(f"""<style>
    .accueil {{ padding: 18px 10px 18px 10px;
                margin-top: 8px; }}
    .accueil .surtitre {{ font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase;
                          color:{c.VERT}; }}
    .accueil h1 {{ font-size: clamp(1.8rem, 4vw, 2.7rem); line-height:1.12; margin:.3rem 0 .5rem 0; padding:0;
                   color:{c.MARINE}; font-weight:900; }}
    .accueil .sous {{ color:{c.GRIS}; font-style:italic; font-size:1.05rem; line-height:1.5; max-width:640px; }}
    .accueil .chiffres {{ display:flex; flex-wrap:wrap; gap:0; margin:22px 0 6px 0; }}
    .accueil .chiffre {{ flex:1 1 160px; padding:2px 18px 6px 0; margin-right:18px; border-right:1px solid {c.FILET}; }}
    .accueil .chiffre:last-child {{ border-right:none; }}
    .accueil .chiffre b {{ display:block; font-size:1.7rem; font-weight:700; color:{c.MARINE}; line-height:1.1; }}
    .accueil .chiffre span {{ font-size:.85rem; color:{c.GRIS}; line-height:1.35; }}
    .questions {{ display:grid; grid-template-columns:1fr 1fr; column-gap:36px; margin-top:22px; }}
    .questions a, .questions .q {{ display:grid; grid-template-columns:52px 1fr 22px; gap:10px; align-items:start;
        padding:16px 4px 16px 0; border-top:1px solid {c.FILET}; text-decoration:none !important;
        color:{c.MARINE} !important; transition: background .15s; }}
    .questions .num {{ font-size:1.9rem; font-weight:300; color:{c.VERT}; line-height:1; letter-spacing:-.02em; }}
    .questions .titre {{ display:block; font-weight:700; font-size:1.06rem; line-height:1.3; }}
    .questions .desc {{ display:block; color:{c.GRIS}; font-size:.88rem; line-height:1.4; margin-top:3px; }}
    .questions .fleche {{ color:{c.VERT}; font-size:1.2rem; opacity:.35; transition: transform .15s, opacity .15s; }}
    .questions a:hover {{ background: linear-gradient(90deg, {c.teinte(c.VERT, 0.08)}, rgba(255,255,255,0)); }}
    .questions a:hover .fleche {{ opacity:1; transform: translateX(4px); }}
    .questions a:hover .titre {{ color:{c.VERT}; }}
    .questions .q.avenir {{ opacity:.55; cursor:default; }}
    .questions .q.avenir .num {{ color:{c.GRIS}; }}
    .questions .bientot {{ display:inline-block; font-size:.66rem; font-weight:700; letter-spacing:.08em;
        text-transform:uppercase; border:1px solid {c.FILET}; padding:0 6px; margin-left:6px; color:{c.GRIS}; }}
    .accueil .note {{ color:{c.GRIS}; font-size:.8rem; font-style:italic; border-top:1px solid {c.FILET};
                      padding-top:8px; margin-top:4px; }}
    @media (max-width: 760px) {{
        .questions {{ grid-template-columns:1fr; }}
        .accueil {{ padding: 18px 14px 12px 14px; }}
        .accueil .chiffre {{ border-right:none; border-bottom:1px solid {c.FILET}; margin-right:0; padding:6px 0; }}
    }}
    </style>""", unsafe_allow_html=True)
    items = []
    for i, (cle, _, q, quoi) in enumerate(ECRANS, start=1):
        corps = (f'<span class="num">{i:02d}</span><span><span class="titre">{fr_typo(q)}</span>'
                 f'<span class="desc">{fr_typo(quoi)}</span></span>')
        if cle in CONSTRUITS:
            items.append(f'<a href="/{cle}" target="_self">{corps}<span class="fleche">→</span></a>')
        else:
            items.append(f'<div class="q avenir">{corps.replace("</span></span>", "")}'
                         f'<span class="bientot">en préparation</span></span></span><span></span></div>')
    st.markdown(
        f'<div class="accueil"><div class="surtitre">Le compagnon du rapport du CLSE</div>'
        f'<h1>Le ministère des Outre-mer, rendu lisible</h1>'
        f'<div class="sous">{fr_typo("Huit questions, quelques chiffres sourcés pour chacune, et un renvoi vers le rapport pour aller plus loin.")}</div>'
        f'<div class="chiffres">'
        f'<div class="chiffre"><b>{n_terr}</b><span>territoires d\'outre-mer, aux statuts différents</span></div>'
        f'<div class="chiffre"><b>{fr(effort, 2)}{NBSP}Md€</b><span>consacrés par l\'État aux outre-mer en 2026, '
        f'tous ministères confondus</span></div>'
        f'<div class="chiffre"><b>{fr(marge, 2)}{NBSP}%</b><span>de cet effort réellement arbitrés par le ministère'
        f'</span></div></div>'
        f'<div class="questions">{"".join(items)}</div>'
        f'<div class="note">Montants en crédits de paiement. En fond : les contours des treize territoires, chacun à '
        f'sa propre échelle (Natural Earth).</div></div>',
        unsafe_allow_html=True)


def a_venir(numero, question, quoi):
    def page():
        c.css()
        entete(f"Écran {numero}", question, quoi, "bleugris")
        st.info("Écran en préparation.")
    return page


pages = [st.Page(accueil, title="Accueil", url_path="accueil", default=True)]
CONSTRUITS = {"histoire": "ecrans/e1_histoire.py", "fonctionnement": "ecrans/e2_fonctionnement.py",
              "statuts": "ecrans/e5_statuts.py", "territoires": "ecrans/e6_territoires.py",
              "representation": "ecrans/e7_representation.py", "ministres": "ecrans/e3_ministres.py",
              "budget": "ecrans/e4_budget.py"}
for i, (cle, mot, q, quoi) in enumerate(ECRANS, start=1):
    if cle in CONSTRUITS:
        pages.append(st.Page(CONSTRUITS[cle], title=f"{i} · {mot}", url_path=cle))
    else:
        pages.append(st.Page(a_venir(i, q, quoi), title=f"{i} · {mot}", url_path=cle))

st.sidebar.markdown(f"<div style='font-weight:700;letter-spacing:.09em;text-transform:uppercase;"
                    f"font-size:.74rem;color:{c.VERT}'>CLSE · rapport MOM</div>", unsafe_allow_html=True)
st.navigation(pages).run()
st.sidebar.caption("Données : documents budgétaires de l'État (PLF, DPT, PAP), JORF, INSEE, IEDOM. "
                   "Montants en crédits de paiement.")
