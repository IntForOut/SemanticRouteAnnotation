# -*- coding: utf-8 -*-

from metadata import *
from neo4j import GraphDatabase
from owlready2 import *



uri = "neo4j://localhost:7687"
username = "test"
password = "testtest"
driver = GraphDatabase.driver(uri, auth=(username, password))


# 'RoutePortion'
CLASS_SKOS = ['CompositionEnsemble', 'NomenclatureCoucheForestière',
              'LocationRelationship', 'SemanticRouteAnnotation',
              'RouteContext', 'RouteCharacteristic']

CLASS_PORTION = ['RoutePortion', 'PRI']






# =============================================================================
#

class OORClass:

    def __init__(self):
        self.fr_prefLabel = ''
        self.en_prefLabel = ''
        self.iri = ''
        self.id = ''
        self.parents = list()
        self.fr_altLabel = list()
        self.en_altLabel = list()
        self.comment = ''
        self.union = list()
        self.restriction = ''
        # isDefinedBy

    def addParent(self, p):
        self.parents.append(p)


# =============================================================================
#

chemin = "/home/md_vandamme/PII/SemanticRouteAnnotation/data/oor_v2_0_0.owl"
onto = get_ontology("file:///" + chemin).load()


listClasses = list(onto.classes())
print (len(listClasses))

listIndividus = list(onto.individuals())
print (len(listIndividus))


CLASSES_OR = []
CLASSES_SKOS = []
CLASSES_PORTION = []


# ThingClass
for o in listClasses:

    c = OORClass()
    c.id = o.iri.split('#')[1]
    c.iri = o.iri

    c.comment = ''
    if len(o.comment) > 0:
        c.comment = o.comment[0].replace('"', '\'')


    for label in o.prefLabel:
        if hasattr(label, 'lang'):
            if label.lang == 'en':
                c.en_prefLabel = locstr(label)
            if label.lang == 'fr':
                c.fr_prefLabel = locstr(label)


    for label in getattr(o, "altLabel", []):
        if isinstance(label, locstr) and label.lang == "fr":
            # print ('    ', locstr(label))
            if locstr(label) not in c.fr_altLabel:
                c.fr_altLabel.append(locstr(label))
        if isinstance(label, locstr) and label.lang == "en":
            if locstr(label) not in c.en_altLabel:
                c.en_altLabel.append(locstr(label))


    # La relation subClass est traduite par is_a
    parents = [p for p in o.is_a if isinstance(p, ThingClass)]
    for p in parents:
        c.addParent(p.iri.split('#')[1])


    # -------------------------------------------------------------------------
    if str(c.id) not in CLASS_SKOS and str(c.id) not in CLASS_PORTION:

        restrictions = [p for p in o.is_a if isinstance(p, Restriction)]
        for r in restrictions:
            # c.restriction = r
            prop = str(r.property).split('.')[1]
            if prop == 'aCommeCompositionEnsemble':
                val = str(r.value).split('.')[1]
                c.restriction = prop + "#" + val
    

        CLASSES_OR.append(c)

        query  = " CREATE ( r:" + NODE_CLASS_OOR + " { "
        query += "          uri: \"" + c.iri + "\", "
        query += "          comment: \"" + c.comment + "\", "
        query += "          id: \"" + c.id + "\", "
        query += "          prefLabel: \"" + c.fr_prefLabel + "\" "
        query += "          } ) RETURN r ";
        records, summary, keys = driver.execute_query(query, database_="neo4j")
                        
        for alt in c.fr_altLabel:
            query =  " CREATE ( r:" + NODE_ALT_LABEL + " { "
            query += "              alt: \"" + alt + "\", lang: 'fr' }) RETURN r "
            records, summary, keys = driver.execute_query(query, database_="neo4j")
                                
            query =  " MATCH (c:" + NODE_CLASS_OOR + ") WHERE c.uri = \"" + c.iri + "\" "
            query += " MATCH (a:" + NODE_ALT_LABEL + ") WHERE a.alt = \"" + alt + "\" "
            query += " CREATE (c) -[r:" + EDGE_HAS_ALTLABEL + "]-> (a) RETURN c, r, a "
            records, summary, keys = driver.execute_query(query, database_="neo4j")

        if hasattr(o, 'equivalent_to'):
            equivs = o.equivalent_to
            if len(equivs) > 0 and str(equivs[0]) != 'ontology.Feature':
                elts = str(equivs[0]).split(" | ")
                for elt in elts:
                    c.union.append(elt.strip().split('.')[1])


    # -------------------------------------------------------------------------
    elif str(c.id) not in CLASS_PORTION:
        CLASSES_SKOS.append(c)

        query  = " CREATE ( r:" + NODE_CLASS_SKOS + " { "
        query += "          uri: \"" + c.iri + "\", "
        query += "          comment: \"" + c.comment + "\", "
        query += "          id: \"" + c.id + "\", "
        query += "          prefLabel: \"" + c.fr_prefLabel + "\" "
        query += "          } ) RETURN r ";
        records, summary, keys = driver.execute_query(query, database_="neo4j")


    # -------------------------------------------------------------------------
    else:
        CLASSES_PORTION.append(c)

        query  = " CREATE ( r:" + NODE_CLASS_PORTION + " { "
        query += "          uri: \"" + c.iri + "\", "
        query += "          comment: \"" + c.comment + "\", "
        query += "          id: \"" + c.id + "\", "
        query += "          prefLabel: \"" + c.fr_prefLabel + "\" "
        query += "          } ) RETURN r ";
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        # restriction ??
        restrictions = [p for p in o.is_a if isinstance(p, Restriction)]
        for r in restrictions:
            # c.restriction = r
            prop = str(r.property).split('.')[1]
            val = str(r.value).split('.')[1]
            c.restriction = prop + "#" + val
            #print (c.restriction)



