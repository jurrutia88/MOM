# CLSE_MOM — le compagnon numérique du rapport du CLSE sur le ministère des Outre-mer

Site web qui rend le rapport lisible en huit questions. L'application est écrite en Streamlit et
tourne entièrement dans le navigateur du lecteur (stlite) : la page est publiée sur GitHub Pages,
sans serveur à réveiller ni compte à créer.
Pour chaque indicateur : un chiffre, une phrase de lecture, un graphique, la source et son
statut, un renvoi vers le rapport, un téléchargement.

## La base unique

**Tous les chiffres de l'application viennent d'un seul classeur :**
`socle/Data_MOM — socle application v5.xlsx`. Rien n'est saisi ailleurs, ni dans le code des
écrans, ni dans `donnees/`.

- L'onglet **Lisez-moi** décrit les conventions et les onglets.
- L'onglet **Journal_corrections** garde la trace de toute modification d'un chiffre : date,
  ancienne valeur, nouvelle valeur, raison, source.
- L'onglet **REF_Controles** donne la valeur attendue de chaque chiffre-clé (48 contrôles).

Le script `outils/exporter.py` lit le classeur, calcule les tableaux de `donnees/` et compare
chaque chiffre-clé à `REF_Controles`. **Au moindre écart, il n'écrit rien** et dit lequel.

Conventions : montants en crédits de paiement (CP), base PLF ; 13 outre-mer (5 DROM, 5 COM,
Nouvelle-Calédonie, TAAF, Clipperton) ; chaque chiffre porte sa période, son périmètre et sa
source officielle ; dépenses fiscales jamais additionnées aux crédits. Ministres : on compte
le membre du gouvernement chargé du portefeuille ; le ministre de l'Intérieur seulement quand
personne d'autre ne le tient.

## Mettre à jour un chiffre — sans rien installer

1. Ouvrir le classeur dans Excel et corriger la valeur dans son onglet.
2. Noter la correction dans **Journal_corrections**.
3. Si la correction change un chiffre-clé, mettre aussi à jour sa ligne dans **REF_Controles**.
4. Sur GitHub, dans le dossier `socle/`, cliquer sur **Add file → Upload files**, déposer le
   classeur (même nom), puis **Commit changes**.
5. L'export tourne tout seul (onglet **Actions** du dépôt, deux minutes environ). S'il réussit,
   l'application se met à jour d'elle-même. S'il échoue, ouvrir l'action en rouge : la dernière
   étape dit quel chiffre ne retombe pas juste, et rien n'a été modifié.

## Modifier un texte

Les titres, sous-titres et phrases de chaque écran sont dans `ecrans/` (un fichier par écran).
Sur GitHub, ouvrir le fichier, cliquer sur le crayon, modifier le texte **entre les guillemets**
sans toucher au reste, puis **Commit changes**. Les chiffres cités dans les phrases ne s'écrivent
pas à la main : ils sont calculés depuis le classeur.

## Consulter le site

Le site est la page `index.html` du dépôt, publiée par GitHub Pages (Settings → Pages, branche
`main`, dossier racine). Le premier chargement prend une trentaine de secondes : le navigateur
installe l'application ; les visites suivantes sont plus rapides. Après chaque export, l'action
refait `index.html` : le site montre les nouveaux chiffres dès la visite suivante.

## Lancer sur un poste (facultatif, pour développer)

```
pip install -r requirements.txt
python outils/exporter.py
streamlit run app.py
```

## Structure

- `socle/` — le classeur de référence (base unique)
- `outils/exporter.py` — l'export contrôlé du socle vers `donnees/`
- `donnees/` — les tableaux lus par l'application (écrits par l'export, **jamais à la main**)
- `figures/` — les figures du deck proposées au téléchargement
- `app.py` — navigation entre les huit écrans
- `ecrans/` — un fichier par écran
- `charte.py` — charte graphique (Lato, fond blanc, cartes en dégradé), gabarit Plotly
- `composants.py` — en-tête, tuiles, cartes, pied de source, glossaire, fond des territoires
- `.github/workflows/exporter.yml` — l'export automatique quand le socle change

Les contours des territoires (`donnees/territoires_contours.csv`, Natural Earth) et les silhouettes
(`donnees/territoires_silhouettes.csv`, d'après une figure du deck) sont des géométries, pas des
chiffres : elles sont fabriquées une fois pour toutes et ne passent pas par le socle.

## État

Les écrans 1 à 7 sont construits ; l'écran 8 (que faut-il transformer ?) attend les scénarios.
