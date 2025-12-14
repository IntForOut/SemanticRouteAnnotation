# -*- coding: utf-8 -*-

from neo4j import GraphDatabase
from metadata import *
import psycopg2
import sys

uri = "neo4j://localhost:7687"
username = "test"
password = "testtest"
driver = GraphDatabase.driver(uri, auth=(username, password))


chemin = "/home/md_vandamme/PII/SemanticRouteAnnotation/data/topo/"


def isToponymeExist(driver, id_source, source):
    nbCP = 0

    request =  " MATCH (w:" + NODE_OR
    request += "            { id_source: \"" + id_source + "\", "
    request += "              source: \"" + source + "\" }) "
    request += " RETURN count(w) as nb "
    records, summary, keys = driver.execute_query(request, database_="neo4j")
    for record in records:
        nbCP = int(record.data()['nb'])
    return (nbCP > 0);

def isToponymeNomExist(driver, nom_source, source):
    nbCP = 0
    ids = -1
    request =  " MATCH (w:" + NODE_OR
    request += "            { nom: \"" + nom_source + "\", "
    request += "              source: \"" + source + "\" }) "
    request += " RETURN count(w) as nb, w.id_source as id "
    records, summary, keys = driver.execute_query(request, database_="neo4j")
    for record in records:
        nbCP = int(record.data()['nb'])
        ids = str(record.data()['id'])
    return (nbCP > 0, ids)

def addToponyme(driver, idToponyme, nomToponyme, nature, source):
    nomToponyme = nomToponyme.replace("\"", "'")
    request =  " CREATE ( t:" + NODE_OR + " {"
    request += "          id_source: \"" + idToponyme + "\", "
    request += "          source: \"" + source + "\", "
    request += "          nom: \"" + nomToponyme.replace("\"", "'") + "\", "
    request += "          nature: \"" + nature + "\" "
    request += " }) return t "
    # print (request)
    records, summary, keys = driver.execute_query(request, database_="neo4j")

def addGeometry(driver, idToponyme, wkt, typegeom, source):
    request =  " MATCH (t:" + NODE_OR + " {"
    request += "          id_source: \"" + idToponyme + "\" , "
    request += "          source: \"" + source + "\" }) "
    request += " CREATE ( g:" + NODE_GEOM + "{ "
    request += "          type:\"" + typegeom + "\", wkt: \"" + wkt + "\" })  "
    request += " CREATE (t) -[r:" + REL_HAS_GEOM + "]-> (g) RETURN t, r, g "
    # print (request)
    records, summary, keys = driver.execute_query(request, database_="neo4j")

def addEdgeInstanceToponyme(driver, idToponyme, uri, source):
    # replace("&apos;", "'")
    request =  " MATCH ( t:" + NODE_OR + " {"
    request += "          id_source: \"" + idToponyme + "\", "
    request += "          source: \"" + source + "\" }) "
    request += " MATCH (c:" + NODE_CLASS_OOR + "{ "
    request += "                  uri: \"" + uri + "\" }) "
    request += " CREATE (t) -[r:" + REL_IS_A + "]-> (c) RETURN t, r, c "
    # print (request)
    records, summary, keys = driver.execute_query(request, database_="neo4j")


# =============================================================================
# Attention, le toponyme n'existe pas toujours
def addLac():

    # Lac
    layerLac = QgsVectorLayer(chemin + "lac.shp", "lac", "ogr")

    for lac in layerLac.getFeatures():
        geom = lac.geometry()
        geom.convertToSingleType()
        geomwkt = str(geom.asWkt())

        cleabs = str(lac['ID'])
        toponyme = str(lac['TOPONYME'])
        nature = str(lac['NATURE'])

        if nature == 'Lac':
            uri = 'http://purl.org/choucas.ign.fr/oor#lac'
        if nature == 'Retenue':
            uri = 'http://purl.org/choucas.ign.fr/oor#retenue'
        if nature == 'Réservoir-bassin':
            uri = 'http://purl.org/choucas.ign.fr/oor#réservoir'

        # print (cleabs, toponyme, nature)


        existe = isToponymeNomExist(driver, toponyme, NODE_BDTOPO)
        if existe[0] and toponyme is not NULL and toponyme != '' and toponyme != 'NULL':
            cleabs = existe[1]

            # on supprimer isA
            request =  " MATCH (w:" + NODE_OR + ") -[r:isA]- (c:LandmarkClass) "
            request += " WHERE w.id_source = \"" + cleabs + "\" "
            request += " DELETE r "
            records, summary, keys = driver.execute_query(request, database_="neo4j")

            # On ajoute le lien entre le lac et la géométrie
            query =  ' MATCH (t:' + NODE_OR + ' { '
            query += '          id_source:"' + cleabs + '", '
            query += '          source:"' + NODE_BDTOPO + '"}) '
            query += ' CREATE (g:' + NODE_GEOM + ' { '
            query += '           type:"' + ATT_POLYGON + '", '
            query += '           wkt: "'+ geomwkt +'"})'
            query += ' CREATE (t) -[r :' + REL_HAS_GEOM + ']-> (g) '
            query += ' RETURN g, r '
            records, summary, keys = driver.execute_query(query, database_="neo4j")

            addEdgeInstanceToponyme(driver, cleabs, uri, NODE_BDTOPO)
        else:
            # print (cleabs)
            toponyme = ""
            addToponyme(driver, cleabs, toponyme, nature, NODE_BDTOPO)
            addGeometry(driver, cleabs, geomwkt, ATT_POLYGON, NODE_BDTOPO)
            addEdgeInstanceToponyme(driver, cleabs, uri, NODE_BDTOPO)




