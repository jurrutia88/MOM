# CLSE_MOM — le compagnon numérique du rapport du CLSE sur le ministère des Outre-mer

Application web publique (Streamlit) qui rend le rapport lisible en huit questions.
Pour chaque indicateur : un chiffre, une phrase de lecture, un graphique, la source et son
statut, un renvoi vers le rapport, un téléchargement.

## Lancer en local

```
pip install -r requirements.txt
streamlit run app.py
```

## Les données

L'application ne lit que `donnees/` et `figures/`. Ces fichiers sont écrits par
`exporter_socle.py`, tenu hors du dépôt avec les classeurs sources ; le script refuse
d'écrire si un chiffre de référence ne retombe pas juste. **Ne pas modifier `donnees/`
à la main.**

Conventions : montants en crédits de paiement (CP) ; 13 outre-mer (5 DROM, 5 COM,
Nouvelle-Calédonie, TAAF, Clipperton) ; chaque chiffre porte sa période, son périmètre
et sa source officielle ; dépenses fiscales jamais additionnées aux crédits.

## Structure

- `app.py` — navigation entre les huit écrans
- `ecrans/` — un fichier par écran
- `charte.py` — charte graphique du CLSE (Lato, fond blanc, cartes en dégradé), gabarit Plotly
- `composants.py` — en-tête, tuiles, cartes, pied de source, glossaire, téléchargements

## État

Maquette : les écrans 3 (ministres) et 4 (budget) sont construits, les autres sont en préparation.
