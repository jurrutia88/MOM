# -*- coding: utf-8 -*-
"""Exporte le socle de l'application vers les tableaux qu'elle affiche (dossier donnees/).

BASE UNIQUE : ce script ne lit qu'un fichier, `socle/Data_MOM — socle application v5.xlsx`. Aucun chiffre
n'est écrit ici : les données sont dans le socle, et les valeurs attendues des chiffres-clés aussi (onglet
REF_Controles).

Le script calcule chaque chiffre-clé et le compare à REF_Controles. S'il en trouve un qui ne retombe pas juste,
il n'écrit RIEN et dit lequel : c'est soit une erreur de saisie, soit une correction voulue — dans ce cas, mettre
à jour REF_Controles et noter la correction dans Journal_corrections.

Usage :
    python outils/exporter.py                          exporte, si tous les contrôles passent
    python outils/exporter.py --montrer-controles      affiche les valeurs calculées, sans rien écrire
"""
import csv
import datetime as dt
import os
import re
import statistics as st_
import sys
from collections import defaultdict
from math import exp, log

import openpyxl

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(ICI)
SOCLE = os.path.join(DEPOT, "socle", "Data_MOM — socle application v5.xlsx")
SORTIE = os.path.join(DEPOT, "donnees")

SORTIES = {}            # nom de fichier → (entêtes, lignes) : rien n'est écrit avant la fin des contrôles
CALCULES = {}           # clé de contrôle → valeur calculée
WB = None


# ─────────────────────────────────────────────── outils
def ecrire(nom, entetes, lignes):
    SORTIES[nom] = (entetes, lignes)


def controle(cle, valeur):
    """Note un chiffre-clé calculé ; la comparaison avec REF_Controles se fait à la fin."""
    if isinstance(valeur, (list, tuple)):
        valeur = ";".join(_txt(v) for v in valeur)
    CALCULES[cle] = _txt(valeur)


def _txt(v):
    if isinstance(v, float):
        return ("%.4f" % v).rstrip("0").rstrip(".")
    return str(v)


def nombre(v):
    """Une cellule : nombre, ou None pour « n.d. »."""
    return None if v in (None, "n.d.", "—", "") else float(v)


def tableau(nom):
    """Un onglet au format du v5 : titre, note, ligne vide, entêtes en ligne 4."""
    ws = WB[nom]
    tete = [c.value for c in ws[4]]
    return [dict(zip(tete, [c.value for c in r])) for r in ws.iter_rows(min_row=5)
            if any(c.value is not None for c in r)]


def parametres():
    return {l["parametre"]: l["valeur"] for l in tableau("REF_Parametres")}


def effort_programmes():
    """L'effort 2026 programme par programme (synthèse tous crédits du DPT) : il retombe sur l'effort du socle,
    19 ministères le portent, les prélèvements sur recettes restent à part. Contrôle ajouté le 24 novembre 2026."""
    P = [l for l in tableau("DATA_DPT_programmes_25_26") if int(l["dpt"]) == 2026]
    tot = sum(nombre(l["plf_n_cp"]) for l in P)
    psr = sum(nombre(l["plf_n_cp"]) for l in P if str(l["ministere_porteur"]).startswith("Prélèvements"))
    porteurs = {l["ministere_porteur"] for l in P if nombre(l["plf_n_cp"]) > 0
                and not str(l["ministere_porteur"]).startswith("Prélèvements")}
    # un programme doté sans ministère connu fausserait le décompte : on refuse
    assert "non trouvé dans la nomenclature" not in porteurs, "programme doté sans ministère porteur"
    controle("Effort par programme 2026 : total CP (Md€) ; ministères porteurs ; prélèvements sur recettes (%)",
             [round(tot / 1e9, 2), len(porteurs), round(100 * psr / tot, 1)])


def chiffres_cites():
    """Les chiffres que les écrans citent tels que la source les donne (onglet REF_Chiffres_cites) : contrôlés ici,
    transmis aux écrans par donnees/chiffres_cites.csv. Aucun chiffre n'est écrit dans le code des écrans."""
    L = tableau("REF_Chiffres_cites")
    v = {l["cle"]: l["valeur"] for l in L}
    assert v["missions_dpt_2026"] == len(tableau("DATA_Missions_DPT_2026")), \
        "le DPT annonce un nombre de missions différent de celui de DATA_Missions_DPT_2026"
    controle("Chiffres cités : écart AE-CP du P123 en LFI 2025 (M€) ; restes à payer en interventions aux "
             "collectivités (%) ; programmes du DPT 2026 ; dont PSR ; missions",
             [v["ecart_ae_cp_p123_2025"], v["rap_interventions_collectivites_2025"], v["programmes_dpt_2026"],
              v["psr_dpt_2026"], v["missions_dpt_2026"]])
    # le groupe GDR : les ultramarins se comptent sur la liste des élus (onglet POL_GDR_elus), en fin de
    # législature (un siège repris en cours de route n'est compté qu'une fois) ; le total vient de la source
    G = tableau("POL_GDR_elus")
    fin = {16: "2024", 17: "2026"}
    ultra = {lg: sum(1 for g in G if int(g["Législature"]) == lg and str(g["Période"]).endswith(fin[lg]))
             for lg in fin}
    for lg in fin:
        assert v["gdr_membres_l%d" % lg] - ultra[lg] < v["seuil_groupe_an"], \
            "GDR, %de législature : le groupe atteindrait le seuil sans les ultramarins" % lg
    controle("Groupe GDR : seuil ; membres 16e ; ultramarins 16e ; membres 17e ; ultramarins 17e",
             [v["seuil_groupe_an"], v["gdr_membres_l16"], ultra[16], v["gdr_membres_l17"], ultra[17]])
    ecrire("chiffres_cites.csv", ["cle", "valeur", "unite", "libelle", "source"],
           [[l["cle"], l["valeur"], l["unite"], l["libelle"], l["source"]] for l in L]
           + [["gdr_ultramarins_l%d" % lg, ultra[lg], "députés",
               "Députés ultramarins du groupe GDR en fin de %de législature" % lg,
               "Calcul : onglet POL_GDR_elus (liste des élus)"] for lg in fin])


