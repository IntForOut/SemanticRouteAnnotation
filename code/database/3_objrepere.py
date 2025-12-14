# -*- coding: utf-8 -*-

import csv
from neo4j import GraphDatabase
from metadata import *
import psycopg2
import shapely
import sys

CSV_PATH = '/home/md_vandamme/PII/SemanticRouteAnnotation/data/landmark/'

uri = "neo4j://localhost:7687"
username = "test"
password = "testtest"
driver = GraphDatabase.driver(uri, auth=(username, password))


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
    request =  " MATCH ( t:" + NODE_OR + " {"
    request += "          id_source: \"" + idToponyme + "\", "
    request += "          source: \"" + source + "\" }) "
    request += " MATCH (c:" + NODE_CLASS_OOR + "{ "
    request += "          uri: \"" + uri + "\" }) "
    request += " CREATE (t) -[r:" + REL_IS_A + "]-> (c) RETURN t, r, c "
    records, summary, keys = driver.execute_query(request, database_="neo4j")


def isToponymeExist(driver, idToponyme, source):
    nbCP = 0

    request =  " MATCH (w:" + NODE_OR
    request += "            { id_source: \"" + idToponyme + "\", "
    request += "              source: \"" + source + "\" }) "
    request += " RETURN count(w) as nb "
    records, summary, keys = driver.execute_query(request, database_="neo4j")
    for record in records:
        nbCP = int(record.data()['nb'])
    return (nbCP > 0)



def insertObjetRepere(driver, table, source):
    with open(CSV_PATH + table + '.csv', 'r') as fichier:
        reader = csv.reader(fichier, delimiter = ';')
        for ligne in reader:
            idToponyme = ligne[1]
            nomToponyme = ligne[2]
            typeToponyme = ligne[3]
            uri = ligne[4]

            wkt = ligne[0]
            if wkt == 'WKT' and idToponyme == 'id':
                continue

            mp = shapely.from_wkt(wkt)
            wkt = str(mp.geoms[0])

            if not isToponymeExist(driver, idToponyme, source):
                addToponyme(driver, idToponyme, nomToponyme, typeToponyme, source)
                addGeometry(driver, idToponyme, wkt, ATT_POINT, source)
                addEdgeInstanceToponyme(driver, idToponyme, uri, source)
            else:
                print (source + ": doublon")





# =============================================================================
# =============================================================================
print ('C2C')
insertObjetRepere (driver, 'c2c', NODE_C2C)

print ('PARC')
insertObjetRepere (driver, 'parc', NODE_PARC)

print ('REFINFO')
insertObjetRepere (driver, 'refugesinfo', NODE_REF_INFO)

print ('OSM')
insertObjetRepere (driver, 'osm', NODE_OSM)

print ('BDTOPO')
insertObjetRepere (driver, 'bdtopo', NODE_BDTOPO)

print ('    fin ObjetRepere')



# =============================================================================
# =============================================================================

def addMatching(driver, idRef, idCandidat, source):
    request  = " MATCH (t1:" + NODE_OR
    request += "     { id_source : \"" + idRef + "\", source: \"" + source + "\"   }) "
    request += " MATCH (t2:" + NODE_OR
    request += "     { id_source: \"" + idCandidat + "\", source: \"" + NODE_BDTOPO + "\" }) "
    request += " CREATE (t2) <-[r:" + REL_SAME_AS + "]- (t1) RETURN r ";
    records, summary, keys = driver.execute_query(request, database_="neo4j")


def addRelationSameAs(driver, table, source):
    try:
        pg_connection_dict = {
            'dbname': 'repere',
            'user': 'test',
            'password': 'test',
            'port': 5433,
            'host': 'localhost'
        }
        conn = psycopg2.connect(**pg_connection_dict)
    
        query =  " Select idsource, idcandidat "
        query += " From " + table + " "
        query += " Where typematching = '1:1 validated' "
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    
        for row in rows:
            idRef = row[0]
            idCandidat = row[1]
            addMatching(driver, idRef, idCandidat, source)
    
    except Exception as e:
        sys.stderr.write("Unable to connect to database\n")
        conn = None
        print(e)


print ('C2C')
addRelationSameAs(driver, 'matching_c2c_bdtopo', NODE_C2C)

print ('PARC')
addRelationSameAs(driver, 'matching_parc_bdtopo', NODE_PARC)

print ('REFINFO')
addRelationSameAs(driver, 'matching_refinfo_bdtopo', NODE_REF_INFO)

print ('OSM')
addRelationSameAs(driver, 'matching_osm_bdtopo', NODE_OSM)


print ('    fin sameAs')


# =============================================================================
# =============================================================================

# Des isA qui manquent

# Bancs : 'amenity#bench', 'bench#yes'
query  = " MATCH  (c:LandmarkClass) WHERE c.id = 'banc'  "
query += " MATCH  (l:LANDMARK) WHERE l.nature in ['amenity#bench', 'bench#yes'] "
query += " CREATE (l) -[r:isA]-> (c) RETURN c, l, r "
records, summary, keys = driver.execute_query(query, database_="neo4j")









# =============================================================================
# =============================================================================
driver.close()
print ('FIN')