# ------ SUBCLASS_OF ------
for c in CLASSES_OR:
    for parent in c.parents:
        query =  " MATCH (e:" + NODE_CLASS_OOR + ") WHERE e.uri = \"" + c.iri + "\" "
        query += " MATCH (p:" + NODE_CLASS_OOR + ") WHERE p.id = \"" + str(parent) + "\" "
        query += " CREATE (e) -[r:" + EDGE_SUBCLASS + "]-> (p) RETURN e, r, p "
        records, summary, keys = driver.execute_query(query, database_="neo4j")




# =============================================================================
#    SKOS

# les entités
for c in CLASSES_SKOS:

    # Récupérer l'objet classe depuis l'ontologie
    classe = getattr(onto, c.id)
    # print ('+++', classe.__name__)

    # ------ SUBCLASS_OF ------
    for parent in c.parents:
        query =  " MATCH (e:" + NODE_CLASS_SKOS + ") WHERE e.uri = \"" + c.iri + "\" "
        query += " MATCH (p:" + NODE_CLASS_SKOS + ") WHERE p.id = \"" + str(parent) + "\" "
        query += " CREATE (e) -[r:" + EDGE_SUBCLASS + "]-> (p) RETURN e, r, p "
        records, summary, keys = driver.execute_query(query, database_="neo4j")


    # ------ NAMED Individual ------
    for individu in listIndividus:
        if isinstance(individu, classe) and c.id != 'SemanticRouteAnnotation' and c.id != 'NomenclatureCoucheForestière':

            lab = ''
            for label in getattr(individu, "label", []):
                if isinstance(label, locstr) and label.lang == "fr":
                    lab = locstr(label)

            # print (individu.name, c.id)
            query  = " MATCH (c:" + NODE_CLASS_SKOS + ") WHERE c.id = \"" + c.id + "\" "
            query += ' CREATE (e:' + NODE_INDIVIDU + '{id: "' + individu.name + '", prefLabel: "' + lab + '"}) '
            query += " CREATE (e) -[r:" + REL_TYPE + "]-> (c) "
            query += " RETURN e, r, c "
            records, summary, keys = driver.execute_query(query, database_="neo4j")



