# -*- coding: utf-8 -*-
"""Les briques d'un écran : en-tête, tuile chiffre, carte de lecture, pied de source,
glossaire et téléchargements. La profondeur est constante d'un écran à l'autre."""
import os
import re
from html import escape

import pandas as pd
import streamlit as st

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
FIGURES = os.path.join(ICI, "figures")
NBSP = " "

# Glossaire : aucun sigle laissé seul (règle de vulgarisation de Priscillia, 19 août).
# Définitions reprises de sa proposition et de la note budgétaire — à valider.
GLOSSAIRE = {
    "DPT": "Document de politique transversale « Outre-mer » : l'annexe au projet de loi de finances qui "
           "additionne tous les crédits que l'État consacre aux outre-mer, tous ministères confondus.",
    "Mission Outre-mer": "La partie du budget de l'État directement portée par le ministère des Outre-mer. "
                         "Elle compte deux programmes : P138 et P123.",
    "P138": "Programme « Emploi outre-mer » : compensation des exonérations de charges des entreprises "
            "(LODEOM), Service militaire adapté (SMA), mobilité (LADOM), financement de l'économie.",
    "P123": "Programme « Conditions de vie outre-mer » : logement, aménagement et équipements, continuité "
            "territoriale, action sanitaire et sociale, dotations aux collectivités.",
    "LODEOM": "Loi pour le développement économique des outre-mer (2009). Le ministère compense aux "
              "organismes sociaux les exonérations de cotisations qu'elle accorde : la dépense suit l'emploi "
              "et la loi, sans arbitrage annuel.",
    "CP": "Crédits de paiement : l'argent effectivement décaissé dans l'année. C'est la mesure retenue partout "
          "dans cette application.",
    "dépenses fiscales": "Impôts que l'État renonce à percevoir (réductions, exonérations, taux réduits). "
                         "Elles soutiennent les outre-mer hors budget : on les montre à côté des crédits, "
                         "jamais additionnées.",
    "mandat": "Une nomination dans un gouvernement, du décret de nomination à la fin des fonctions. Une même "
              "personne reconduite dans un nouveau gouvernement ouvre un nouveau mandat.",
    "rang": "La place du ministre dans le gouvernement, du plus élevé au plus modeste : ministre d'État, "
            "ministre, ministre délégué, secrétaire d'État. Les deux premiers siègent de plein droit au Conseil "
            "des ministres ; les deux autres passent par le ministre dont ils relèvent.",
    "rattaché à l'Intérieur": "Le portefeuille des outre-mer n'est pas autonome : il est placé auprès du "
                              "ministre de l'Intérieur, qui en a l'autorité.",
    "ancrage": "Un lien avec un territoire d'outre-mer antérieur à la nomination. « Né outre-mer » : la "
               "naissance. « Autre forme » : ascendance, résidence, activité, mandat ou engagement, d'après la "
               "grille d'ancrage du CLSE.",
}


def fr_typo(t):
    """Espaces insécables du français, et un montant ne se coupe jamais."""
    for a, b in ((" »", NBSP + "»"), ("« ", "«" + NBSP), (" :", NBSP + ":"), (" ;", NBSP + ";"),
                 (" ?", NBSP + "?"), (" !", NBSP + "!"), (" %", NBSP + "%")):
        t = t.replace(a, b)
    t = re.sub(r"(\d) (?=\d{3}\b)", r"\1" + NBSP, t)
    t = re.sub(r"(\d) (?=M?d?€)", r"\1" + NBSP, t)
    return t


def fr(x, dec=1):
    """Un nombre à la française : 21,94 · 2 827."""
    s = f"{x:,.{dec}f}".replace(",", NBSP).replace(".", ",")
    return s


def sigle(terme, affiche=None):
    """Un terme avec sa définition au survol."""
    return f'<abbr title="{escape(GLOSSAIRE[terme])}">{affiche or terme}</abbr>'


def _html(t):
    return fr_typo(t)


def entete(surtitre, titre, sous=None, accent="vert"):
    st.markdown(f'<div class="entete {accent}"><div class="filet"></div>'
                f'<div class="surtitre">{_html(surtitre)}</div><h1>{_html(titre)}</h1>'
                + (f'<div class="sous">{_html(sous)}</div>' if sous else "") + "</div>",
                unsafe_allow_html=True)


def tuile(col, valeur, legende, accent="marine"):
    col.markdown(f'<div class="tuile {accent}"><div class="valeur">{_html(valeur)}</div>'
                 f'<div class="souligne"></div><div class="legende">{_html(legende)}</div></div>',
                 unsafe_allow_html=True)


def carte(intitule, paragraphes, accent="vert", conteneur=st):
    if isinstance(paragraphes, str):
        paragraphes = [paragraphes]
    corps = "".join(f"<p>{_html(p)}</p>" for p in paragraphes)
    conteneur.markdown(f'<div class="carte {accent}"><div class="intitule">{_html(intitule)}</div>{corps}</div>',
                       unsafe_allow_html=True)


def pied(source, statut="Confirmé", renvoi=None):
    """Source officielle, statut de fiabilité (Confirmé / Estimé / Reconstitué), renvoi au rapport."""
    cls = "statut" + ("" if statut == "Confirmé" else " estime")
    r = f' · <span class="renvoi">Dans le rapport : {_html(renvoi)}</span>' if renvoi else ""
    st.markdown(f'<div class="pied"><span class="{cls}">{statut}</span>Source : {_html(source)}{r}</div>',
                unsafe_allow_html=True)


def glossaire(termes):
    with st.expander("Les mots de cet écran"):
        for t in termes:
            st.markdown(f"**{t}** — {fr_typo(GLOSSAIRE[t])}")


@st.cache_data(show_spinner=False)
def lire(nom):
    return pd.read_csv(os.path.join(DONNEES, nom), sep=";", decimal=",", encoding="utf-8-sig")


def telecharger(col, libelle, fichier, figure=False):
    """Un bouton de téléchargement : une figure-phare (PNG) ou les données (CSV)."""
    chemin = os.path.join(FIGURES if figure else DONNEES, fichier)
    with open(chemin, "rb") as f:
        col.download_button(libelle, f.read(), file_name=fichier,
                            mime="image/png" if figure else "text/csv", use_container_width=True)
