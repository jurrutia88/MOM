# -*- coding: utf-8 -*-
"""Écrit index.html : la même application, exécutée dans le navigateur du lecteur (stlite), sans serveur.

Pourquoi (José, 24 novembre 2026) : gratuit, sans réveil, sans inscription, et le CLSE garde la main. Le site
statique est servi tel quel par GitHub Pages ; index.html charge stlite, qui télécharge le code et les tableaux
de donnees/ à côté de lui et fait tourner Streamlit dans le navigateur. Rien n'est recodé.

index.html donne la liste des fichiers, chacun avec l'empreinte de son contenu (sans quoi un navigateur
resservirait l'ancienne version depuis son cache). Il est donc refait à chaque modification : l'action
GitHub le fait seule après l'export.
Usage : python outils/construire_index.py
"""
import glob
import hashlib
import json
import os
import tomllib

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STLITE = "1.12.1"                       # publié le 5 novembre 2026
MOTIFS = ["app.py", "charte.py", "composants.py", "ecrans/*.py", "donnees/*.csv", "figures/*.png",
          ".streamlit/config.toml"]
# plotly : la version du serveur ; pandas est fourni par Pyodide
DEPENDANCES = ["plotly==5.24.1"]

fichiers = {}
for m in MOTIFS:
    for f in sorted(glob.glob(os.path.join(ICI, m))):
        rel = os.path.relpath(f, ICI).replace(os.sep, "/")
        # l'empreinte du contenu dans l'adresse : un fichier modifié n'est jamais resservi depuis le cache
        empreinte = hashlib.sha1(open(f, "rb").read()).hexdigest()[:10]
        fichiers[rel] = {"url": "./%s?v=%s" % (rel, empreinte)}

PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<title>Le ministère des Outre-mer en chiffres — CLSE</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/browser@%(v)s/build/stlite.css">
<style>
  body { margin: 0; background: #FFFFFF; font-family: Lato, "Segoe UI", sans-serif; color: #1D323F; }
  #attente { position: fixed; inset: 0; display: flex; flex-direction: column; align-items: center;
             justify-content: center; gap: 10px; text-align: center; padding: 16px; }
  #attente b { font-size: 1.3rem; }
  #attente span { color: #5A6B75; font-size: .95rem; max-width: 420px; line-height: 1.45; }
</style>
</head>
<body>
<div id="attente"><b>Le ministère des Outre-mer en chiffres</b>
  <span>Chargement de l'application… la première visite prend une vingtaine de secondes ;
  les suivantes sont plus rapides.</span></div>
<div id="root"></div>
<script type="module">
import { mount } from "https://cdn.jsdelivr.net/npm/@stlite/browser@%(v)s/build/stlite.js";
const app = mount({
  requirements: %(deps)s,
  entrypoint: "app.py",
  streamlitConfig: %(config)s,
  files: %(files)s,
}, document.getElementById("root"));
const obs = new MutationObserver(() => {
  if (document.querySelector("#root [data-testid='stApp']")) {
    document.getElementById("attente").remove(); obs.disconnect();
  }
});
obs.observe(document.getElementById("root"), { childList: true, subtree: true });
</script>
</body>
</html>
"""

# stlite ne lit pas .streamlit/config.toml : on lui passe le thème (clair, couleurs de la charte) au lancement,
# sinon un navigateur réglé en mode sombre affiche les graphiques sur fond noir.
with open(os.path.join(ICI, ".streamlit", "config.toml"), "rb") as f:
    THEME = {"theme." + k: v for k, v in tomllib.load(f).get("theme", {}).items()}

page = PAGE % {"v": STLITE, "config": json.dumps(THEME, ensure_ascii=False), "deps": json.dumps(DEPENDANCES),
               "files": json.dumps(fichiers, indent=2, ensure_ascii=False)}
# 404.html = la même page : GitHub Pages la sert pour une adresse d'écran (…/budget) ouverte directement ou
# rechargée, et l'application affiche alors le bon écran au lieu d'une erreur.
for nom in ("index.html", "404.html"):
    with open(os.path.join(ICI, nom), "w", encoding="utf-8") as f:
        f.write(page)
print("écrit : index.html et 404.html (%d fichiers)" % len(fichiers))
