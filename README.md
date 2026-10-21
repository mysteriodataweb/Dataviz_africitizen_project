# Dataviz Africitizen — la production d'électricité dans le monde et en Afrique

Collecte, nettoyage, analyse exploratoire et visualisation (Power BI) de la production d'électricité par pays de 1985 à 2024, à partir des données d'[Our World in Data](https://ourworldindata.org/grapher/electricity-generation).

## Pipeline

| Étape | Fichier | Rôle |
|---|---|---|
| 1. Collecte | [`energy_scraping.ipynb`](energy_scraping.ipynb) | Scraping du tableau de la page OWID (Helium/Selenium + BeautifulSoup), puis téléchargement du CSV complet, car le tableau de la page ne contient qu'un résumé. |
| | [`scraper_utils.py`](scraper_utils.py) | Fonctions réutilisables : `scrape_table_from_url`, `parse_html_table`, `download_csv`, `close_browser` (voir [`SCRAPER_USAGE.md`](SCRAPER_USAGE.md)). |
| | `electricity_generation.csv` | Données brutes : `Entity`, `Code`, `Year`, `Electricity generation - TWh`. |
| 2. Nettoyage | [`data_cleaning.py`](data_cleaning.py) | Garde uniquement les pays (grâce au code ISO) et produit le fichier utilisé par Power BI. |
| | `electricity_generation_countries.xlsx` | Données nettoyées (215 pays), source du rapport Power BI. |
| 3. Analyse | [`Exploratory_analysis.ipynb`](Exploratory_analysis.ipynb) | Nettoyage, couverture des données, analyse univariée, cas de Niue, classification des pays, focus Afrique, interprétations et recommandations. |
| 4. Visualisation | `Dataviz.pbix` | Tableau de bord Power BI ([version en ligne](https://centralecasablanca-my.sharepoint.com/:u:/g/personal/kwamialfredjordal_biam_centrale-casablanca_ma/IQCuixPiVBAdR5JULKCmN6eyASzmxekXu7V-3w9OIIGNnEk?e=C5oSI6)). |

## Installation et utilisation

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt

python data_cleaning.py            # régénère electricity_generation_countries.xlsx depuis le CSV brut
jupyter notebook                   # ouvre les notebooks
pytest                             # lance les tests
```

Le scraping (`scrape_table_from_url`) nécessite Google Chrome. Le notebook d'analyse fonctionne aussi sans Chrome ni connexion Internet : le scraping de la page de Niue est alors simplement ignoré.

## Principaux résultats

- **Le nettoyage d'origine laissait 27 agrégats parmi les pays** (G20, G7, OCDE, Union européenne, ASEAN, groupes de revenus...). Ils apparaissaient parmi les « pays » à forte production, et dans Power BI les totaux étaient environ 4,8 fois trop élevés (140 228 TWh en 2022 au lieu de 28 927 TWh). Le filtrage se fait maintenant avec la colonne `Code` (code ISO 3166-1 alpha-3).
- **Les données ne couvrent pas les mêmes pays chaque année** : environ 80 pays de 1985 à 1999, 214 de 2000 à 2022, 175 en 2023 et 101 en 2024. Les pays sont donc comparés sur leur production de **2022**, la dernière année renseignée pour presque tous les pays, et non plus sur la somme de toutes les années, qui avantageait les pays renseignés depuis 1985.
- **La distribution est très asymétrique** (skewness ~10,5) : les productions vont de quelques GWh à près de 9 000 TWh. Les classes suivent donc une échelle logarithmique : *Low* < 10 TWh/an ≤ *Medium* < 100 TWh/an ≤ *High*. En 2022, on compte 105 pays dans la classe *Low*, 71 dans la classe *Medium* et 37 dans la classe *High*. Les plus gros producteurs sont la Chine (8 849 TWh), les États-Unis (4 287), l'Inde (1 829), la Russie (1 167) et le Japon (1 041).
- **Niue n'a pas une production nulle** : elle produit environ 3 000 MWh, soit 0,003 TWh, une valeur arrondie à 0 dans un jeu de données précis à 0,01 TWh.
- **Afrique** : 3,2 % de l'électricité mondiale en 2022 (2,9 % en 2000), pour près de 18 % de la population mondiale. La production africaine a doublé depuis 2000 (+109 % contre +89 % dans le monde). L'Afrique du Sud et l'Égypte en assurent près de la moitié, et 40 des 56 pays africains produisent moins de 10 TWh par an.

## Tableau de bord Power BI

- `electricity_generation_countries.xlsx` a été régénéré **avec le même schéma** (feuille `Sheet1`, colonnes `Entity`, `Year`, `Electricity generation - TWh`) : il suffit d'**actualiser** le rapport (*Accueil > Actualiser*) pour que les agrégats disparaissent. Si Power BI ne trouve pas le fichier, mettez à jour son chemin dans *Transformer les données > Paramètres de la source de données*.
- Les totaux et les courbes sur 1985-1999 et 2023-2024 ne portent pas sur les mêmes pays que sur 2000-2022 : la baisse visible en 2023-2024 vient des données manquantes, pas d'une baisse réelle. Filtrez de préférence les années 2000 à 2022.
- Sans filtre d'année, la carte qui affiche la somme de `Electricity generation - TWh` additionne toutes les années. Sélectionnez une année avec le segment.
- `Year` est une date au 1er janvier : dans la hiérarchie de dates, seul le niveau *Année* a un sens (pas les trimestres, les mois ni les jours).

## Sources

- Our World in Data, *Electricity generation*, à partir des données d'[Ember](https://ember-energy.org/) et de l'[Energy Institute — Statistical Review of World Energy](https://www.energyinst.org/statistical-review). Licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [Worldometers](https://www.worldometers.info/fr/electricite/niue-electricite/) pour la production électrique de Niue (2016).