# =============================================================================
#    PROPERTY

for c in CLASSES_OR:
    if c.restriction != "":
        prop = c.restriction.split('#')[0]
        val = c.restriction.split('#')[1]
        # print (prop, val)

        query =  " MATCH (p:" + NODE_CLASS_OOR + ") WHERE p.uri = \"" + c.iri + "\" "
        query += " MATCH (g:" + NODE_INDIVIDU + ") WHERE g.id = \"" + str(val) + "\" "
        query += " CREATE (p) -[r:aCommeCompositionEnsemble]-> (g) "
        query += " RETURN p, g, r "
        records, summary, keys = driver.execute_query(query, database_="neo4j")


for c in CLASSES_SKOS:
    # Récupérer l'objet classe depuis l'ontologie
    classe = getattr(onto, c.id)

    for individu in listIndividus:
        if isinstance(individu, classe) and c.id != 'SemanticRouteAnnotation' and c.id != 'NomenclatureCoucheForestière':
            # locationRelation
            if c.id  == 'RouteContext':
                valprop = str(individu.locationRelation[0])
                val = valprop.split('.')[1]
                # print (val, individu.name, 'locationRelation')

                query =  " MATCH (rl:" + NODE_INDIVIDU + ") WHERE rl.id = \"" + val + "\" "
                query += " MATCH (a:" + NODE_INDIVIDU + ") WHERE a.id = \"" + individu.name + "\" "
                query += " CREATE (a) -[r:locationRelation]-> (rl) "
                query += " RETURN a, rl, r "
                records, summary, keys = driver.execute_query(query, database_="neo4j")




# =============================================================================
#    PORTION

# les entités
for c in CLASSES_PORTION:

    # ------ SUBCLASS_OF ------
    for parent in c.parents:
        query =  " MATCH (e:" + NODE_CLASS_PORTION + ") WHERE e.uri = \"" + c.iri + "\" "
        query += " MATCH (p:" + NODE_CLASS_PORTION + ") WHERE p.id = \"" + str(parent) + "\" "
        query += " CREATE (e) -[r:" + EDGE_SUBCLASS + "]-> (p) RETURN e, r, p "
        records, summary, keys = driver.execute_query(query, database_="neo4j")



# =============================================================================
#    CLasses Landmarks de référence pour les RouteContext
#
#  on le fait à la main: ajouter une relation "referencedLandmark"
#
for individu in listIndividus:

    if individu.name  == 'longer_lac':
        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"lac\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"retenue\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"étang\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

    if individu.name  == 'longer_foret':
        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt_de_conifères\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt_de_feuillus\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt_mixtes\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

    if individu.name  == 'longer_haie':
        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

    if individu.name  == 'traverser_foret':
        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt_de_conifères\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt_de_feuillus\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"forêt_mixtes\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

    if individu.name  == 'prendre_pont':
        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"pont\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"passerelle\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

    if individu.name  == 'proche_access_routier':
        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"parking\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"parking_touristique_isole\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"gare\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

    if individu.name  == 'point_de_cheminement':
        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"abri\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"refuge\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"sommet\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"pic\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"grotte\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"gouffre\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")


        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"col\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"panneau\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"ruine\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")


    if individu.name  == 'proche_commodité':
        
        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"aire_de_pique-nique\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"fontaine\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")

        query =  " MATCH (l:" + NODE_CLASS_OOR + ") WHERE l.id = \"banc\" "
        query += " MATCH (i:" + NODE_INDIVIDU + ") WHERE i.id = \"" + individu.name + "\" "
        query += " CREATE (i) -[r:referencedLandmark]-> (l) "
        query += " RETURN i, r, l "
        records, summary, keys = driver.execute_query(query, database_="neo4j")






# =============================================================================
#
driver.close()

print ('FIN')




