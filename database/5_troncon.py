# -*- coding: utf-8 -*-

from neo4j import GraphDatabase
import csv
from metadata import *

uri = "neo4j://localhost:7687"
username = "test"
password = "testtest"
driver = GraphDatabase.driver(uri, auth=(username, password))


chemin = "/home/md_vandamme/PII/ZENODO/VERCORS/"
layerTronconIti = QgsVectorLayer(chemin + "mobilite.shp", "Network mobility", "ogr")


# =============================================================================
# -----------------------------------------------------------------------------
#       TRONCON - ITINERAIRE (follow)
#

seq = 1
for troncon in layerTronconIti.getFeatures():

    if len(troncon.geometry().asGeometryCollection()) > 1:
        print ('Multi')
        continue

    geom = troncon.geometry()
    geom.convertToSingleType()
    geomwkt = str(geom.asWkt())
    ordre = str(troncon['id'])
    iditi = str(troncon['iti'])

    cleabs = str(troncon['cleabs'])
    nature = str(troncon['nature'])

    # On regarde si le troncon est déjà inséré
    nb = 0
    req  = " MATCH (n:" + NODE_TRONCON_ROUTE + ") "
    req += " WHERE n.cleabs = '" + cleabs + "' "
    req += " RETURN count(n) as nb "
    recordsNB, summary, keys = driver.execute_query(req, database_="neo4j")
    for record in recordsNB:
        nb = int(record.data()['nb'])

    if nb <= 0:

        # ---------------------------------------------------------------------
        #  On crée le tronçon de route et sa géométrie
        query =  ' CREATE (t:' + NODE_TRONCON_ROUTE + ' {'
        query += '     cleabs: "' + cleabs + '", '
        query += '     length:"' + str(geom.length()) + '" '
        query += ' }) '
        query += ' CREATE (g:' + NODE_GEOM + ' {type:"' + ATT_LINESTRING + '", wkt: "'+ geomwkt +'"})'
        query += ' CREATE (t) -[r :' + REL_HAS_GEOM + ']-> (g) '
        query += ' RETURN g, t, r '
        records, summary, keys = driver.execute_query(query, database_="neo4j")

    # -------------------------------------------------------------------------
    # On ajoute le lien entre l'itinéraire et le tronçon
    # direction = True
    query  = ' MATCH (i:' + NODE_ROUTE + ' {id :"' + iditi + '"}), '
    query += '       (t:' + NODE_TRONCON_ROUTE + ' {cleabs:"' + cleabs + '"}) '
    query += ' CREATE (i) -[r :' + REL_FOLLOW + ' {'
    query += '                          order: "' + ordre + '" }]-> (t) '
    query += ' RETURN r '
    records, summary, keys = driver.execute_query(query, database_="neo4j")

print ('    fin troncon')


# =============================================================================
# -----------------------------------------------------------------------------
#       Connectivité des tronçons:
#
#  on est dans le cas du double sens
#

# liste des troncons
req  = " MATCH (t:" + NODE_TRONCON_ROUTE + ") -[:" + REL_HAS_GEOM + "]- (g:" + NODE_GEOM + ") "
req += " RETURN t.cleabs as cleabs, g.wkt as wkt "
recordsT1, summary, keys = driver.execute_query(req, database_="neo4j")
recordsT2, summary, keys = driver.execute_query(req, database_="neo4j")