# ─────────────────────────────────────────────── 1 · budget : cascade, missions, séries
def budget():
    ref = {l["repere"]: l["valeur_eur"] for l in tableau("REF_Budget_2026")}
    dpt = ref["Effort total de l'État outre-mer (DPT, hors fiscal)"]
    fiscal = ref["Dépenses fiscales outre-mer 2026 — norme retenue"]
    pap = tableau("DATA_PAP_2026_actions")
    p138 = sum(a["cp_2026_eur"] for a in pap if a["programme"] == "P138")
    p123 = sum(a["cp_2026_eur"] for a in pap if a["programme"] == "P123")
    mission = p138 + p123
    contraint = sum(a["cp_2026_eur"] * a["fraction_engagee_d_avance"] for a in pap)
    marge = mission - contraint
    lodeom = next(a for a in pap if a["code"] == "138-01")["cp_2026_eur"]
    dot = next(a for a in pap if a["code"] == "123-06")
    controle("Mission Outre-mer 2026 (€)", mission)
    controle("Marge réellement arbitrée 2026 (€, arrondi)", round(marge))
    controle("Part de la Mission dans le DPT (%)", round(100 * mission / dpt, 2))
    controle("Part de la marge dans le DPT (%)", round(100 * marge / dpt, 2))
    controle("Part du DPT hors Mission (%)", round(100 * (1 - mission / dpt), 1))
    controle("Part avec dépenses fiscales (%)", round(100 * marge / (dpt + fiscal), 1))
    ecrire("budget_cascade.csv", ["etape", "libelle", "bas_eur", "haut_eur", "part_dpt_pct", "affiche"],
           [["1", "Effort total de l'État", 0, dpt, 100.0, ("%.2f" % (dpt / 1e9)).replace(".", ",")],
            ["2", "hors Mission Outre-mer", mission, dpt, round(100 * (dpt - mission) / dpt, 1), ""],
            ["3", "Mission Outre-mer", 0, mission, round(100 * mission / dpt, 2), ("%.2f" % (mission / 1e9)).replace(".", ",")],
            ["4", "engagements contraints", marge, mission, round(100 * contraint / dpt, 2), ""],
            ["5", "Marge réellement arbitrée", 0, round(marge), round(100 * marge / dpt, 2),
             ("%.2f" % (marge / 1e9)).replace(".", ",")]])
    ecrire("budget_cascade_detail.csv", ["poste", "cp_eur"],
           [["P138 Emploi outre-mer", p138], ["P123 Conditions de vie outre-mer", p123],
            ["Compensation LODEOM (action 138-01)", lodeom],
            ["Dotations aux collectivités (action 123-06)", dot["cp_2026_eur"]],
            ["Fraction des dotations retirée (hypothèse)", dot["fraction_engagee_d_avance"]]])
    # les trente missions
    mis = tableau("DATA_Missions_DPT_2026")
    total = ref["Effort total — somme de l'annexe « Synthèse tous crédits »"]
    assert abs(sum(m["cp_2026_eur"] for m in mis) - total) <= 5, "missions : la somme ne retombe pas sur le total"
    assert next(m for m in mis if m["mission"] == "Outre-mer")["cp_2026_eur"] == mission, \
        "la mission Outre-mer de DATA_Missions_DPT_2026 diffère de la somme des actions du PAP"
    controle("Missions contributrices (nombre)", len(mis))
    ecrire("budget_contributeurs.csv", ["mission", "cp_eur", "part_pct"],
           [[m["mission"], m["cp_2026_eur"], round(100 * m["cp_2026_eur"] / total, 2)] for m in mis])
    # les séries 2007-2026 (onglets d'origine, entêtes en ligne 3)
    ws = WB["DATA_Budget_DPT_07_26"]
    serie = [[int(ws.cell(r, 1).value), ws.cell(r, 2).value, nombre(ws.cell(r, 3).value),
              nombre(ws.cell(r, 4).value), nombre(ws.cell(r, 5).value)]
             for r in range(4, ws.max_row + 1) if isinstance(ws.cell(r, 1).value, (int, float))]
    controle("Série DPT : années", "%d-%d" % (serie[0][0], serie[-1][0]))
    controle("Série DPT : dernière année (Md€ ; M€ ; %)", serie[-1][2:])
    controle("Série DPT : part de la Mission en 2007 (%)", serie[0][4])
    ecrire("budget_serie.csv", ["annee", "gouvernement", "dpt_md", "mission_m", "part_pct"], serie)
    ws = WB["DATA_Fiscal_09_26"]
    fisc = [[int(ws.cell(r, 1).value), ws.cell(r, 2).value, nombre(ws.cell(r, 3).value),
             nombre(ws.cell(r, 5).value), nombre(ws.cell(r, 6).value)]
            for r in range(4, ws.max_row + 1) if isinstance(ws.cell(r, 1).value, (int, float))]
    controle("Dépenses fiscales : dernière année (M€ ; ratio)", [fisc[-1][0], fisc[-1][2], fisc[-1][4]])
    controle("Dépenses fiscales : pic (M€)", max(f[2] for f in fisc))
    ecrire("fiscal_serie.csv", ["annee", "gouvernement", "fiscal_m", "mission_m", "ratio"], fisc)
    # la tour de contrôle (sources et statuts)
    ws = WB["00_Statut_indicateurs"]
    tete = next(r for r in range(1, 10) if ws.cell(r, 2).value == "Indicateur")
    ecrire("indicateurs.csv", ["ecran", "indicateur", "valeur", "millesime", "source", "statut"],
           [[ws.cell(r, c).value for c in range(1, 7)] for r in range(tete + 1, ws.max_row + 1)
            if ws.cell(r, 2).value])
    return pap, mission, marge


