# SemanticRouteAnnotation

<p align="center">
<table style="border:none;border:0;width:60%"><tr>
  <td align="center" style="width:30%">...</td>
  <td style="padding:16px;"><label>SemanticRouteAnnotation:</label> a source code for loading semantic annotations into a graph database and performing semantic queries.</td>
</tr></table>
</p>

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Code source License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Supported Python Versions](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)







## Prerequisites

Créer une base de données neo4j et un utilisateur qui a les bons droits. La version de la base utilisée est la 5.24. Il faut aussi installer les plugins suivants : 


Certains scripts écrits en python utilisent l'API QGIS et doivent donc être lancés dans la console python de QGIS.


## Data Description


1/ S'appuie sur la version 2.0 de l'ontologie des objets de repères qui est fournie dans le répertoire *data* et dont les évolutions sont référencées dans le dépôt github: 


2/ Sur un jeu d'annotations et d'itinéraires déposés sur une plateforme de dépôt de données ouvertes *Zenodo*: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17930773.svg)](https://doi.org/10.5281/zenodo.17930773)

The 13 routes, derived from diverse collaborative sources, are stored in the file routes.csv. The geometries of the routes were map-matched to the BDTOPO road network representing the mobility network and are stored in the mobilite layer of the GeoPackage. The map-matching process is described in: https://doi.org/10.1080/23729333.2019.1615730.

The semantic annotations of the routes are also stored in the GeoPackage in the following layers:

    pii_balcons for route segments running along balconies,

    pii_lacet for route segments consisting of a series of hairpin bends,

    pii_foret for segments running along or through forests,

    pii_lac for route segments running along lakes,

    pii_pont for segments crossing bridges.



3/ Les POI :
- les 5 fichiers CSV contenant les landmarks sont extraits du jeu de données sur Zenodo ... et sur la zone d'étude







## Charger la base de données


1°) Les 3 premiers peuvent lanceScript 1


4°) A lancer dans QGIS:
-


## Requêtes



## Citation

Ce travail a été publié dans ce rapport technique:

<div style="background-color:rgba(200, 200, 200, 0.0470588); text-align:left; vertical-align: middle; padding:10px;">
.......
</div>



## Special thanks to
<ul>
<li></li>
<li></li>
<li></li>
</ul>


## Development

License: MIT LICENSE

Institute: LASTIG, Univ Gustave Eiffel, Geodata-Paris, IGN

Authors: [Marie-Dominique Van Damme](https://www.umr-lastig.fr/mdvandamme/)



