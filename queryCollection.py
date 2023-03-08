from SPARQLWrapper import SPARQLWrapper, JSON

import textManipulation
from textManipulation import dynamicgeneration_filter_nutritions
from textManipulation import dynamicgeneration_union
from textManipulation import dynamicgeneration_filter_nutritions_category

# endpoint connection
sparqlurl = SPARQLWrapper("https://graphdb.informatik.uni-bremen.de:7200/repositories/nonfoodkg")
sparqlurl2 = SPARQLWrapper("https://api.krr.triply.cc/datasets/mkumpel/ProductKG/services/ProductKG/sparql")

#Query to get only the ingredients which are associated with a symptom or a disease
def get_harmful_ingredients_of_product(ean):
    s = ean
    sparql = sparqlurl2
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")

    sparql.setQuery("""
PREFIX symp: <http://purl.org/ProductKG/symptom-disease#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tax: <http://purl.org/ProductKG/product-taxonomy#>
PREFIX trust: <http://purl.org/ProductKG/trust#>
PREFIX gr: <http://purl.org/goodrelations/v1#>
PREFIX in: <http://purl.org/ProductKG/nonfoodingredient#>
PREFIX disease: <http://purl.org/ProductKG/disease#>
PREFIX inDisease: <http://purl.org/ProductKG/ingredient-disease#>
SELECT DISTINCT  ?ingredient ?label ?productName ?productEAN WHERE {


  ?disease rdfs:subClassOf ?r1.
  ?r1 rdf:type owl:Restriction.
  ?r1 owl:onProperty inDisease:is_triggered_by.
  ?r1 owl:someValuesFrom ?ingredient.
    OPTIONAL{
  ?ingredient rdfs:subClassOf ?subClass.

    ?subClass rdfs:label ?label.
    FILTER(LANG(?label)="en")
  }



  ?product a tax:Product.
  ?in1 rdf:type ?ingredient.
  ?product in:has_ingredient ?in1.
  ?product gr:name ?productName.
  ?product gr:hasEAN_UCC-13 "%s".

}""" % s)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

def get_product_name(ean):
    s = ean
    sparql = sparqlurl2
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")

    sparql.setQuery("""
PREFIX gr: <http://purl.org/goodrelations/v1#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?productName WHERE {
  ?product gr:hasEAN_UCC-13 "%s".
  ?product gr:name ?productName
} LIMIT 1""" %s)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

#Query to get all ingredients of a product given its ean number
def get_Ingredients_of_Prod(prodEAN):
    sparql = sparqlurl2
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery("""
PREFIX in: <http://purl.org/ProductKG/nonfoodingredient#>
PREFIX gr: <http://purl.org/goodrelations/v1#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?productName ?ingredient ?label WHERE {
  ?product gr:hasEAN_UCC-13 "%s".
  ?product gr:name ?productName.
  ?product in:has_ingredient ?ingredient.

}
        """ % prodEAN)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


prefix = """
    PREFIX symp: <http://purl.org/ProductKG/symptom#>
    PREFIX symp-nutrition: <http://purl.org/ProductKG/symptom-nutrition#>
    PREFIX user: <http://purl.org/ProductKG/user-profile#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX nutri: <http://purl.org/ProductKG/food-nutrition#>
    PREFIX nutrition: <http://purl.org/ProductKG/nutrition#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX tax: <http://purl.org/ProductKG/product-taxonomy#>
            \n"""