# ─────────────────────────────────────────────── 2 · le fonctionnement (écran 2) et les restes à payer
def fonctionnement(pap, mission, marge):
    tot = {p: sum(a["cp_2026_eur"] for a in pap if a["programme"] == p) for p in ("P138", "P123")}
    lignes = []
    for a in pap:
        contraint = a["cp_2026_eur"] * a["fraction_engagee_d_avance"]
        lignes.append([a["code"], a["programme"], a["libelle_court"], a["cp_2026_eur"],
                       round(100 * a["cp_2026_eur"] / tot[a["programme"]], 1), round(contraint),
                       round(a["cp_2026_eur"] - contraint), float(a["restes_a_payer_2025_m"] or 0)])
    controle("Engagé d'avance (euros sur dix)", round(10 * sum(l[5] for l in lignes) / mission))
    controle("Restes à payer 2025 par action, total (M€)", round(sum(l[7] for l in lignes), 1))
    ecrire("fonctionnement_actions.csv",
           ["code", "programme", "action", "cp_eur", "part_programme_pct", "contraint_eur", "pilotable_eur",
            "restes_a_payer_m"], lignes)
    ws = WB["DATA_Restes_a_payer_13_25"]
    rap = [[int(ws.cell(r, 1).value), nombre(ws.cell(r, 3).value), nombre(ws.cell(r, 4).value)]
           for r in range(4, ws.max_row + 1) if isinstance(ws.cell(r, 1).value, (int, float))]
    controle("Restes à payer : dernière année (année ; M€ ; mission M€)", rap[-1])
    ecrire("restes_serie.csv", ["annee", "restes_a_payer_m", "mission_m"], rap)
    F = {l["indicateur"]: l for l in tableau("DATA_Fonctionnement")}
    C = {l["categorie"]: l for l in tableau("REF_Couts_P216")}
    moy = sum(c["cout_moyen_eur"] * c["etp"] for c in C.values()) / sum(c["etp"] for c in C.values())
    cab = (F["Membres du cabinet"]["valeur"] * C["HF"]["cout_moyen_eur"]
           + F["Personnels support du cabinet"]["valeur"] * C["C"]["cout_moyen_eur"]
           + F["Indemnités du cabinet (€)"]["valeur"])
    n = F["Agents de la direction générale des outre-mer"]["valeur"]
    est = [cab + n * moy, cab + n * C["B"]["cout_moyen_eur"], cab + n * C["A"]["cout_moyen_eur"]]
    controle("Masse salariale cabinet + DGOM (M€ : estimation ; basse ; haute)", [round(x / 1e6) for x in est])
    sortie = [[k, F[k]["valeur"], F[k]["statut"], F[k]["source"]]
              for k in ("Agents de la direction générale des outre-mer", "Membres du cabinet",
                        "Personnels support du cabinet", "Emplois du service militaire adapté", "dont volontaires")]
    sortie += [["Masse salariale cabinet + DGOM, estimation (€)", round(est[0]), "Estimé",
                "Effectifs × coûts moyens du PAP 2026, programme 216"],
               ["Masse salariale, borne basse (€)", round(est[1]), "Estimé", "idem, tous agents en catégorie B"],
               ["Masse salariale, borne haute (€)", round(est[2]), "Estimé", "idem, tous agents en catégorie A"]]
    ecrire("fonctionnement_chiffres.csv", ["indicateur", "valeur", "statut", "source"], sortie)


