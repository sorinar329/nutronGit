
prefix = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX tax: <http://knowrob.org/kb/product-taxonomy.owl#>
            PREFIX ingredient: <http://purl.org/heals/ingredient/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
			PREFIX food: <http://purl.org/heals/food/>"""


# function that generates queries dynamically based on a given list
# def dynamicgeneration_filter_nutritions(list):
#     query = prefix + "\n" """
#     select distinct ?class1 ?label2 ?value{
#         ?food owl:sameAs ?class1.
#         ?food rdfs:subClassOf* ntr:Food.
#         ?food rdfs:label ?label2.
#         #a
#         BIND((#b) as ?value)
#     } ORDER BY DESC(?value)"""
#     i = 0
#     j = 1
#     while i < len(list):
#         substring = "?food rdfs:subClassOf* ?restriction" + str(j) + ".\n?restriction" + str(
#             j) + " rdf:type owl:Restriction.\n?restriction" + str(j) + " owl:onProperty/rdfs:isDefinedBy ntr:" + list[
#                         i] + ".\n?restriction" + str(j) + " owl:hasValue" + " ?value" + str(j)
#         substringb = "+?value" + str(j)
#         query = query.replace("#a", substring+".\n#a")
#         if i == 0:
#             query = query.replace("#b", substringb + "replace")
#         if i < (len(list) - 1) and i != 0:
#             query = query.replace("replace", "+?value"+str(j) +"replace")
#         if i == (len(list) - 1):
#             query = query.replace("replace","+?value"+str(j))
#         i += 1
#         j += 1
#
#     return query

def dynamicgeneration_filter_nutritions(list):
    query = """ PREFIX ntr: <http://localhost/usda_food_nutritions#>
    PREFIX tax: <http://knowrob.org/kb/product-taxonomy.owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    select distinct ?restriction ?food ?class ?label ?label2 ?value{
        ?food owl:sameAs ?class.
        ?food rdfs:subClassOf ntr:Food.
        #FILTER ( !strstarts(str(?class), "http://localhost/usda_food_nutritions#") )							
        FILTER ( !strstarts(str(?class), "http://knowrob.org/kb/product-taxonomy.owl#") )							
        ?class rdfs:label ?label.
        ?food rdfs:label ?label2.
        #a
        BIND((#b) as ?value)
    } ORDER BY DESC(?value)"""
    i = 0
    j = 1
    while i < len(list):
        substring = "?food rdfs:subClassOf ?restriction" + str(j) + ".\n?restriction" + str(
            j) + " rdf:type owl:Restriction.\n?restriction" + str(j) + " owl:onProperty/rdfs:isDefinedBy ntr:" + list[
                        i] + ".\n?restriction" + str(j) + " owl:hasValue" + " ?value" + str(j)
        substringb = "+?value" + str(j)
        query = query.replace("#a", substring+".\n#a")
        if i == 0:
            query = query.replace("#b", substringb + "replace")
        if i < (len(list) - 1) and i != 0:
            query = query.replace("replace", "+?value"+str(j) +"replace")
        if i == (len(list) - 1):
            query = query.replace("replace","+?value"+str(j))
        i += 1
        j += 1

    return query



# function that generates queries dynamically based on a given list and a category
def dynamicgeneration_filter_nutritions_category(list, category):
    query = prefix + "\n" """
    select distinct ?restriction ?food ?class1 ?label ?label2 ?value{
        ?food owl:sameAs ?class1.
        ?food rdfs:subClassOf* ntr:Food.
        #FILTER ( !strstarts(str(?class1), "http://localhost/usda_food_nutritions#") )							
        FILTER ( !strstarts(str(?class1), "http://knowrob.org/kb/product-taxonomy.owl#") )	
        ?food rdfs:subClassOf* ntr:%s.						
        ?class1 rdfs:label ?label.
        ?food rdfs:label ?label2.
        #a
        BIND((#b) as ?value)
    } ORDER BY DESC(?value)""" %category
    i = 0
    j = 1
    while i < len(list):
        substring = "?food rdfs:subClassOf* ?restriction" + str(j) + ".\n?restriction" + str(
            j) + " rdf:type owl:Restriction.\n?restriction" + str(j) + " owl:onProperty/rdfs:isDefinedBy ntr:" + list[
                        i] + ".\n?restriction" + str(j) + " owl:hasValue" + " ?value" + str(j)
        substringb = "+?value" + str(j)
        query = query.replace("#a", substring+".\n#a")
        if i == 0:
            query = query.replace("#b", substringb + "replace")
        if i < (len(list) - 1) and i != 0:
            query = query.replace("replace", "+?value"+str(j) +"replace")
        if i == (len(list) - 1):
            query = query.replace("replace","+?value"+str(j))
        i += 1
        j += 1

    return query


# function that generates queries dynamically based on a given list
def dynamicgeneration_union(list):
        query = prefix + "\n" """
			select distinct ?recipe ?label where {
                 ?recipe rdf:type ingredient:Recipe.
                 ?recipe ntr:component/food:hasIngredient ?ing.
                 ?recipe rdfs:label ?label.
                 ?ing rdfs:subClassOf* ?restriction.
                 ?restriction rdf:type owl:Restriction.
                 ?restriction owl:onProperty ?property.
                 #a

            }"""
        i = 0
        j = 0
        while i < len(list):
            substring = "{?property rdfs:isDefinedBy " + list[j] + " }"
            if i == 0:
                query = query.replace("#a", substring+"\n#a")
            else:
                query = query.replace("#a", "UNION" + substring+"\n#a")
            i+=1
            j+=1
        return query


#print(dynamicgeneration_filter_nutritions(['Starch', 'Sugar']))
triplyprefix = """
 PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX tax: <http://purl.org/ProductKG/product-taxonomy#>
    PREFIX nutri: <http://purl.org/ProductKG/nutrition#>
            \n"""
def triply_dynamicgeneration_filter(list):
    query = triplyprefix + """select ?food ?label ?value where {
    
    #a
    ?food rdfs:label ?label.
    BIND((#b) as ?value)
    
    }OrderBy Desc(?value)"""

    x = len(list)
    i = 0
    j = 0
    while i < x:
        substring = "?cut" + str(i+1) + " owl:intersectionOf" + " ?res" + str(i+1) + ".\n" + "?res" + str(i+1) + \
                    " rdf:first/owl:someValuesFrom nutri:" + list[j] + ".\n" "?res" + str(i+1) +\
                    " rdf:rest/rdf:rest/rdf:first/owl:hasValue " + "?value" + str(i+1) + ".\n" + "?food" + \
                    " rdfs:subClassOf" + " ?cut" + str(i+1) + ".\n"

        query = query.replace("#a", substring + "\n#a" )
        substringb = "+?value" + str(j+1)
        if i == 0:
            query = query.replace("#b", substringb + "replace")
        if i < (len(list) - 1) and i != 0:
            query = query.replace("replace", "+?value" + str(j+1) + "replace")
        if i == (len(list) - 1):
            query = query.replace("replace", "+?value" + str(j+1))
        j += 1
        i += 1
    return query

def textmaniptest():
    return 0
    #print(triply_dynamicgeneration_filter(['calcium','iron']))
    #2400 Ergebnisse soll das haben circa.


textmaniptest()
#print(dynamicgeneration_union(['A', 'B', 'C', 'D']))