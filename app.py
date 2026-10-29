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
from composants import carte, entete    # noqa: E402

# (adresse, mot du menu, question de Priscillia, contenu prévu)
ECRANS = [
    ("histoire", "L'histoire", "D'où vient le ministère des Outre-mer ?",
     "Une frise historique et quelques chiffres de contexte."),
    ("fonctionnement", "Le fonctionnement", "Comment fonctionne le ministère aujourd'hui ?",
     "Son administration, ses effectifs, ses deux programmes, son rôle de coordination."),
    ("ministres", "Les ministres", "Qui a dirigé le ministère ?",
     "Personnes, mandats, durée, femmes, ancrage ultramarin, premier ministre ultramarin."),
    ("budget", "Le budget", "Quel pouvoir budgétaire réel a le ministère ?",
     "De l'effort de l'État aux crédits que le ministère décide vraiment."),
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
    entete("Le compagnon du rapport", "Le ministère des Outre-mer, rendu lisible",
           "Huit questions, quelques chiffres sourcés pour chacune, et un renvoi vers le rapport du CLSE "
           "pour aller plus loin.")
    cols = st.columns(2, gap="large")
    for i, (cle, _, q, quoi) in enumerate(ECRANS):
        with cols[i % 2]:
            fait = cle in CONSTRUITS
            carte(f"Question {i + 1}" + ("" if fait else " · en préparation"), [f"<b>{q}</b>", quoi],
                  "orange" if fait else "bleugris")
    st.caption("Maquette de travail — écrans 2, 3 et 4 construits.")


def a_venir(numero, question, quoi):
    def page():
        c.css()
        entete(f"Écran {numero}", question, quoi, "bleugris")
        st.info("Écran en préparation.")
    return page


pages = [st.Page(accueil, title="Accueil", url_path="accueil", default=True)]
CONSTRUITS = {"fonctionnement": "ecrans/e2_fonctionnement.py", "ministres": "ecrans/e3_ministres.py",
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