# ─────────────────────────────────────────────── 3 · les ministres (écrans 1 et 3)
def ministres():
    ws = WB["DATA_Ministres_base"]
    tete = [c.value for c in ws[1]]
    M = [dict(zip(tete, [c.value for c in r])) for r in ws.iter_rows(min_row=2) if r[0].value]
    j = lambda s: dt.datetime.strptime(s, "%d/%m/%Y").date()
    P = tableau("REF_Presidences")
    court = {p["president"]: p["nom_court"] for p in P}
    lignes = []
    for m in M:
        lignes.append([m["id"], m["prenom"] + " " + m["nom"], m["sexe"], m["ancrage_retenu"],
                       m["rang_protocolaire"], m["fonction_complete"], m["nom_gouvernement"],
                       court[m["president"]], m["premier_ministre"],
                       "rattaché à l'Intérieur" if m["portefeuille_autonome"] == "Non" else "plein exercice",
                       j(m["date_entree"]).isoformat(), j(m["date_sortie"]).isoformat(), m["duree_jours"]])
        assert m["duree_jours"] == (j(m["date_sortie"]) - j(m["date_entree"])).days + 1, \
            "durée fausse pour %s %s (bornes incluses)" % (m["prenom"], m["nom"])
    d = [l[12] for l in lignes]
    pers = lambda L: len({l[1] for l in L})
    f = [l for l in lignes if l[2] == "F"]
    ne = [l for l in lignes if l[3] == "né outre-mer"]
    anc = [l for l in lignes if l[3] != "aucun"]
    rangs = [l[4] for l in lignes]
    controle("Ministres : personnes ; mandats", [pers(lignes), len(lignes)])
    controle("Ministres : durée moyenne ; médiane ; min ; max (jours)",
             [round(st_.mean(d)), st_.median(d), min(d), max(d)])
    controle("Ministres : mandats de moins de six mois", sum(1 for x in d if x < 183))
    controle("Ministres : femmes (personnes ; mandats)", [pers(f), len(f)])
    controle("Ministres : nés outre-mer (personnes ; mandats) ; toute forme d'ancrage (personnes ; mandats)",
             [pers(ne), len(ne), pers(anc), len(anc)])
    controle("Ministres : dernier mandat d'un ministre né outre-mer (début)", max(l[10] for l in ne))
    controle("Ministres : rangs (ministre d'État ; ministre ; délégué ; secrétaire d'État)",
             [rangs.count(r) for r in ("Ministre d'État", "Ministre", "Ministre délégué", "Secrétaire d'État")])
    controle("Ministres : mandats de plein exercice", sum(1 for l in lignes if l[9] == "plein exercice"))
    controle("Ministres : personnes au rang de ministre ou de ministre d'État",
             pers([l for l in lignes if l[4] in ("Ministre", "Ministre d'État")]))
    pres = []
    for p in P:
        L = [l for l in lignes if l[7] == p["nom_court"]]
        ans = (dt.date.fromisoformat(p["fin"]) - dt.date.fromisoformat(p["debut"])).days / 365.25
        en_cours = p is P[-1]
        pres.append([p["nom_court"], p["debut"][:4], "" if en_cours else p["fin"][:4], len(L), pers(L),
                     round(st_.mean(l[12] for l in L)), round(len(L) / ans, 2),
                     sum(1 for l in L if l[9] != "plein exercice"),
                     round(100 * sum(1 for l in L if l[2] == "F") / len(L)),
                     round(100 * sum(1 for l in L if l[3] == "né outre-mer") / len(L)),
                     round(100 * sum(1 for l in L if l[3] == "autre forme") / len(L))])
    for k_, i in (("mandats", 3), ("personnes", 4), ("durée moyenne (j)", 5), ("mandats par an", 6),
                  ("rattachés à l'Intérieur", 7), ("part de femmes (%)", 8)):
        controle("Par présidence : " + k_, [p[i] for p in pres])
    ecrire("ministres_mandats.csv",
           ["id", "ministre", "sexe", "ancrage", "rang", "fonction", "gouvernement", "president",
            "premier_ministre", "rattachement", "debut", "fin", "duree_jours"], lignes)
    ecrire("ministres_presidents.csv",
           ["president", "debut", "fin", "mandats", "ministres", "duree_moyenne_j", "mandats_par_an",
            "rattaches_interieur", "part_femmes_pct", "part_nes_om_pct", "part_autre_forme_pct"], pres)
    # les périodes de rattachement à l'Intérieur, calculées (l'écran 1 les cite)
    ratt = sorted((l[10], l[11], l[1]) for l in lignes if l[9] != "plein exercice")
    periodes = []
    for a, b, qui in ratt:
        # deux mandats rattachés qui se suivent forment une seule période : à moins d'un mois d'écart, ou tenus
        # par la même personne (Lemoine, 1985 : écart de dates à vérifier dans la base)
        if periodes and ((dt.date.fromisoformat(a) - dt.date.fromisoformat(periodes[-1][1])).days <= 31
                         or qui == periodes[-1][2]):
            periodes[-1][1] = max(periodes[-1][1], b)
            periodes[-1][2] = qui
        else:
            periodes.append([a, b, qui])
    controle("Périodes de rattachement à l'Intérieur", ["%s-%s" % (a[:4], b[:4]) for a, b, _q in periodes])
    nc = tableau("DATA_Ministres_non_comptes")
    ecrire("ministres_chiffres.csv", ["indicateur", "valeur"], [
        ["Date d'arrêt de la base", j(parametres()["Date d'arrêt de la base des ministres"]).isoformat()],
        ["Personnes", pers(lignes)], ["Mandats", len(lignes)],
        ["Durée moyenne (jours)", round(st_.mean(d))], ["Durée médiane (jours)", st_.median(d)],
        ["Mandats de moins de six mois", sum(1 for x in d if x < 183)],
        ["Femmes (personnes)", pers(f)], ["Femmes (mandats)", len(f)],
        ["Nés outre-mer (personnes)", pers(ne)], ["Nés outre-mer (mandats)", len(ne)],
        ["Toute forme d'ancrage (personnes)", pers(anc)], ["Toute forme d'ancrage (mandats)", len(anc)],
        ["Mandats de plein exercice", sum(1 for l in lignes if l[9] == "plein exercice")],
        ["Mandats rattachés à l'Intérieur", sum(1 for l in lignes if l[9] != "plein exercice")],
        ["Mandats de ministre d'État", rangs.count("Ministre d'État")], ["Mandats de ministre", rangs.count("Ministre")],
        ["Mandats de ministre délégué", rangs.count("Ministre délégué")],
        ["Mandats de secrétaire d'État", rangs.count("Secrétaire d'État")],
        ["Périodes de rattachement", ", ".join("%s-%s" % (a[:4], b[:4]) for a, b, _q in periodes)],
        ["Nombre de périodes de rattachement", len(periodes)],
        ["Titres « outre-mer » non comptés", _non_comptes(nc)]])