def addPont():

    # 'Mur', 'Ruines', 'pont'
    layerPont = QgsVectorLayer(chemin + "pont.shp", "pont", "ogr")

    for pont in layerPont.getFeatures():
        geom = pont.geometry()
        geom.convertToSingleType()
        geomwkt = str(geom.asWkt())

        cleabs = str(pont['ID'])
        toponyme = str(pont['TOPONYME'])
        nature = str(pont['NATURE'])
        nat_detail = str(pont['NAT_DETAIL'])
        # print (nature, nat_detail)
        # print (toponyme)

        # CONSLINE0000000007530888    Ruines
        # CONSLINE0000000332220458  Ruines
        # CONSLINE0000000333269209    Ruines
        # CONSLINE0000000256893034    Pont        Pont de l'Amour
        # CONSLINE0000000007530887    Pont

        if nature == 'Pont':
            uri = 'http://purl.org/choucas.ign.fr/oor#pont'
        if nature == 'Ruines':
            uri = 'http://purl.org/choucas.ign.fr/oor#ruine'

        TAB = ['CONSLINE0000000007530888', 'CONSLINE0000000332220458',
               'CONSLINE0000000333269209', 'CONSLINE0000000256893034', 'CONSLINE0000000007530887']
        if cleabs not in TAB:
            continue

        # if toponyme != None and toponyme != '' and toponyme != 'NULL':
        if isToponymeExist(driver, cleabs, NODE_BDTOPO):
            # On ajoute le lien entre le pont et la géométrie
            query = ' MATCH (t:' + NODE_OR + ' {id_source:"' + cleabs + '", source:"' + NODE_BDTOPO + '"}) '
            query += ' CREATE (g:' + NODE_GEOM + ' {type:"' + ATT_LINESTRING + '", wkt: "'+ geomwkt +'"})'
            query += ' CREATE (t) -[r :' + REL_HAS_GEOM + ']-> (g) '
            query += ' RETURN g, r '
            records, summary, keys = driver.execute_query(query, database_="neo4j")
        else:
            # on Crée le toponyme
            addToponyme(driver, cleabs, toponyme, nature, NODE_BDTOPO)
            addGeometry(driver, cleabs, geomwkt, ATT_LINESTRING, NODE_BDTOPO)
            addEdgeInstanceToponyme(driver, cleabs, uri, NODE_BDTOPO)


def addForet():

    layerVeget = QgsVectorLayer(chemin + "veget.shp", "veget", "ogr")

    for veget in layerVeget.getFeatures():

        geom = veget.geometry()
        # geom.convertToSingleType()
        geomwkt = str(geom.asWkt())

        cleabs = str(veget['ID'])
        nature = str(veget['NATURE'])
        # print (cleabs, nature)

        uri = ''
        if nature == 'Bois':
            uri = 'http://purl.org/choucas.ign.fr/oor#bois'
        elif nature == 'Forêt fermée de conifères':
            uri = 'http://purl.org/choucas.ign.fr/oor#forêt_de_conifères'
        elif nature == 'Forêt fermée de feuillus':
            uri = 'http://purl.org/choucas.ign.fr/oor#forêt_de_feuillus'
        elif nature == 'Forêt fermée mixte':
            uri = 'http://purl.org/choucas.ign.fr/oor#forêt_mixtes'
        elif nature == 'Haie':
            uri = 'http://purl.org/choucas.ign.fr/oor#haie'
        elif nature == 'Vigne':
            uri = 'http://purl.org/choucas.ign.fr/oor#vigne'
        elif nature == 'Forêt ouverte':
            uri = 'http://purl.org/choucas.ign.fr/oor#forêt'
        elif nature == 'Verger':
            uri = 'http://purl.org/choucas.ign.fr/oor#verger'
        else:
            print ('non reconnue:', nature)


        # on Crée le toponyme
        addToponyme(driver, cleabs, '', nature, NODE_BDTOPO)
        addGeometry(driver, cleabs, geomwkt, ATT_POLYGON, NODE_BDTOPO)
        addEdgeInstanceToponyme(driver, cleabs, uri, NODE_BDTOPO)



