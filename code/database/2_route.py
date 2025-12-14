# -*- coding: utf-8 -*-

from neo4j import GraphDatabase
import csv

from metadata import *

uri = "neo4j://localhost:7687"
username = "test"
password = "testtest"
driver = GraphDatabase.driver(uri, auth=(username, password))

with open("/home/md_vandamme/PII/ZENODO/VERCORS/routes.csv", newline="") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=";", doublequote=True)

    next(spamreader)

    for fields in spamreader:
        if len(fields) <= 0:
            continue

        iditi = fields[0]
        titre = fields[1]

        if iditi == "27606" or iditi == "30683" or iditi == "45405" or iditi == "27592":
            source = NODE_PARC
        elif iditi == "376275" or iditi == "24596" or iditi == "571521":
            source = NODE_VISORANDO
        elif iditi == "17660" or iditi == "22594" or iditi == "13627" or iditi == "1955":
            source = NODE_ALTRANDO
        elif iditi == "55536":
            source = NODE_C2C
        elif iditi == "293730":
            source = NODE_CIRKWI
        else:
            print ('Aucune source identifiée pour cet itinéraire')

        query =  ' CREATE (e:' + NODE_ROUTE + ' {'
        query += '             id: "' + iditi + '", '
        query += '             dataSource: "' + source + '", '
        query += '             title: "' + titre + '"}) '
        query += ' RETURN e '
        # print (query)
        records, summary, keys = driver.execute_query(query, database_="neo4j")


driver.close()