def _non_comptes(nc):
    """Une mention par personne, avec ses années : « Brice Hortefeux (2009-2011) »."""
    par = {}
    for n in nc:
        qui = ("l'intérim d'" if str(n["fonction"]).startswith("Intérim") else "") + "%s %s" % (n["prenom"], n["nom"])
        a_, b_ = n["date_entree"][-4:], n["date_sortie"][-4:]
        lo, hi = par.get(qui, (a_, b_))
        par[qui] = (min(lo, a_), max(hi, b_))
    return ", ".join("%s (%s)" % (q, a_ if a_ == b_ else "%s-%s" % (a_, b_))
                     for q, (a_, b_) in sorted(par.items(), key=lambda x: x[1]))


# ─────────────────────────────────────────────── 4 · l'histoire (écran 1)
def histoire():
    types = {l["jalon"]: l["type"] for l in tableau("REF_Types_E1")}
    ws = WB["E1_Histoire"]
    lignes = []
    for r in range(5, ws.max_row + 1):
        jalon, date, fait, expl, src = (ws.cell(r, c).value for c in range(1, 6))
        if not jalon:
            continue
        an = int(re.search(r"\d{4}", date).group()) if re.search(r"\d{4}", date) else 1650
        assert jalon in types, "jalon sans type dans REF_Types_E1 : %s" % jalon
        lignes.append([jalon, date, an, types[jalon], fait, expl, src])
    lignes += [[l["jalon"], l["date"], l["annee"], l["type"], l["fait"], l["explication"], l["source"]]
               for l in tableau("E1_Jalons_complement")]
    # une source primaire nomme un texte (loi, décret, numéro) ; sinon c'est une source secondaire
    for l in lignes:
        l.append("Confirmé" if re.search(r"Loi n|[Dd]écret n|Décret du|JORF du|mandats", l[6]) else "Secondaire")
    lignes.sort(key=lambda l: l[2])
    controle("Frise : jalons ; dont sources secondaires",
             [len(lignes), sum(1 for l in lignes if l[7] == "Secondaire")])
    ecrire("histoire_jalons.csv", ["jalon", "date", "annee", "type", "fait", "explication", "source", "statut"],
           lignes)


# ─────────────────────────────────────────────── 5 · les statuts (écran 5)
def statuts():
    T = {l["territoire"]: l for l in tableau("REF_Territoires")}
    ws = WB["E5_Statuts"]
    lignes = []
    for r in range(5, ws.max_row + 1):
        terr, fr_, ue, src = (ws.cell(r, c).value for c in range(1, 5))
        if not terr or terr not in T:
            continue
        groupe = ("Article 73" if "art. 73" in fr_ else "Article 74" if "art. 74" in fr_
                  else "Titre XIII" if "titre XIII" in fr_ else "Statut particulier")
        lignes.append([terr, groupe, fr_, "aucun" if ue == "—" else ue, T[terr]["ocean"], T[terr]["habite"], src])
    G = [l[1] for l in lignes]
    U = [l[3] for l in lignes]
    controle("Statuts : territoires ; habités", [len(lignes), sum(1 for l in lignes if l[5] == "oui")])
    controle("Statuts : art. 73 ; art. 74 ; titre XIII ; particuliers",
             [G.count(g) for g in ("Article 73", "Article 74", "Titre XIII", "Statut particulier")])
    controle("Statuts : RUP ; PTOM ; aucun", [U.count(u) for u in ("RUP", "PTOM", "aucun")])
    ecrire("statuts.csv", ["territoire", "groupe", "statut", "regime_europeen", "ocean", "habite", "source"], lignes)


# ─────────────────────────────────────────────── 6 · les territoires (écran 6)
REF_FRANCE = ("France (réf.)", "France hexa. (réf.)")
DROM = ("Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte")
# Indice intégré de précarité (José, 29 octobre 2026), calcul du CLSE — « Reconstitué » : chaque indicateur
# rapporté à sa valeur nationale, moyenne géométrique par dimension puis entre dimensions, à poids égaux.
DIMENSIONS = [("Revenus", (1, 13)), ("Emploi", (5, 6, 7)), ("Éducation", (8,)), ("Santé", (9, 11)),
              ("Vie chère", (3,))]


