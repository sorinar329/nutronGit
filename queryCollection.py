from SPARQLWrapper import SPARQLWrapper, JSON

import textManipulation
from textManipulation import dynamicgeneration_filter_nutritions
from textManipulation import dynamicgeneration_union
from textManipulation import dynamicgeneration_filter_nutritions_category

# endpoint connection
#https://graphdb.informatik.uni-bremen.de:7200/repositories/nonfoodkg
#http://DESKTOP-NJVHG71:7200/repositories/test123
sparqlurl = SPARQLWrapper("https://graphdb.informatik.uni-bremen.de:7200/repositories/nonfoodkg")

# query for the conjuction of nutrients which result in a product that contains at least the given nutrients
def filter_conjuction_nutrients(list):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery(dynamicgeneration_filter_nutritions(list))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

# query for the conjuction of nutrients which result in a product that contains at least the given nutrients
def filter_conjuction_nutrients_category(list, category):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery(dynamicgeneration_filter_nutritions_category(list, category))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for recommended recipes for a given symptom
def recipe_for_symptom(list):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery(dynamicgeneration_union(list))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for the nutritional coverage of the 'other' category for a recipe
def recipe_coverage_others(gender, age, activity, ingredient1, portions):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery("""
         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                    PREFIX ntr: <http://localhost/usda_food_nutritions#>
                                    PREFIX ingredient: <http://purl.org/heals/ingredient/>
                                    PREFIX food: <http://purl.org/heals/food/>

    select ?intake ?nutrient ?nutrient ?label ?unit (SUM(?coverage2) as ?totalCoverage) (SUM(?totalvalue)as ?abc)  {
        ?idv ntr:has_gender ntr:%s.
        ?idv ntr:has_age_group ntr:%s.
        ?idv ntr:has_energy_independent_intake|ntr:%s ?low.
        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Vitamin}
        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Minerals}
        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Lipid}
        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Carbohydrates}
        ?property rdfs:isDefinedBy ?nutrient.
        ?nutrient rdfs:label ?label.
        FILTER (lang(?label) = 'en')
        ?property rdfs:subPropertyOf ntr:has_nutrient.
        ?property ntr:unit ?unit.
        ?low ?recommended ?intake.
        ?recommended rdfs:isDefinedBy ?nutrient.

        %s ntr:component ?comp.
        %s food:serves ?portion.
        ?comp food:hasIngredient ?ing.
        ?comp ntr:amount ?amount

        Bind(((?amount / 100)/?portion)*%s as ?factor)

        ?ing rdfs:subClassOf ?restriction.
        ?restriction rdf:type owl:Restriction.
        ?restriction owl:onProperty/rdfs:isDefinedBy ?nutrient.
        ?restriction owl:hasValue ?value

        Bind((?value * ?factor) / ?intake * 100 as ?coverage )

        %s food:serves ?portions

        Bind((?coverage / ?portions) as ?coverage2)
        Bind((?intake/100)*?coverage2 as ?totalvalue)

        } GROUP BY ?intake ?nutrient ?label ?unit 
                                    """ % (
    gender, age, activity, ingredient1, ingredient1, portions, ingredient1))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for the protein intake of a product