# =============================================================================
# Attention, le toponyme n'existe pas toujours
def addTroncon():

    layerTroncon = QgsVectorLayer(chemin + "TRONCON_DE_ROUTE.shp", "TRONCON_DE_ROUTE", "ogr")

    for troncon in layerTroncon.getFeatures():

        geom = troncon.geometry()
        geom.convertToSingleType()
        geomwkt = str(geom.asWkt())

        cleabs = str(troncon['ID'])
        nature = str(troncon['NATURE'])

        uri = ''
        if nature == 'Sentier':
            uri = 'http://purl.org/choucas.ign.fr/oor#sentier'
        elif nature == 'Chemin':
            uri = 'http://purl.org/choucas.ign.fr/oor#chemin'
        elif nature == 'Route empierrée':
            uri = 'http://purl.org/choucas.ign.fr/oor#route'
        elif nature == 'Route à 1 chaussée':
            uri = 'http://purl.org/choucas.ign.fr/oor#route'
        elif nature == 'Rond-point':
            uri = 'http://purl.org/choucas.ign.fr/oor#rond_point'
        elif nature == 'Escalier':
            uri = 'http://purl.org/choucas.ign.fr/oor#escalier'
        else:
            print (nature, ' uri non traitée')


        # on Crée le toponyme
        addToponyme(driver, cleabs, '', nature, NODE_BDTOPO)
        addGeometry(driver, cleabs, geomwkt, ATT_LINESTRING, NODE_BDTOPO)
        addEdgeInstanceToponyme(driver, cleabs, uri, NODE_BDTOPO)


# =============================================================================
# Attention, le toponyme n'existe pas toujours
def addParking():
    # Parking
    layerParking = QgsProject.instance().mapLayersByName('equipement')[0]
    layerParking = QgsVectorLayer(chemin + "equipement.shp", "equipement", "ogr")

    for equipement in layerParking.getFeatures():
        geom = equipement.geometry()
        geom.convertToSingleType()
        geomwkt = str(geom.asWkt())

        cleabs     = str(equipement['ID'])
        toponyme   = str(equipement['TOPONYME'])
        nature     = str(equipement['NATURE'])
        nat_detail = str(equipement['NAT_DETAIL'])

        if nature != 'Parking' and nature != 'Gare routière':
            continue

        if nat_detail != None and nat_detail != '' and nat_detail != 'NULL':
            nature = nat_detail
        #print(nature)

        uri = ''
        if nature == 'Parking':
            uri = 'http://purl.org/choucas.ign.fr/oor#parking'
        elif nature == 'Parking touristique isolé':
            uri = 'http://purl.org/choucas.ign.fr/oor#parking_touristique_isole'
        elif nature == 'Gare routière':
            uri = 'http://purl.org/choucas.ign.fr/oor#gare_routière'
        else:
            print (nature, ' uri non traitée')


        if isToponymeExist(driver, cleabs, NODE_BDTOPO):
            # On ajoute le lien entre le equipement et la géométrie
            query =  ' MATCH (t:' + NODE_OR + ' { '
            query += '          id_source:"' + cleabs + '", '
            query += '          source:"' + NODE_BDTOPO + '"}) '
            query += ' CREATE (g:' + NODE_GEOM + ' { '
            query += '           type:"' + ATT_POLYGON + '", '
            query += '           wkt: "'+ geomwkt +'"})'
            query += ' CREATE (t) -[r :' + REL_HAS_GEOM + ']-> (g) '
            query += ' RETURN g, r '
            records, summary, keys = driver.execute_query(query, database_="neo4j")

            # On ajoute une deuxième nature
            addEdgeInstanceToponyme(driver, cleabs, uri, NODE_BDTOPO)

        else:
            addToponyme(driver, cleabs, toponyme, nature, NODE_BDTOPO)
            addGeometry(driver, cleabs, geomwkt, ATT_POLYGON, NODE_BDTOPO)
            addEdgeInstanceToponyme(driver, cleabs, uri, NODE_BDTOPO)






# =============================================================================
# =============================================================================

addLac()
print ('    Lac OK')
addPont()
print ('    Pont OK')
addForet()
print ('    Vegetation OK')
addTroncon()
print ('    Troncon routier OK')
addParking()
print ('    Parking OK')


print ('Fin Geometrie géo')
driver.close()
print ('FIN')