for record1 in recordsT1:
    cleabs1 = str(record1.data()['cleabs'])
    g1 = QgsGeometry.fromWkt(record1.data()['wkt'])
    g1.convertToSingleType()
    g1 = g1.asPolyline()
    p1 = g1[0]
    p2 = g1[-1]

    for record2 in recordsT2:
        cleabs2 = str(record2.data()['cleabs'])
        g2 = QgsGeometry.fromWkt(record2.data()['wkt'])

        if cleabs1 == cleabs2:
            continue

        g2.convertToSingleType()
        g2 = g2.asPolyline()
        p3 = g2[0]
        p4 = g2[-1]

        if p1.distance(p3) < 0.5:
            nb = 0
            req  = " MATCH (n:" + NODE_TRONCON_ROUTE + ") -[:" + REL_CONNECT + "]- (t:" + NODE_TRONCON_ROUTE + ") "
            req += " WHERE n.cleabs = '" + cleabs1 + "' "
            req += "   and t.cleabs = '" + cleabs2 + "' "
            req += " RETURN count(n) as nb"
            records5, summary, keys = driver.execute_query(req, database_="neo4j")
            for record in records5:
                nb = int(record.data()['nb'])

            if nb <= 0:
                query  = ' MATCH (i:' + NODE_TRONCON_ROUTE + ' {cleabs :"' + cleabs1 + '"}), '
                query += '       (t:' + NODE_TRONCON_ROUTE + ' {cleabs :"' + cleabs2 + '"}) '
                query += ' CREATE (i) -[r :' + REL_CONNECT 
                query += '      {direction: "' + ATT_SENS_INVERSE + '"}]-> (t) '
                query += ' RETURN r '
                records, summary, keys = driver.execute_query(query, database_="neo4j")

        if p1.distance(p4) < 0.5:
            nb = 0
            req  = " MATCH (n:" + NODE_TRONCON_ROUTE + ") -[:" + REL_CONNECT + "]- (t:" + NODE_TRONCON_ROUTE + ") "
            req += " WHERE n.cleabs = '" + cleabs1 + "' "
            req += "   and t.cleabs = '" + cleabs2 + "' "
            req += " RETURN count(n) as nb"
            records5, summary, keys = driver.execute_query(req, database_="neo4j")
            for record in records5:
                nb = int(record.data()['nb'])

            if nb <= 0:
                query  = ' MATCH (i:' + NODE_TRONCON_ROUTE + ' {cleabs :"' + cleabs1 + '"}), '
                query += '       (t:' + NODE_TRONCON_ROUTE + ' {cleabs :"' + cleabs2 + '"}) '
                query += ' CREATE (i) -[r :' + REL_CONNECT 
                query += '      {direction: "' + ATT_SENS_SAME + '"}]-> (t) '
                query += ' RETURN r '
                records, summary, keys = driver.execute_query(query, database_="neo4j")

        if p2.distance(p3) < 0.5:
            nb = 0
            req  = " MATCH (n:" + NODE_TRONCON_ROUTE + ") -[:" + REL_CONNECT + "]- (t:" + NODE_TRONCON_ROUTE + ") "
            req += " WHERE n.cleabs = '" + cleabs1 + "' "
            req += "   and t.cleabs = '" + cleabs2 + "' "
            req += " RETURN count(n) as nb"
            records5, summary, keys = driver.execute_query(req, database_="neo4j")
            for record in records5:
                nb = int(record.data()['nb'])

            if nb <= 0:
                query  = ' MATCH (i:' + NODE_TRONCON_ROUTE + ' {cleabs :"' + cleabs1 + '"}), '
                query += '       (t:' + NODE_TRONCON_ROUTE + ' {cleabs :"' + cleabs2 + '"}) '
                query += ' CREATE (i) -[r :' + REL_CONNECT + ' {direction: "' + ATT_SENS_SAME + '"}]-> (t) '
                query += ' RETURN r '
                records, summary, keys = driver.execute_query(query, database_="neo4j")

        if p2.distance(p4) < 0.5:
            nb = 0
            req  = " MATCH (n:" + NODE_TRONCON_ROUTE + ") -[:" + REL_CONNECT + "]- (t:" + NODE_TRONCON_ROUTE + ") "
            req += " WHERE n.cleabs = '" + cleabs1 + "' "
            req += "   and t.cleabs = '" + cleabs2 + "' "
            req += " RETURN count(n) as nb"
            records5, summary, keys = driver.execute_query(req, database_="neo4j")
            for record in records5:
                nb = int(record.data()['nb'])

            if nb <= 0:
                query  = ' MATCH (i:' + NODE_TRONCON_ROUTE + ' {cleabs :"' + cleabs1 + '"}), '
                query += '       (t:' + NODE_TRONCON_ROUTE + ' {cleabs :"' + cleabs2 + '"}) '
                query += ' CREATE (i) -[r :' + REL_CONNECT + ' {direction: "' + ATT_SENS_INVERSE + '"}]-> (t) '
                query += ' RETURN r '
                records, summary, keys = driver.execute_query(query, database_="neo4j")

print ('    fin connectivité')


# =============================================================================
# -----------------------------------------------------------------------------
#       Création des noeuds et relations "incident":
#
#  on est dans le cas du double sens
#