def protein_intake(product, gender, age, weight, unit):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    print(product)
    if "ingredient" in product:
        sparql.setQuery("""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX tax: <http://knowrob.org/kb/product-taxonomy.owl#>
            PREFIX ingredient: <http://purl.org/heals/ingredient/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
			SELECT DISTINCT ?class ?nutrient ?label ?unit ?value ?intake ?coverage ?valueb
            WHERE {?class owl:sameAs %s.
    				?class rdfs:subClassOf ntr:Food.
                    ?class rdfs:subClassOf ?restriction.

                    ?restriction rdf:type owl:Restriction.
                    Bind(?restriction as ?restriction2)
                    Bind(?restriction as ?restriction3)
		
                    ?restriction owl:hasValue ?value.
                    ?restriction2 owl:onProperty ?property.
                    ?property rdfs:isDefinedBy ntr:Protein.
					?property rdfs:isDefinedBy ?nutrient.
    				?property ntr:unit ?unit.
    				?nutrient rdfs:label ?label.
    				#FILTER ( !strstarts(str(?class), "http://localhost/usda_food_nutritions#") )
                    FILTER (lang(?label) = 'en')
                    ?idv ntr:has_gender ntr:%s.
                    ?idv ntr:has_age_group ntr:%s.
                    ?idv ntr:has_bodyweight_dependent_intake ?b.
                    ?b ntr:recommended_protein_intake ?c.
    				bind((?c*%s) as ?intake  )
    				bind((?value*100 / ?intake)*%s as ?coverage)
                    bind((?value)*%s as ?valueb)
    				#bind ((?valueb/xsd:integer(?intake))*100 as ?coverage)
            }""" %(product, gender, age, weight, unit, unit))
    elif "ntr" in product:
        sparql.setQuery("""PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX tax: <http://knowrob.org/kb/product-taxonomy.owl#>
            PREFIX ingredient: <http://purl.org/heals/ingredient/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
			SELECT DISTINCT ?class ?nutrient ?label ?unit ?value ?intake ?coverage ?valueb
            WHERE {
    				%s rdfs:subClassOf ?restriction.
					
                    ?restriction rdf:type owl:Restriction.
                    Bind(?restriction as ?restriction2)
                    Bind(?restriction as ?restriction3)
		
                    ?restriction owl:hasValue ?value.
                    ?restriction2 owl:onProperty ?property.
                    ?property rdfs:isDefinedBy ntr:Protein.
					?property rdfs:isDefinedBy ?nutrient.
    				?property ntr:unit ?unit.
    				?nutrient rdfs:label ?label.
    				#FILTER ( !strstarts(str(?class), "http://localhost/usda_food_nutritions#") )
                    FILTER (lang(?label) = 'en')
                    ?idv ntr:has_gender ntr:%s.
                    ?idv ntr:has_age_group ntr:%s.
                    ?idv ntr:has_bodyweight_dependent_intake ?b.
                    ?b ntr:recommended_protein_intake ?c.
    				bind((?c*%s) as ?intake  )
    				bind((?value*100 / ?intake)*%s as ?coverage)
    				bind((?value)*%s as ?valueb)
                    }"""% (product, gender, age, weight, unit, unit))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def query_reference(product, category, gender, age, activity, unit):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    if "ingredient" in product:
        sparql.setQuery("""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX ptx: <http://knowrob.org/kb/product-taxonomy.owl#>
            PREFIX ingredient: <http://purl.org/heals/ingredient/>

            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT ?class ?label ?nutrient ?unit ?value ?valueb ?intake ?coverage
            WHERE {?class owl:sameAs %s.
                    ?class rdfs:subClassOf ?restriction.
                    ?nutrient rdfs:subClassOf ntr:%s.

                    ?restriction rdf:type owl:Restriction.
                    Bind(?restriction as ?restriction2)
                    Bind(?restriction as ?restriction3)

                    ?restriction owl:hasValue ?value.
                    ?restriction2 owl:onProperty ?property.
                    ?property rdfs:isDefinedBy ?nutrient.
                    ?nutrient rdfs:label ?label.
                    FILTER (lang(?label) = 'en')
                    ?property ntr:unit ?unit.

    				?idv ntr:has_gender ntr:%s.
                    ?idv ntr:has_age_group ntr:%s.
                    ?idv ntr:has_energy_independent_intake|ntr:%s ?a.
                    ?recommended rdfs:isDefinedBy ?nutrient.
                    ?a ?recommended ?intake
                    bind((?value*%s) as ?valueb)
    				bind ((?valueb/(?intake))*100 as ?coverage)

        }
        """ % (product, category, gender, age, activity, unit))


    elif "ntr" in product:
        sparql.setQuery("""
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ntr: <http://localhost/usda_food_nutritions#>
                    PREFIX ptx: <http://knowrob.org/kb/product-taxonomy.owl#>
                    PREFIX ingredient: <http://purl.org/heals/ingredient/>

                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT DISTINCT ?class ?label ?nutrient ?unit ?value ?valueb ?intake ?coverage
                    WHERE {
                            %s rdfs:subClassOf ?restriction.
                            ?nutrient rdfs:subClassOf ntr:%s.

                            ?restriction rdf:type owl:Restriction.
                            Bind(?restriction as ?restriction2)
                            Bind(?restriction as ?restriction3)

                            ?restriction owl:hasValue ?value.
                            ?restriction2 owl:onProperty ?property.
                            ?property rdfs:isDefinedBy ?nutrient.
                            ?nutrient rdfs:label ?label.
                            FILTER (lang(?label) = 'en')
                            ?property ntr:unit ?unit.

            				?idv ntr:has_gender ntr:%s.
                            ?idv ntr:has_age_group ntr:%s.
                            ?idv ntr:has_energy_independent_intake|ntr:%s ?a.
                            ?recommended rdfs:isDefinedBy ?nutrient.
                            ?a ?recommended ?intake
                            bind((?value*%s) as ?valueb)
            				bind ((?valueb/(?intake))*100 as ?coverage)
                }
                """ % (product, category, gender, age, activity, unit))

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def query_reference_others(product, gender, age, activity, unit):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    if "ingredient" in product:
        sparql.setQuery("""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX ptx: <http://knowrob.org/kb/product-taxonomy.owl#>
            PREFIX ingredient: <http://purl.org/heals/ingredient/>

            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT ?class ?label ?nutrient ?unit ?value ?valueb ?intake ?coverage
            WHERE {?class owl:sameAs %s.
                    ?class rdfs:subClassOf ?restriction.
                    ?nutrient rdfs:subClassOf ntr:Nutritional_Component.
    				FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Vitamin}
    				FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Minerals}
    				FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Lipid}
    				FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Carbohydrates}

                    ?restriction rdf:type owl:Restriction.
                    Bind(?restriction as ?restriction2)
                    Bind(?restriction as ?restriction3)

                    ?restriction owl:hasValue ?value.
                    ?restriction2 owl:onProperty ?property.
                    ?property rdfs:isDefinedBy ?nutrient.
                    ?nutrient rdfs:label ?label.
                    FILTER (lang(?label) = 'en')
                    ?property ntr:unit ?unit.

    				?idv ntr:has_gender ntr:%s.
                    ?idv ntr:has_age_group ntr:%s.
                    ?idv ntr:has_energy_independent_intake|ntr:%s ?a.
                    ?recommended rdfs:isDefinedBy ?nutrient.
                    ?a ?recommended ?intake
                    bind((?value*%s) as ?valueb)
    				bind ((?valueb/(?intake))*100 as ?coverage)

        }
        """ % (product, gender, age, activity, unit))


    elif "ntr" in product:
        sparql.setQuery("""
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ntr: <http://localhost/usda_food_nutritions#>
                    PREFIX ptx: <http://knowrob.org/kb/product-taxonomy.owl#>
                    PREFIX ingredient: <http://purl.org/heals/ingredient/>

                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT DISTINCT ?class ?label ?nutrient ?unit ?value ?valueb ?intake ?coverage
                    WHERE {
                            %s rdfs:subClassOf ?restriction.
                            ?nutrient rdfs:subClassOf ntr:Nutritional_Component.
    				        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Vitamin}
    				        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Minerals}
    				        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Lipid}
    				        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Carbohydrates}

                            ?restriction rdf:type owl:Restriction.
                            Bind(?restriction as ?restriction2)
                            Bind(?restriction as ?restriction3)

                            ?restriction owl:hasValue ?value.
                            ?restriction2 owl:onProperty ?property.
                            ?property rdfs:isDefinedBy ?nutrient.
                            ?nutrient rdfs:label ?label.
                            FILTER (lang(?label) = 'en')
                            ?property ntr:unit ?unit.

            				?idv ntr:has_gender ntr:%s.
                            ?idv ntr:has_age_group ntr:%s.
                            ?idv ntr:has_energy_independent_intake|ntr:%s ?a.
                            ?recommended rdfs:isDefinedBy ?nutrient.
                            ?a ?recommended ?intake
                            bind((?value*%s) as ?valueb)
            				bind ((?valueb/(?intake))*100 as ?coverage)
                }
                """ % (product, gender, age, activity, unit))

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for the nutrients based on a symptom
def treatment_nutrients(symptoms):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery("""PREFIX ntr: <http://localhost/usda_food_nutritions#>
                    PREFIX tax: <http://knowrob.org/kb/product-taxonomy.owl#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ingredient: <http://purl.org/heals/ingredient/>

select distinct ?treatment ?label{
    					ntr:%s rdfs:subClassOf ?restriction.
                        ?restriction rdf:type owl:Restriction.
                        ?restriction owl:someValuesFrom ?treatment.
                        ?treatment rdfs:label ?label
                        FILTER (lang(?label) = 'en')
                        }""" % symptoms)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for all products in the NutrOn Ontology that have a link
