# SemanticRouteAnnotation

A source code for loading semantic annotations into a graph database and performing semantic queries.

<br/>

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Code source License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Supported Python Versions](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)


...


> README Contents
> - [Prerequisites](#Prerequisites)
> - [Data Description](#Data-Description)
> - [Purpose of the Python Scripts](#Purpose-of-the-Python-Scripts)
>     * [Loading data](#Loading Data in the Graph Database)
>     * [Semantic Queries](#Performing Semantic Queries)
> - [Special thanks](#Special thanks)
> - [Development](#Development)
> - [Acknowledgments](#Acknowledgments)


<br/>

## Prerequisites

- A Neo4j database and a user with the appropriate permissions have been created. The database version used is 5.24. You also need to install the following plugin: APOC (5.24.2).

- Some Python scripts use the QGIS API and therefore need to be run in the QGIS Python console.


<br/>

## Data Description


1/ S'appuie sur la version 2.0 de l'ontologie des objets de repères qui est fournie dans le répertoire *data* et dont les évolutions sont référencées dans le dépôt github: 


2/ Sur un jeu d'annotations et d'itinéraires déposés sur une plateforme de dépôt de données ouvertes *Zenodo*: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17930773.svg)](https://doi.org/10.5281/zenodo.17930773)

The 13 routes, derived from diverse collaborative sources, are stored in the file routes.csv. The geometries of the routes were map-matched to the BDTOPO road network representing the mobility network and are stored in the mobilite layer of the GeoPackage. The map-matching process is described in: https://doi.org/10.1080/23729333.2019.1615730.

The semantic annotations of the routes are also stored in the GeoPackage in the following layers:

* *pii_balcons* for route segments running along balconies,

* *pii_lacet* for route segments consisting of a series of hairpin bends,

* *pii_foret* for segments running along or through forests,

* *pii_lac* for route segments running along lakes,

* *pii_pont* for segments crossing bridges.



3/ Les POI :
- les 5 fichiers CSV contenant les landmarks sont extraits du jeu de données sur Zenodo ... et sur la zone d'étude





<br/>

## Purpose of the Python Scripts

### Loading Data in the Graph Database


1°) Les 3 premiers peuvent lanceScript 1


2°) A lancer dans QGIS:
-


### Performing Semantic Queries



<br/>

## How to cite

Ce travail a été publié dans ce rapport technique:

<div style="background-color:rgba(200, 200, 200, 0.0470588); text-align:left; vertical-align: middle; padding:10px;">
.......
</div>

<br/>

## Special thanks
<ul>
<li></li>
<li></li>
<li></li>
</ul>

<br/>

## Development

License: MIT LICENSE

Institute: LASTIG, Univ Gustave Eiffel, Geodata-Paris, IGN

Authors: [Marie-Dominique Van Damme](https://www.umr-lastig.fr/mdvandamme/)


<br/>

## Acknowledgments

This work was supported by the ANR research project **[IntForOut](https://www.umr-lastig.fr/intforout/)**: Multisource spatial data INTegration FOR the Monitoring of Ecosystems under the pressure of OUTdoor recreation (ANR-23-CE55-0003).