def territoires():
    ws = WB["DATA_Territorial_PIV"]
    lignes = []
    for r in range(4, ws.max_row + 1):
        v = [ws.cell(r, c).value for c in range(1, 9)]
        if v[0] is None or v[1] in (None, "Territoire"):
            continue
        ind, terr, val, mil, _ref, comp, src, com = v
        brut = str(val).strip()
        m = re.search(r"[\d.]+", brut)
        num = float(m.group()) if m and brut not in ("n.d.",) else None
        marque = "≈" if brut.startswith("~") else (">" if brut.startswith(">") else "")
        nom, unite = re.match(r"\d+\.\s*(.+?)\s*\(([^)]*)\)\s*$", ind).groups()
        lignes.append([int(ind.split(".")[0]), nom, unite, terr, num, marque, mil, comp,
                       "oui" if terr in REF_FRANCE else "non", src, com or ""])
    val = {(l[0], l[3]): l[4] for l in lignes}
    controle("Indicateurs territoriaux (nombre)", len({l[0] for l in lignes}))
    controle("Pauvreté : Mayotte ; France (%)", [val[(1, "Mayotte")], val[(1, "France (réf.)")]])
    controle("Chômage : Martinique ; Guadeloupe ; Guyane ; La Réunion ; Mayotte ; France (%)",
             [val[(5, t)] for t in ("Martinique", "Guadeloupe", "Guyane", "La Réunion", "Mayotte", "France (réf.)")])
    controle("Prix alimentaires DROM : min ; max (%)", [min(val[(3, t)] for t in DROM), max(val[(3, t)] for t in DROM)])
    ecrire("territoires_indicateurs.csv",
           ["num", "indicateur", "unite", "territoire", "valeur", "marque", "millesime", "comparable", "reference",
            "source", "commentaire"], lignes)
    T = {l["territoire"]: l for l in tableau("REF_Territoires")}
    ws = WB["DATA_PIB_hab_13terr"]
    pib = []
    for r in range(4, ws.max_row + 1):
        terr, statut, eur, an, _pct, src = (ws.cell(r, c).value for c in range(1, 7))
        if not terr or not isinstance(eur, (int, float)):
            continue
        nom = terr.replace(" (y compris Saint-Martin)", "")
        cp, popu = (T[nom]["cp_2026_eur"], T[nom]["population"]) if nom in T else (None, None)
        ehab = round(cp / popu) if cp else None
        pib.append([nom, terr, statut, eur, str(an), src, cp, popu, ehab, round(eur / ehab, 1) if ehab else None])
    P = {p[0]: p for p in pib}
    controle("PIB par habitant : Mayotte ; Saint-Barthélemy ; Martinique (€)",
             [P[t][3] for t in ("Mayotte", "Saint-Barthélemy", "Martinique")])
    controle("Effort par habitant : Mayotte ; Guadeloupe ; Martinique ; La Réunion ; Guyane (€)",
             [P[t][8] for t in ("Mayotte", "Guadeloupe", "Martinique", "La Réunion", "Guyane")])
    controle("Richesse pour 1 € : Wallis-et-Futuna ; Mayotte ; Saint-Barthélemy",
             [P[t][9] for t in ("Wallis-et-Futuna", "Mayotte", "Saint-Barthélemy")])
    ecrire("territoires_pib_effort.csv",
           ["territoire", "libelle_socle", "statut", "pib_hab_eur", "annee_pib", "source_pib", "cp_2026_eur",
            "population", "effort_hab_eur", "richesse_pour_1_euro"], pib)
    # l'indice intégré de précarité des cinq DROM
    par = {(l[0], l[3]): l for l in lignes}
    gm = lambda xs: exp(sum(log(x) for x in xs) / len(xs))
    detail, indice = [], []
    for t in DROM:
        dims = []
        for dim, nums in DIMENSIONS:
            rs = []
            for n in nums:
                l = par[(n, t)]
                if n == 3:                       # déjà un écart à l'Hexagone : + 42 % → 1,42
                    fr_, r = None, 1 + l[4] / 100
                else:
                    fr_ = par[(n, "France (réf.)")][4]
                    r = l[4] / fr_
                rs.append(r)
                detail.append([t, dim, n, l[1], l[2], l[4], fr_, round(r, 3), l[6], l[7]])
            dims.append(gm(rs))
            indice.append([t, dim, round(gm(rs), 3)])
        indice.append([t, "Indice intégré", round(gm(dims), 3)])
    I = {(t, d): v for t, d, v in indice}
    controle("Indice de précarité : Mayotte ; Guyane ; Guadeloupe ; La Réunion ; Martinique",
             [I[(t, "Indice intégré")] for t in ("Mayotte", "Guyane", "Guadeloupe", "La Réunion", "Martinique")])
    ecrire("territoires_precarite_detail.csv",
           ["territoire", "dimension", "num", "indicateur", "unite", "valeur", "france", "rapport_a_la_france",
            "millesime", "comparable"], detail)
    ecrire("territoires_precarite.csv", ["territoire", "dimension", "indice"], indice)
    return T