def usda_query():
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery("""PREFIX ntr: <http://localhost/usda_food_nutritions#>
    PREFIX tax: <http://knowrob.org/kb/product-taxonomy.owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    select distinct ?food ?label{
            ?food rdfs:subClassOf/rdfs:subClassOf ntr:Food.
    		?food rdfs:label ?label.}""")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# all Products that are linked with the FoodKg
def foodOn_ing():
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery(""" PREFIX owl: <http://www.w3.org/2002/07/owl#>
                        PREFIX dct: <http://purl.org/dc/terms/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX ntr: <http://localhost/usda_food_nutritions#>
                        PREFIX tax: <http://knowrob.org/kg/ProductTaxonomy.owl#> 
                        
                        SELECT DISTINCT ?class ?label  WHERE{
                              	?ntr owl:sameAs ?class.
                                ?ntr rdfs:subClassOf ntr:Food.
    							FILTER ( !strstarts(str(?class), "http://localhost/usda_food_nutritions#") )
    							FILTER ( !strstarts(str(?class), "http://knowrob.org/kb/product-taxonomy.owl#") )
                                ?class rdfs:label ?label.
                            }""")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def coverage_recipe(gender, age, activity, ingredient1, ingredient2):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery(""" 
                               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                PREFIX ntr: <http://localhost/usda_food_nutritions#>
                                PREFIX ingredient: <http://purl.org/heals/ingredient/>
                                PREFIX food: <http://purl.org/heals/food/>

select ?intake ?nutrient (SUM(?coverage2) as ?totalCoverage)  {
    ?idv ntr:has_gender ntr:%s.
    ?idv ntr:has_age_group ntr:%s.
    ?idv ntr:%s ?low.
    ?low ?recommended ?intake.
    ?recommended rdfs:isDefinedBy ?nutrient.

    %s ntr:component ?comp.
    ?comp food:hasIngredient ?ing.
    ?comp ntr:amount ?amount

    Bind(?amount / 100 as ?factor)

    ?ing rdfs:subClassOf ?restriction.
    ?restriction rdf:type owl:Restriction.
    ?restriction owl:onProperty/rdfs:isDefinedBy ?nutrient.
    ?restriction owl:hasValue ?value

    Bind((?value * ?factor) / ?intake * 100 as ?coverage )

    %s food:serves ?portions

    Bind((?coverage / ?portions) as ?coverage2)

    } GROUP BY ?intake ?nutrient
                                """ % (gender, age, activity, ingredient1, ingredient2))

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for the products
def query_products():
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery(""" 
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX dct: <http://purl.org/dc/terms/>
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX ntr: <http://localhost/usda_food_nutritions#>
                            PREFIX tax: <http://knowrob.org/kg/ProductTaxonomy.owl#> 
                            PREFIX ingredient: <http://purl.org/heals/ingredient/>

                            SELECT DISTINCT ?class ?label  WHERE{
                                ?ntr owl:equivalentClass ?class.
                                ?ntr rdfs:subClassOf ntr:Food.
                                ?class rdfs:label ?label
                                FILTER(LANG(?label) = "" || LANGMATCHES(LANG(?label), "en"))
                            }
                            """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for all recipes that have ingredients
def query_recipes():
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery(""" 			
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX tax: <http://knowrob.org/kg/ProductTaxonomy.owl#> 
            PREFIX ingredient: <http://purl.org/heals/ingredient/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
			PREFIX food: <http://purl.org/heals/food/>
			SELECT DISTINCT ?class ?label WHERE{
    				?class rdf:type food:Recipe.
    				?class rdfs:label ?label.
    				?class ntr:component ?comp
    				
} """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for the products in a recipe
def query_products_in_recipe(recipe, portions):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery("""PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX tax: <http://knowrob.org/kg/ProductTaxonomy.owl#> 
            PREFIX ingredient: <http://purl.org/heals/ingredient/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
			PREFIX food: <http://purl.org/heals/food/>
			SELECT DISTINCT ?ing ?label ?amount ?class ?total WHERE{
    				%s ntr:component ?a.
    				%s	food:serves ?portion .
    				?a ntr:amount ?amount.
    				Bind((?amount*%s) / ?portion as ?total)
    				?a food:hasIngredient ?ing.
    			    #?ing rdfs:label ?label.
    				?ing owl:sameAs ?class.
    				?class rdfs:label ?label.
    				FILTER ( !strstarts(str(?class), "http://knowrob.org/kb/product-taxonomy.owl#") )
                    }""" %(recipe, recipe, portions))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# recipe query for a recipe
def query_recipe_protein(gender, age, ingredient1, portions):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery("""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX ntr: <http://localhost/usda_food_nutritions#>
                    PREFIX ingredient: <http://purl.org/heals/ingredient/>
                    PREFIX food: <http://purl.org/heals/food/>

select DISTINCT  ?nutrient ?label ?unit ?intake (SUM(?intake2) as ?abc) (SUM(?coverage)as ?totalCoverage)  {
     ?idv ntr:has_gender ntr:%s.
     ?idv ntr:has_age_group ntr:%s.
     ?idv ntr:has_bodyweight_dependent_intake ?b.
     ?b ntr:recommended_protein_intake ?c.
     %s ntr:component ?comp.
     %s food:serves ?portion.
     ?comp food:hasIngredient ?ing.
     ?comp ntr:amount ?amount.
	 ?ing rdfs:subClassOf ?restriction. 
     ?restriction owl:onProperty/rdfs:isDefinedBy ntr:Protein.
     ?restriction owl:hasValue ?value.
     ?restriction owl:onProperty ?property.
     ?property rdfs:isDefinedBy ntr:Protein.
     ?property rdfs:isDefinedBy ?nutrient.
     ?property ntr:unit ?unit.
     ?nutrient rdfs:label ?label.
     FILTER (lang(?label) = 'en')
     ?comp food:hasIngredient ?ing.
     ?comp ntr:amount ?amount
     Bind((?c*70) as ?intake).
     Bind((?amount / 100)/?portion * %s as ?factor)
    Bind((?factor*?value) as ?intake2)
    Bind((?intake2/?intake)*100 as ?coverage)
    } Group By ?intake ?nutrient ?unit ?label"""% (gender, age, ingredient1, ingredient1, portions))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for the nutritional informations of a recipe
def query_nutrient_recipe_percategory(gender, age, activity, category, ingredient1, portions):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    sparql.setQuery("""
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                PREFIX ntr: <http://localhost/usda_food_nutritions#>
                                PREFIX ingredient: <http://purl.org/heals/ingredient/>
                                PREFIX food: <http://purl.org/heals/food/>

select ?intake ?nutrient ?nutrient ?label ?unit (SUM(?coverage2) as ?totalCoverage) (SUM(?totalvalue)as ?abc)  {
    ?idv ntr:has_gender ntr:%s.
    ?idv ntr:has_age_group ntr:%s.
    ?idv ntr:has_energy_independent_intake|ntr:%s ?low.
    ?nutrient rdfs:subClassOf ntr:%s.
    ?property rdfs:isDefinedBy ?nutrient.
    ?nutrient rdfs:label ?label.
    FILTER (lang(?label) = 'en')
    ?property rdfs:subPropertyOf ntr:has_nutrient.
    ?property ntr:unit ?unit.
    ?low ?recommended ?intake.
    ?recommended rdfs:isDefinedBy ?nutrient.

    %s ntr:component ?comp.
    %s food:serves ?portion.
    ?comp food:hasIngredient ?ing.
    ?comp ntr:amount ?amount

    Bind(((?amount / 100)/?portion)*%s as ?factor)

    ?ing rdfs:subClassOf ?restriction.
    ?restriction rdf:type owl:Restriction.
    ?restriction owl:onProperty/rdfs:isDefinedBy ?nutrient.
    ?restriction owl:hasValue ?value

    Bind((?value * ?factor) / ?intake * 100 as ?coverage )

    %s food:serves ?portions

    Bind((?coverage / ?portions) as ?coverage2)
    Bind((?intake/100)*?coverage2 as ?totalvalue)
    
    } GROUP BY ?intake ?nutrient ?label ?unit 
                                """ % (gender, age, activity, category, ingredient1, ingredient1, portions, ingredient1))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for nutrient information of products
def query_reference(product, category, gender, age, activity, unit):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    if "ingredient" in product:
        sparql.setQuery("""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX ptx: <http://knowrob.org/kb/product-taxonomy.owl#>
            PREFIX ingredient: <http://purl.org/heals/ingredient/>
            
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT ?class ?label ?nutrient ?unit ?value ?valueb ?intake ?coverage
            WHERE {?class owl:sameAs %s.
                    ?class rdfs:subClassOf ?restriction.
                    ?nutrient rdfs:subClassOf ntr:%s.
                    
                    ?restriction rdf:type owl:Restriction.
                    Bind(?restriction as ?restriction2)
                    Bind(?restriction as ?restriction3)

                    ?restriction owl:hasValue ?value.
                    ?restriction2 owl:onProperty ?property.
                    ?property rdfs:isDefinedBy ?nutrient.
                    ?nutrient rdfs:label ?label.
                    FILTER (lang(?label) = 'en')
                    ?property ntr:unit ?unit.
    
    				?idv ntr:has_gender ntr:%s.
                    ?idv ntr:has_age_group ntr:%s.
                    ?idv ntr:has_energy_independent_intake|ntr:%s ?a.
                    ?recommended rdfs:isDefinedBy ?nutrient.
                    ?a ?recommended ?intake
                    bind((?value*%s) as ?valueb)
    				bind ((?valueb/(?intake))*100 as ?coverage)

        }
        """ % (product, category, gender, age, activity,unit))


    elif "ntr" in product:
        sparql.setQuery("""
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ntr: <http://localhost/usda_food_nutritions#>
                    PREFIX ptx: <http://knowrob.org/kb/product-taxonomy.owl#>
                    PREFIX ingredient: <http://purl.org/heals/ingredient/>

                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT DISTINCT ?class ?label ?nutrient ?unit ?value ?valueb ?intake ?coverage
                    WHERE {
                            %s rdfs:subClassOf ?restriction.
                            ?nutrient rdfs:subClassOf ntr:%s.

                            ?restriction rdf:type owl:Restriction.
                            Bind(?restriction as ?restriction2)
                            Bind(?restriction as ?restriction3)

                            ?restriction owl:hasValue ?value.
                            ?restriction2 owl:onProperty ?property.
                            ?property rdfs:isDefinedBy ?nutrient.
                            ?nutrient rdfs:label ?label.
                            FILTER (lang(?label) = 'en')
                            ?property ntr:unit ?unit.

            				?idv ntr:has_gender ntr:%s.
                            ?idv ntr:has_age_group ntr:%s.
                            ?idv ntr:has_energy_independent_intake|ntr:%s ?a.
                            ?recommended rdfs:isDefinedBy ?nutrient.
                            ?a ?recommended ?intake
                            bind((?value*%s) as ?valueb)
            				bind ((?valueb/(?intake))*100 as ?coverage)
                }
                """ % (product, category, gender, age, activity, unit))

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


# query for nutrient information of product for the 'other' category
def query_reference_others(product, gender, age, activity, unit):
    sparql = sparqlurl
    sparql.setCredentials("nonfoodkg", "nWOgDJkfYdXzYDW7vc3bYAHn3CGv0l")
    if "ingredient" in product:
        sparql.setQuery("""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ntr: <http://localhost/usda_food_nutritions#>
            PREFIX ptx: <http://knowrob.org/kb/product-taxonomy.owl#>
            PREFIX ingredient: <http://purl.org/heals/ingredient/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT ?class ?label ?nutrient ?unit ?value ?valueb ?intake ?coverage
            WHERE {?class owl:sameAs %s.
                    ?class rdfs:subClassOf ?restriction.
                    ?nutrient rdfs:subClassOf ntr:Nutritional_Component.
    				FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Vitamin}
    				FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Minerals}
    				FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Lipid}
    				FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Carbohydrates}

                    ?restriction rdf:type owl:Restriction.
                    Bind(?restriction as ?restriction2)
                    Bind(?restriction as ?restriction3)

                    ?restriction owl:hasValue ?value.
                    ?restriction2 owl:onProperty ?property.
                    ?property rdfs:isDefinedBy ?nutrient.
                    ?nutrient rdfs:label ?label.
                    FILTER (lang(?label) = 'en')
                    ?property ntr:unit ?unit.

    				?idv ntr:has_gender ntr:%s.
                    ?idv ntr:has_age_group ntr:%s.
                    ?idv ntr:has_energy_independent_intake|ntr:%s ?a.
                    ?recommended rdfs:isDefinedBy ?nutrient.
                    ?a ?recommended ?intake
                    bind((?value*%s) as ?valueb)
    				bind ((?valueb/(?intake))*100 as ?coverage)

        }
        """ % (product, gender, age, activity, unit))


    elif "ntr" in product:
        sparql.setQuery("""
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ntr: <http://localhost/usda_food_nutritions#>
                    PREFIX ptx: <http://knowrob.org/kb/product-taxonomy.owl#>
                    PREFIX ingredient: <http://purl.org/heals/ingredient/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT DISTINCT ?class ?label ?nutrient ?unit ?value ?valueb ?intake ?coverage
                    WHERE {
                            %s rdfs:subClassOf ?restriction.
                            ?nutrient rdfs:subClassOf ntr:Nutritional_Component.
    				        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Vitamin}
    				        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Minerals}
    				        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Lipid}
    				        FILTER NOT EXISTS {?nutrient rdfs:subClassOf ntr:Carbohydrates}

                            ?restriction rdf:type owl:Restriction.
                            Bind(?restriction as ?restriction2)
                            Bind(?restriction as ?restriction3)

                            ?restriction owl:hasValue ?value.
                            ?restriction2 owl:onProperty ?property.
                            ?property rdfs:isDefinedBy ?nutrient.
                            ?nutrient rdfs:label ?label.
                            FILTER (lang(?label) = 'en')
                            ?property ntr:unit ?unit.

            				?idv ntr:has_gender ntr:%s.
                            ?idv ntr:has_age_group ntr:%s.
                            ?idv ntr:has_energy_independent_intake|ntr:%s ?a.
                            ?recommended rdfs:isDefinedBy ?nutrient.
                            ?a ?recommended ?intake
                            bind((?value*%s) as ?valueb)
            				bind ((?valueb/(?intake))*100 as ?coverage)
                }
                """ % (product, gender, age, activity, unit))

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

prefix = """
    PREFIX symp: <http://purl.org/NonFoodKG/symptom#>
    PREFIX user: <http://purl.org/NonFoodKG/user-profile#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX nutri: <http://purl.org/NonFoodKG/food-nutrition#>
    PREFIX nutrition: <http://purl.org/NonFoodKG/nutrition#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX tax: <http://purl.org/NonFoodKG/product-taxonomy#>
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
    print(prefix + query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def triply_query_filter(products):
    spq = SPARQLWrapper(sparqlurltripy)
    sparql = spq
    sparql.setQuery(textManipulation.triply_dynamicgeneration_filter(products))
    print(textManipulation.triply_dynamicgeneration_filter(products))
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
    a = print(prefix + query)
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
    #print(prefix + query)
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
    a = print(prefix + query)
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
  ?nutrient rdfs:label ?label
  FILTER (lang(?label) = 'en')
    }"""  %symptom
    sparql.setQuery(prefix + query)
    a = print(prefix + query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]



def test1():
    products = ['iron','calcium']
    a = triply_query_filter(products)
    for item in a:
        print(item["label"]["value"])


def test2():
    a = triply_query_nutrient_products_percategory("age19to25" , "female", "has_medium_intake", "vitamin", "Cheese_gouda", str(1.0))
    for item in a:
        print(item["label"]["value"])
        print(item["unit"]["value"])
        print(item["value2"]["value"])
        print(item["value"]["value"])
        print(item["coverage"]["value"])

def test3():
    a = triply_query_nutrient_products_protein("age19to25", "male", str(80), "Cheese_gouda", str(100) )
    for item in a:
        print(item["label"]["value"])
        print(item["unit"]["value"])
        print(item["value2"]["value"])
        print(item["value"]["value"])
        print(item["coverage"]["value"])


def test4():
    symp = "Headache"
    a = triply_query_symptoms(symp)
    for item in a:
        print(item["label"]["value"])

def test5():
    a = triply_query_symptoms_data()
    for item in a:
        print(item["label"]["value"])
        print(item["class"]["value"])
#test5()
