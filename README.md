# api-offres-emploi 
A python wrapper for [API Offres d'emploi v2](https://www.emploi-store-dev.fr/portail-developpeur-cms/home/catalogue-des-api/documentation-des-api/api/api-offres-demploi-v2.html) available on [Emploi Store](https://www.emploi-store.fr/portail/accueil) (Pole Emploi).

### Table of content

- [1. Setting up](#1-setting-up)
- [2. Usage](#2-usage)
  - [Installation](#21-installation)
  - [Authentification](#22-authentification)
- [3. Examples](#3-examples)
  - [3.1. search](#31-search)
  - [3.2. referentiel](#32-referentiel)
- [4. Analysis of the search output](#4-analysis-of-the-search-output)
  - [4.1. Aggregate view of job offers](#41-aggregate-view-of-job-offers)
  - [4.2. Detailed view of job offers](#42-detailed-view-of-job-offers)

## 1. Setting up
To use the API, you need to subscribe to the _Api Offres d'emploi v2_. Here are the steps:
- Create an account on [Emploi store](https://www.emploi-store-dev.fr/)
- Go to the dashboard (*Tableau de bord*) and create an application. You should then have the client ID (_Identifiant_) and client secret key (_Clé secrète_).
- Go to [catalogue](https://www.emploi-store-dev.fr/portail-developpeur/catalogueapi) and subscribe to _Api Offres d'emploi v2_

## 2. Usage

### 2.1. Installation
The package can be installed via pip:
```python
pip install api-offres-emploi
```

### 2.2. Authentification
To authentificate, create an instance of `Api` with your client id and secrets (you might want to access these two variables through environment variables instead of hardcoding them):

```python
from offres_emploi import Api
client = Api(client_id="<your client id>", 
             client_secret="<your client secret>")
```

### 2.3. Methods exposed by the API 'Offres d'emploi v2'
The API _Offres d'emploi v2_ has two methods : 
- `search` : return aggregate count (named _filtresPossibles_) of the job offers along with the detailed list of these job offers (named _resultats_). A lot of parameters are available : date, keywords, localization, etc. Extensive information on the website page [Rechercher par critères](https://www.emploi-store-dev.fr/portail-developpeur-cms/home/catalogue-des-api/documentation-des-api/api/api-offres-demploi-v2/rechercher-par-criteres.html).
- `referentiel` : return reference source (more information on the website page [Référentiels](https://www.emploi-store-dev.fr/portail-developpeur-cms/home/catalogue-des-api/documentation-des-api/api/api-offres-demploi-v2/referentiels.html)).

**About range and pagination**: In the method `search`, only the first 150 job offers are returned by default by the API (since the default `range` value is `0-149`). There are three constraints regarding the `range` parameter ([see the reference for the parameter 'range'](https://www.emploi-store-dev.fr/portail-developpeur-cms/home/catalogue-des-api/documentation-des-api/api/api-offres-demploi-v2/rechercher-par-criteres.html)):
- the maximal value for the first element of range is 1000 
- the maximal value for the second element of range is 1149
- the number of result for a given requests must be inferior or equals to 150 

Hence for a given search, it is possible to get up to 1150 job offers, by modifying the value of the parameter `range` for each request (`0-149` then `150-299`, `300-449`, etc.). However some `search` might have much more than 1150 job offers. In this case one has to narrow down the search using additional parameters (for instance: by playing with the parameters `minCreationDate` and `maxCreationDate` of the request). 

**Limit rate** : The API limit rate is set to 3 requests per second.

**Equivalence between the *API Offres d'emploi v2* methods and this module methods**: The 2 main methods from *Api Offres d'emploi v2* have the same name in the python module (`search` and `referentiel`) and are methods of the module class `Api`. One notable difference is that the output of `search` of this module has an additional `Content-Range` entry (describe hereafter).

## 3. Examples
### 3.1. Search
#### Minimal example of search
The _API Offres d'emploi v2_ has default parameters, so we can make a requests without parameters (will return the latest job offers) :
```python
basic_search = client.search()
```
The output of the module's `Api.search` method is the same as the _Api Offres d'emploi v2_ (dictionnary with entries `filtresPossibles` and `resultats`) with an additional entry, `Content-Range`, that gives the first and last index used for the `range` parameter along with the total number of available job offers for this request. For instance : 
```python
basic_search['Content-Range']
```
will output :
```python
{'first_index': '0', 'last_index': '149', 'max_results': '300749'}
```
The other fields (`filtresPossibles` and `resultats`) are explored further the [section 4](#4-analysis-of-the-search-output).

#### A more complex search
A more sensible approach would be to search for special keyword over a certain period, for instance the job offers with that include the keyword _big data_ since 2020-03-01 at 12h30. 
```python
from offres_emploi.utils import dt_to_str_iso
import datetime

start_dt = datetime.datetime(2020, 3, 1, 12, 30)
end_dt = datetime.datetime.today()
params = {
    "motsCles": "data science",
    'minCreationDate': dt_to_str_iso(start_dt),
    'maxCreationDate': dt_to_str_iso(end_dt)
}
search_on_big_data = client.search(params=params)
```

The full list of parameters for the `search` request are available in the page [Rechercher par critères](https://www.emploi-store-dev.fr/portail-developpeur-cms/home/catalogue-des-api/documentation-des-api/api/api-offres-demploi-v2/rechercher-par-criteres.html). These parameters are passed as dictionary to the parameter `params`. Note that the keys of this dictionnary are in camelCase, as in the _API Offres d'emploi v2_ specification. Also, we feed a `datetime` object to the helper function `dt_to_str_iso` to convert it to a string with the appropriate [ISO-8601](https://www.w3.org/TR/NOTE-datetime) format required by the API.

### 3.2. Referentiel
Getting reference source (_referentiel_ in french) is more straightforward since it does not need any parameter ; one just need to specify the desired reference source:
```python
referentiel_metiers = client.referentiel('metiers')
```
It will output the following list of dictionnaries: 
```python
[{'code': '1',
  'libelle': "Métiers de l'environnement et du développement durable"},
 {'code': '2',
  'libelle': 'Métiers de la défense et de la sécurité publique (hors logistique, santé, tertiaire, restauration)'},
 {'code': '3',
  'libelle': "Métiers du patrimoine et de la restauration d'oeuvres d'art"},
 {'code': '4', 'libelle': "Métiers de l'intelligence économique"},
 {'code': '5', 'libelle': 'Métiers de la recherche'},
 ...
 ]
```

The full list of *referentiel* is available in the docstring of the method or in the [Référentiel page](https://www.emploi-store-dev.fr/portail-developpeur-cms/home/catalogue-des-api/documentation-des-api/api/api-offres-demploi-v2/referentiels.html) of the API.

## 4. Analysis of the search output
The output of the `Api.search` is a dictionary with three entries:

- *filtresPossibles*
- *resultats*
- *Content-Range*

The breakdown of the available job offers into different categories (type of contract, experience, qualification, nature of contract) are available in the _filtresPossibles_ field and the detailed view of the job offers in _resultats_ field.

```python
filters = search_on_big_data['filtresPossibles']
results =  search_on_big_data['resultats']
content_range = search_on_big_data['Content-Range']
```

The number of job offers available at this point in time for this search is given by:

```python
content_range['max_results']
```

### 4.1. Aggregate view of job offers
The helper function `filters_to_df` is used to convert the field `filtresPossibles` in a suitable format:

```python
from offres_emploi.utils import filters_to_df
filters_df = filters_to_df(filters)
```
It will output:
```python
           filtre valeur_possible  nb_resultats
0     typeContrat             CDD             3
1     typeContrat             CDI           138
2     typeContrat             LIB            37
3      experience               0            15
4      experience               1            96
5      experience               2            47
6      experience               3            20
7   qualification               0             4
8   qualification               9            76
9   qualification               X            98
10  natureContrat              E1           141
11  natureContrat              NS            37
```

It is then straightforward to plot these figures using the data visualization library [seaborn](https://seaborn.pydata.org/):

```python
import seaborn as sns
g = sns.FacetGrid(filters_df, col="filtre", sharex=False, sharey=False)
g = g.map(data=sns.barplot, row="valeur_possible", col="nb_resultats")
```

![barplot of the breakdown](/img/filters.png)


### 4.2 Detailed view of job offers
The detailed view _resultats_ has a more friendly structure and can be pass directly to a `pandas.DataFrame` constructor. For example, to  know the salary offered by the enterprises for this search:

```python
import pandas as pd
results_df = pd.DataFrame(results)
salary_by_enterprise = (
 results_df[['entreprise', 'salaire']]
 .dropna()
 .agg(dict(entreprise=lambda x: x.get('nom'),
           salaire=lambda x: x.get('commentaire')))
 .dropna(subset=["salaire"])
 .loc[lambda df: df.salaire.str.contains("\d+")]
 .sort_values("salaire")
)
```

It will output:

```python
                                  entreprise                        salaire
73                                CLEEVEN SE         25 - 45 k€ brut annuel
112                                    ASTEK         30 - 40 k€ brut annuel
113                                 ADSERVIO         30 - 50 k€ brut annuel
15                                   REDLEAN         30 - 50 k€ brut annuel
29                           EOLE CONSULTING         30 - 50 k€ brut annuel
66                               PHOENIX ISI         32 - 35 k€ brut annuel
12                          DGA DRH CPP SDCO         32 - 52 k€ brut annuel
109                                EXPERTEAM         35 - 45 k€ brut annuel
47                              GROUPE ASTEN         35 - 48 k€ brut annuel
16                                 ENERGISME         35 - 60 k€ brut annuel
90                                     VISEO         36 - 50 k€ brut annuel
80   SOCIETE ALTRAN, Bat Teck - E. Golf Park         38 - 42 k€ brut annuel
14                AINABL TECHNOLOGIES FRANCE         38 - 50 k€ brut annuel
68   SOCIETE ALTRAN, Bat Teck - E. Golf Park         40 - 45 k€ brut annuel
28                                   Katchme         40 - 50 k€ brut annuel
124                                 HUMAINEA         42 - 45 k€ brut annuel
79   SOCIETE ALTRAN, Bat Teck - E. Golf Park         45 - 48 k€ brut annuel
86                          DGA DRH CPP FDCO  A partir de 34 k€ brut annuel
114                     SILICOM REGION OUEST  A partir de 35 k€ brut annuel
17                                      SNEF  A partir de 40 k€ brut annuel
96                               NODYA GROUP  A partir de 40 k€ brut annuel
89                       QUADRA INFORMATIQUE  A partir de 45 k€ brut annuel
35                                   Hunteed  A partir de 49 k€ brut annuel
```
Now you know where to apply.