# ─────────────────────────────────────────────── 7 · la représentation (écran 7)
SIEGES = {"Saint-Martin / Saint-Barthélemy": ("Saint-Martin", "Saint-Barthélemy")}


def representation(T):
    ws = WB["E7_Representation_AN"]
    lignes, total, an = [], None, None
    for r in range(5, ws.max_row + 1):
        terr, n, src = (ws.cell(r, c).value for c in range(1, 4))
        if not terr or not isinstance(n, int):
            continue
        if terr.startswith("TOTAL"):
            total = n
        elif terr.startswith("Assemblée"):
            an = n
        else:
            popu = sum(T[t]["population"] for t in SIEGES.get(terr, (terr,)))
            lignes.append([terr, n, popu, round(popu / n), src])
    assert sum(l[1] for l in lignes) == total, "E7 : la somme des sièges ne retombe pas sur le total"
    pop = {l["perimetre"]: l["population"] for l in tableau("REF_Population_France")}
    habites = [t for t in T.values() if t["habite"] == "oui"]
    pop_om = sum(t["population"] for t in habites)
    quatre = sum(T[t]["population"] for t in ("Guadeloupe", "Martinique", "Guyane", "La Réunion"))
    p4 = pop["Métropole et quatre départements (Guadeloupe, Martinique, Guyane, La Réunion)"]
    assert p4 - pop["Métropole"] == quatre, "les quatre départements ne retombent pas sur le décret"
    pop_fr = p4 + pop_om - quatre
    controle("Représentation : sièges ; Assemblée ; part des sièges (%)", [total, an, round(100 * total / an, 2)])
    controle("Représentation : part de la population (%)", round(100 * pop_om / pop_fr, 2))
    ecrire("representation_sieges.csv", ["territoire", "deputes", "population", "habitants_par_depute", "source"],
           lignes)
    ecrire("representation_chiffres.csv", ["indicateur", "valeur", "source"], [
        ["Sièges de députés des outre-mer", total, "Code électoral ; Assemblée nationale (17e législature)"],
        ["Sièges de l'Assemblée nationale", an, "Assemblée nationale"],
        ["Part des sièges (%)", round(100 * total / an, 2), "Calcul"],
        ["Population des onze territoires habités", pop_om, "INSEE (décret n° 2025-1362), ISEE, ISPF, STSEE"],
        ["Population de la France, outre-mer compris", pop_fr,
         "Décret n° 2025-1362 (métropole et quatre départements, 2023) + Mayotte et collectivités (millésimes propres)"],
        ["Part de la population (%)", round(100 * pop_om / pop_fr, 2), "Calcul — indicatif, millésimes différents"]])


# ─────────────────────────────────────────────── 8 · les couleurs politiques (écran 7)
CODES = {"Gauche autonomiste / indépendantiste": "AI", "Gauche radicale / communiste": "GR",
         "Gauche socialiste / réformiste": "GS", "Centre": "C", "Centre droit": "CD", "Droite": "D",
         "Extrême droite": "ED", "Composite / transversal": "Co", "Non déterminée": "ND"}