# Liste des troncons
req  = " MATCH (g:" + NODE_GEOM + ") -[:" + REL_HAS_GEOM + "]- (t:" + NODE_TRONCON_ROUTE + ") "
# req += " WHERE t.cleabs = 'TRONROUT0000002209679382' "
req += " RETURN t.cleabs as cleabs, g.wkt as wkt "
records, summary, keys = driver.execute_query(req, database_="neo4j")

seq = 1
for record in records:
    # Construction du noeud candidat avec sa géométrie
    cleabs = str(record.data()['cleabs'])
    g = QgsGeometry.fromWkt(record.data()['wkt'])
    g.convertToSingleType()
    line = g.asPolyline()

    p1 = line[0]
    p2 = line[-1]
    # print (cleabs)
    # print (p1, p2)

    # On regarde si les noeuds existent déjà
    req =  " MATCH (n:" + NODE_NODE_ROUTE + ") -[:" + REL_HAS_GEOM + "]- (g:" + NODE_GEOM + ") "
    req += " RETURN g.wkt as wkt, n.id as id "
    records1, summary1, keys1 = driver.execute_query(req, database_="neo4j")
    ID_INI = -1
    trouveIni = False
    ID_FIN = -1
    trouveFin = False
    for record1 in records1:
        ide = str(record1.data()['id'])
        geom = QgsGeometry.fromWkt(record1.data()['wkt'])
        if geom.distance(QgsGeometry.fromPointXY(p1)) < 0.5:
            trouveIni = True
            #print ('-----')
            ID_INI = ide
        if geom.distance(QgsGeometry.fromPointXY(p2)) < 0.5:
            trouveFin = True
            #print ('+++++')
            ID_FIN = ide

    if not trouveIni:
        # print ('pas de noeud initial')
        # On crée le noeud source
        ID_INI = "N" + str(seq)
        # print ('    ', ID_INI)
        query =  ' CREATE (n:' + NODE_NODE_ROUTE + ' {id: "' + str(ID_INI) + '"})  '
        query += ' CREATE (g:' + NODE_GEOM + ' {type: "ATT_POINT", wkt:"' + p1.asWkt() + '"})  '
        query += ' CREATE (n) -[:' + REL_HAS_GEOM + ']-> (g) '
        query += ' RETURN n, g '
        records2, summary, keys = driver.execute_query(query, database_="neo4j")
        seq += 1
    #else:
    #    print ('Noeud initial : ', ID_INI)


    if not trouveFin:
        #print ('pas de noeud final')
        #print (ID_FIN)
        # On crée le noeud source
        ID_FIN = "N" + str(seq)
        # print ('    ', ID_FIN)
        query =  ' CREATE (n:' + NODE_NODE_ROUTE + ' {id: "' + str(ID_FIN) + '"})  '
        query += ' CREATE (g:' + NODE_GEOM + ' {type: "ATT_POINT", wkt:"' + p2.asWkt() + '"})  '
        query += ' CREATE (n) -[:' + REL_HAS_GEOM + ']-> (g) '
        query += ' RETURN n, g '
        records3, summary, keys = driver.execute_query(query, database_="neo4j")
        seq += 1
    #else:
    #    print ('Noeud final : ', ID_FIN)


    # on ajoute la relation SORTANT

    query  = " MATCH (t:" + NODE_TRONCON_ROUTE + " {cleabs: '" + cleabs + "'}) "
    query += ' MATCH (n:'  + NODE_NODE_ROUTE + '   {id: "' + str(ID_INI) + '"})  '
    query += ' CREATE (n) -[:' + REL_SORTANT + ']-> (t) '
    query += ' RETURN n, t '
    records4, summary, keys = driver.execute_query(query, database_="neo4j")

    # on ajoute la relation ENTRANT
    query  = " MATCH (t:" + NODE_TRONCON_ROUTE + " {cleabs: '" + cleabs + "'}) "
    query += ' MATCH (n:'  + NODE_NODE_ROUTE + '   {id: "' + str(ID_FIN) + '"})  '
    query += ' CREATE (n) -[:' + REL_ENTRANT + ']-> (t) '
    query += ' RETURN n, t '
    records4, summary, keys = driver.execute_query(query, database_="neo4j")

print ('    fin des noeuds')

driver.close()
print ('FIN')