sparqlurltripy = "https://api.krr.triply.cc/datasets/mkumpel/ProductKG/services/ProductKG/sparql"
def triply_query_products():
    spq = SPARQLWrapper(sparqlurltripy)
    sparql = spq
    query = """
       SELECT distinct ?food ?label  WHERE {
  ?food rdfs:subClassOf ?sup . 
  FILTER NOT EXISTS{?sub rdfs:subClassOf ?food FILTER(?sub != ?food && ?sub != owl:Nothing )}
  ?sup rdfs:subClassOf | rdfs:subClassOf/rdfs:subClassOf | rdfs:subClassOf/rdfs:subClassOf/rdfs:subClassOf nutri:Food.
  ?food rdfs:label ?label
}"""
    sparql.setQuery(prefix + query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def triply_query_filter(products):
    spq = SPARQLWrapper(sparqlurltripy)
    sparql = spq
    sparql.setQuery(textManipulation.triply_dynamicgeneration_filter(products))

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def triply_query_nutrient_products_percategory(age, gender, activity, category, product, unit):
    spq = SPARQLWrapper(sparqlurltripy)
    sparql = spq
    if category == "vitamin" or "minerals":
        query = """ SELECT ?intake ?label ?nutrient ?unit ?value ?value2 ?coverage WHERE {
                  ?user user:has_age_group user:%s.
                  ?user user:has_gender user:%s.
                  ?user nutri:has_energy_independent_intake | nutri:%s ?intake.
                  ?intake ?recommended_intake ?value.
                  ?recommended_intake rdfs:isDefinedBy ?nutrient.
                
                  ?cut owl:intersectionOf ?res.
                  ?res rdf:first/owl:someValuesFrom ?nutrient.
                  ?nutrient rdfs:subClassOf*/rdfs:subClassOf nutrition:%s.
                  ?nutrient rdfs:label ?label.
                  FILTER (lang(?label) = 'en')
                  ?res rdf:rest/rdf:first/owl:someValuesFrom ?unit.
                  ?res rdf:rest/rdf:rest/rdf:first/owl:hasValue ?value2.
                  nutri:%s rdfs:subClassOf ?cut.
                
                  Bind((?value2 * 100 / ?value) * %s  as ?coverage)
           } Order By (?food)""" % (age, gender, activity, category, product, unit)
    if category == "lipid":
        query = """ SELECT ?intake ?nutrient ?label ?unit ?value ?value2 ?coverage WHERE {
                          ?user user:has_age_group user:%s.
                          ?user user:has_gender user:%s.
                          ?user nutri:has_energy_independent_intake | nutri:%s ?intake.
                          ?intake ?recommended_intake ?value.
                          ?recommended_intake rdfs:isDefinedBy ?nutrient.

                          ?cut owl:intersectionOf ?res.
                          ?res rdf:first/owl:someValuesFrom ?nutrient.
                          {?nutrient rdfs:subClassOf*/rdfs:subClassOf nutrition:%s.
                          }UNION
                          {nutrition:sterol rdfs:subClassOf ?nutrient.}
                          ?nutrient rdfs:label ?label.
                          FILTER (lang(?label) = 'en')
                          ?res rdf:rest/rdf:first/owl:someValuesFrom ?unit.
                          ?res rdf:rest/rdf:rest/rdf:first/owl:hasValue ?value2.
                          nutri:%s rdfs:subClassOf ?cut.

                          Bind((?value2 * 100 / ?value) * %s   as ?coverage)
                   } Order By (?food)""" % (age, gender, activity, category, product, unit)
    if category == "carbohydrates":
        query = """ SELECT ?intake ?label ?nutrient ?unit ?value ?value2 ?coverage WHERE {
                              ?user user:has_age_group user:%s.
                              ?user user:has_gender user:%s.
                              ?user nutri:has_energy_independent_intake | nutri:%s ?intake.
                              ?intake ?recommended_intake ?value.
                              ?recommended_intake rdfs:isDefinedBy ?nutrient.

                              ?cut owl:intersectionOf ?res.
                              ?res rdf:first/owl:someValuesFrom ?nutrient.
                              {?nutrient rdfs:subClassOf*/rdfs:subClassOf nutrition:%s.
                              }UNION
                              {nutrition:dietary_fibre rdfs:subClassOf ?nutrient.}
                              ?nutrient rdfs:label ?label.
                              FILTER (lang(?label) = 'en')
                              ?res rdf:rest/rdf:first/owl:someValuesFrom ?unit.
                              ?res rdf:rest/rdf:rest/rdf:first/owl:hasValue ?value2.
                              nutri:%s rdfs:subClassOf ?cut.

                              Bind((?value2 * 100/ ?value) * %s  as ?coverage)
                       } Order By (?food)""" % (age, gender, activity, category, product, unit)

    sparql.setQuery(prefix + query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def triply_query_nutrient_products_protein(age, gender, weight, product, unit):
    spq = SPARQLWrapper(sparqlurltripy)
    sparql = spq
    query = """
           SELECT ?intake ?label ?value ?nutrient ?unit ?value2 ?coverage WHERE {
  ?user user:has_age_group user:%s.
  ?user user:has_gender user:%s.
  ?user nutri:has_bodyweight_dependent_intake ?intake2.
  ?intake2 nutri:recommended_protein_intake ?proteinintake.
  nutri:recommended_protein_intake rdfs:isDefinedBy ?nutrient.
  Bind(?proteinintake * %s as ?value)

  ?cut owl:intersectionOf ?res.
  ?res rdf:first/owl:someValuesFrom nutrition:protein.
  ?res rdf:rest/rdf:first/owl:someValuesFrom ?unit.
  ?nutrient rdfs:label ?label.
  FILTER (lang(?label) = 'en')
  ?res rdf:rest/rdf:rest/rdf:first/owl:hasValue ?value2.
  nutri:%s rdfs:subClassOf ?cut.

  Bind((?value2 * 100 / ?value) * %s as ?coverage)
} Order By (?food)""" % (age, gender, weight, product, unit)
    sparql.setQuery(prefix + query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

def triply_query_symptoms_data():
    spq = SPARQLWrapper(sparqlurltripy)
    sparql = spq
    query = """SELECT distinct ?class ?label WHERE {
  ?class rdfs:subClassOf/rdfs:subClassOf symp:Symptom.
  ?class rdfs:label ?label
  FILTER(lang(?label) = "en")
    }"""
    sparql.setQuery(prefix + query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def triply_query_symptoms(symptom):
    spq = SPARQLWrapper(sparqlurltripy)
    sparql = spq
    query = """
    SELECT ?nutrient ?label WHERE {
 symp:%s rdfs:subClassOf ?res.
  ?res owl:someValuesFrom|owl:someValuesFrom/owl:unionOf/rdf:rest*/rdf:first ?nutrient.
  ?res owl:onProperty symp-nutrition:possible_treatment.
  ?nutrient rdfs:label ?label
  FILTER (lang(?label) = 'en')
    }"""  %symptom
    sparql.setQuery(prefix + query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]



# def test1():
#     products = ['iron','calcium']
#     a = triply_query_filter(products)
#     for item in a:
#         print(item["label"]["value"])
#
#
# def test2():
#     a = triply_query_nutrient_products_percategory("age19to25" , "female", "has_medium_intake", "vitamin", "Cheese_gouda", str(1.0))
#     for item in a:
#         print(item["label"]["value"])
#         print(item["unit"]["value"])
#         print(item["value2"]["value"])
#         print(item["value"]["value"])
#         print(item["coverage"]["value"])
#
# def test3():
#     a = triply_query_nutrient_products_protein("age19to25", "male", str(80), "Cheese_gouda", str(100) )
#     for item in a:
#         print(item["label"]["value"])
#         print(item["unit"]["value"])
#         print(item["value2"]["value"])
#         print(item["value"]["value"])
#         print(item["coverage"]["value"])
#
#
# def test4():
#     symp = "Headache"
#     a = triply_query_symptoms(symp)
#     for item in a:
#         print(item["label"]["value"])
#
# def test5():
#     a = triply_query_symptoms_data()
#     for item in a:
#         print(item["label"]["value"])
#         print(item["class"]["value"])
#
# test3()