MOIS = {m: i + 1 for i, m in enumerate(["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                                         "septembre", "octobre", "novembre", "décembre"])}


def _date_fr(t):
    jr, m, a = re.match(r"(\d+)(?:er)?\s+(\S+)\s+(\d{4})", t.strip()).groups()
    return dt.date(int(a), MOIS[m], int(jr))


def politique():
    positions = [(l["Position"], l["Famille"], l["Ce qu'elle regroupe"], l["Couleur"])
                 for l in tableau("POL_Positions")             # les notes sous le tableau n'ont pas de couleur
                 if l.get("Position") and str(l.get("Couleur") or "").startswith("#")]
    connues = {p for p, *_ in positions}
    groupes = {l["Groupe à l'Assemblée (Sycomore)"]: (l["Position retenue (José)"] or l["Position proposée"],
                                                       l["Nature"]) for l in tableau("POL_Groupes")
               if l.get("Groupe à l'Assemblée (Sycomore)")}
    elus = {(int(l["Législature"]), l["Député"]): l["Position retenue (José)"] or l["Position proposée"]
            for l in tableau("POL_GDR_elus") if l.get("Député")}
    faux = sorted({p for p, _n in groupes.values() if not p.startswith("Élu par élu")} - connues
                  | (set(elus.values()) - connues))
    assert not faux, "positions absentes de POL_Positions : %s" % faux
    famille = {p: f for p, f, _d, _c in positions}
    arret = dt.date.fromisoformat(dt.datetime.strptime(parametres()["Date de collecte Sycomore"],
                                                       "%d/%m/%Y").date().isoformat())
    lignes, inconnus = [], set()
    for m in tableau("POL_Deputes_Sycomore"):
        t = m["mandat"]
        if t.startswith("Depuis"):
            debut, fin = _date_fr(t[len("Depuis le "):]), arret
        else:
            a, b = re.match(r"Du (.+?) au (.+)$", t).groups()
            debut, fin = _date_fr(a), _date_fr(b)
        g = (m["groupe"] or "").strip() or "(non renseigné)"
        leg = int(m["legislature"])
        if g not in groupes:
            inconnus.add(g)
            continue
        pos, nature = groupes[g]
        if pos.startswith("Élu par élu"):
            pos = elus.get((leg, m["depute"]))
            if pos is None:
                inconnus.add("%s (%s, %d)" % (g, m["depute"], leg))
                continue
        lignes.append([leg, m["territoire"], m["depute"], g, pos, famille[pos], nature,
                       debut.isoformat(), fin.isoformat(), (fin - debut).days, m["fiche"]])
    assert not inconnus, "mandats sans position dans la grille : %s" % sorted(inconnus)
    controle("Députés : mandats ; législatures ; sièges de la dernière législature",
             [len(lignes), len({l[0] for l in lignes}),
              sum(1 for l in lignes if l[0] == max(x[0] for x in lignes) and l[8] == arret.isoformat())])
    ecrire("politique_positions.csv", ["ordre", "position", "famille", "couleur", "code", "definition"],
           [[i + 1, p, f, c, CODES[p], d] for i, (p, f, d, c) in enumerate(positions)])
    ecrire("politique_mandats.csv", ["legislature", "territoire", "depute", "groupe", "position", "famille", "nature",
                                     "debut", "fin", "jours", "fiche_sycomore"], lignes)
    noms = [p for p, *_ in positions]
    jours = defaultdict(float)
    for l in lignes:
        jours[(l[0], l[1], l[4])] += l[9]
    synthese = []
    for leg, terr in sorted({(l[0], l[1]) for l in lignes}):
        tot = sum(v for (l_, t_, _), v in jours.items() if (l_, t_) == (leg, terr))
        parts = {p: jours.get((leg, terr, p), 0) / tot for p in noms}
        dom = max(parts, key=parts.get)
        if len([p for p, v in parts.items() if abs(v - parts[dom]) < 0.02]) > 1:
            dom = "Partagé"
        synthese.append([leg, terr, dom, round(100 * max(parts.values()), 1),
                         famille.get(dom, "Partagé")] + [round(100 * parts[p], 1) for p in noms])
    ecrire("politique_territoires.csv", ["legislature", "territoire", "position_dominante", "part_dominante_pct",
                                         "famille_dominante"] + ["part_%s_pct" % CODES[p] for p in noms], synthese)
    DROM4 = {"Guadeloupe", "Martinique", "Guyane", "La Réunion"}
    PACIF = {"Polynésie française", "Nouvelle-Calédonie", "Wallis-et-Futuna"}
    PERIODES = [("1958-1981", range(1, 7)), ("1981-2017", range(7, 15)), ("2017-2026", range(15, 18))]
    chiffres = []
    for zone, terrs in (("Antilles, Guyane, La Réunion", DROM4), ("Pacifique", PACIF)):
        for nom_p, legs in PERIODES:
            sel = [l for l in lignes if l[1] in terrs and l[0] in legs]
            tot = sum(l[9] for l in sel)
            for niveau, k_ in (("famille", 5), ("position", 4)):
                acc = defaultdict(float)
                for l in sel:
                    acc[l[k_]] += l[9]
                for cle, v in sorted(acc.items(), key=lambda x: -x[1]):
                    chiffres.append([zone, nom_p, niveau, cle, round(100 * v / tot, 1)])
    chiffres.append(["Outre-mer", "17e législature", "nombre", "Extrême droite",
                     len({l[2] for l in lignes if l[0] == 17 and l[4] == "Extrême droite"})])
    ecrire("politique_chiffres.csv", ["zone", "periode", "niveau", "valeur", "part_jours_pct"], chiffres)


# ─────────────────────────────────────────────── contrôle final et écriture
def main():
    global WB
    montrer = "--montrer-controles" in sys.argv
    WB = openpyxl.load_workbook(SOCLE, data_only=True)
    pap, mission, marge = budget()
    effort_programmes()
    chiffres_cites()
    fonctionnement(pap, mission, marge)
    ministres()
    histoire()
    statuts()
    T = territoires()
    representation(T)
    politique()
    attendus = {str(l["controle"]): _txt(l["valeur_attendue"]) if not isinstance(l["valeur_attendue"], str)
                else l["valeur_attendue"] for l in tableau("REF_Controles")}
    if montrer:
        for k_, v in CALCULES.items():
            print("%-95s %s" % (k_, v))
        return
    ecarts = [(k_, v, attendus.get(k_)) for k_, v in CALCULES.items() if attendus.get(k_) != v]
    if ecarts:
        print("EXPORT REFUSÉ — %d chiffre(s)-clé(s) ne retombent pas sur REF_Controles :" % len(ecarts))
        for k_, v, a in ecarts:
            print("  • %s\n      calculé : %s\n      attendu : %s" % (k_, v, a if a is not None else "(absent)"))
        print("Si la correction est voulue : mettre à jour REF_Controles et noter la correction dans "
              "Journal_corrections, puis relancer.")
        sys.exit(1)
    os.makedirs(SORTIE, exist_ok=True)
    for nom, (entetes, lignes) in SORTIES.items():
        with open(os.path.join(SORTIE, nom), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(entetes)
            for l in lignes:
                w.writerow(["" if v is None else (str(v).replace(".", ",") if isinstance(v, float) else v)
                            for v in l])
        print("  écrit : donnees/%s (%d lignes)" % (nom, len(lignes)))
    print("%d contrôles passés." % len(CALCULES))


if __name__ == "__main__":
    main()
