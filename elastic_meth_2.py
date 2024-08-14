"""

  Author:
  * Eugenie Karadjoff
  <eugenie.karadjoff@free.fr> -- it will change in the near future, but works properly right now

  Organization and its members involved:
  LORIA - Laboratoire LOrrain de Recherche en Informatique et ses Applications (France) -- Team K :
  * Mathieu d'Aquin <mathieu.daquin@loria.fr>
  * Emmanuel Nauer <emmanuel.nauer@loria.fr>

  :purpose:
  * SEMANTIC project is pythom program that allows its users to make research on semantic web.
  It connects to any SPARQL endpoints, then extracts, sort and compile data in nosql database, and open
  possibility to launch researches upon them
  for every .py files, please refers to readme file because they are 3 versions of it for
  each function (extract, search)

  :license: without license, the default copyright laws apply.

  last update : July 2022

"""
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.helpers import reindex
from datetime import datetime
# from latex import Latex
import time

"""""""""""""""""""""""""""""""""""""""""""""""""""QUERY_ES"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Elastic_meth:

    @staticmethod
    def config_and_create_index(index_name) -> None:
        """
        creates an index with custom settings : tokenizer letter and filter lowercase
        :param index_name: the index name
        """
        es = Elasticsearch('http://localhost:9200')
        settings = {
            "analysis": {
                "analyzer": {
                    "custom_analyzer": {
                        "tokenizer": "letter",
                        "filter": ["lowercase"]
                    }
                }
            }
        }
        if not es.indices.exists(index=f"{index_name}"):
            es.indices.create(index=index_name, settings=settings)
        es.close()

    @staticmethod
    def check_index_exists(index):
        """
        checks if an index already exists or not
        :param index: name of the index
        :return: a boolean
        """
        es = Elasticsearch('http://localhost:9200')
        resp = es.indices.exists(index=f"{index}")
        es.close()
        return resp

    @staticmethod
    def refresh_index(index) -> None:
        """
        refreshes an index with its current documents
        :param index: name of the index
        """
        es = Elasticsearch('http://localhost:9200')
        es.indices.refresh(index=f"{index}")
        es.close()

    @staticmethod
    def reindex(source, destination):
        """
        1 - permits to add content of an existant index to another one
        2 - permits to copy an existant index into a new one
        3 - note that, point 2 is the only possibility to rename an index, by reindexation
        under a new name in a new index
        If the destination index doesn't exist this fonction will create it automatically, with its given name
        :param source: name of index to reindex
        :param destination: name of index receiving reindexation data - wether it exists or not
        """
        es = Elasticsearch('http://localhost:9200')
        reindex(client=es, source_index=source, target_index=destination, chunk_size=500)
        es.close()

    @staticmethod
    def create_document(index, endpoint, graph, values):
        """
        creates a document with all its fields implementing a json list of values
        :param index: name of the index
        :param endpoint: SPARQL uri endpoint
        :param graph : SPARQL uri endpoint graph
        :param values: json list of values
        :return: json document
        """
        document = {
            "_index": f"{index}",
            "timestamp": datetime.now(),
            "endpoint": f"{endpoint}",
            "graph": f"{graph}",
            "values": values
        }
        return document

    @staticmethod
    def count_document(index):
        """
        counts results number stored in the index
        :param index: name of the index
        :return: an int, number of results in the index
        """
        es = Elasticsearch('http://localhost:9200')
        resp = es.count(index=f"{index}")
        es.close()
        return resp

    @staticmethod
    def get_last_identifier(index):
        """
        gets the id of the last document indexed
        only useful when field _id is defined by user, beginning by 1 and incrementing by 1 during previous indexation
        :param index: name of the index
        :return: an int, the last identifier
        """
        last_tag = Elastic_meth.count_document(index)['count']
        return last_tag

    @staticmethod
    def store_elastic_search(index, endpoint, graph, results) -> None:
        """
        :param index: name of the index
        :param endpoint: SPARQL uri endpoint
        :param graph : SPARQL uri of the endpoint graph
        :param results: matrix of values - each element are a list values for one result
        :return:
        """
        es = Elasticsearch('http://localhost:9200')

        def bulking_indexing():
            def generate_data():
                for r in results:
                    yield {
                        "_index": f"{index}",
                        "timestamp": datetime.now(),
                        "endpoint": f"{endpoint}",
                        "graph": f"{graph}",
                        "values": r
                    }

            bulk(es, generate_data())
            time.sleep(1)

        start = time.time()
        if not Elastic_meth.check_index_exists(index):
            Elastic_meth.config_and_create_index(index)
            print("Index created")
        bulking_indexing()
        end = time.time()
        print(f"Storing {len(results)} results in ES took {end - start} secs - for {graph} ")
        Elastic_meth.refresh_index(index)
        es.close()

    @staticmethod
    def search(l_index, es_query) -> None:
        """
        searches matching results in index(es) from elastic search query
        :param l_index: list of index(es) targeted
        :param es_query: json elastic search query
        """
        es = Elasticsearch('http://localhost:9200')
        resp = es.search(index=l_index, query=es_query, size=50)
        print(f"Got {resp['hits']['total']['value']} Hits :")
        x = 1
        for hit in resp['hits']['hits']:
            print(f"res {x}", "%(endpoint)s %(values)s" % hit["_source"])
            x += 1
        es.close()


"""""""""""""""""""""""""""""""""""""""""""""""""""MAIN"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def main():
    all_index = ["class", "property", "label_class", "label_property", "subclass", "subproperty", "property_domain",
                 "property_range", "indi_range_property", "indi_domain_property", "entity_type"]

    """# displays all data
    query = {"match_all": {}}
    print("Displays results about all data ")
    Elastic_meth.search(all_index, query)

    # displays all classes
    query = {"match_all": {}}
    print("Displays results about classes")
    Elastic_meth.search("class", query)"""

    # I search for results about Aids
    query = {"match": {"values": "Aids"}}
    print("Displays results about AIDS : ")
    Elastic_meth.search("property", query)

    # I search for results about protein OR gene
    query = {"bool": {"should": [
        {"match": {"values": "protein"}},
        {"match": {"values": "gene"}}
    ]}}
    print("Displays results about protein OR gene ")
    Elastic_meth.search(all_index, query)

    # I search for results about protein AND gene
    query = {"bool": {"must": [
        {"match": {"values": ".*Protein.*"}},
        {"match": {"values": ".*GENE.*"}}
    ]}}
    print("Displays results about protein AND gene")
    Elastic_meth.search(all_index, query)

    # I search for cancer AND its treatments
    query = {"bool": {"must": [
        {"match": {"values": ".*Cancer.*"}},
        {"match": {"values": ".*Treatment.*"}}
    ]}}
    print("Displays results about cancer and its treatment")
    Elastic_meth.search(all_index, query)

    # I search for persons
    query = {"bool": {"must": [
        {"regexp": {"values": ".*foaf.*"}},
        {"regexp": {"values": ".*person.*"}},
        {"regexp": {"values": ".*people.*"}}
    ]}}
    print("Displays results about persons regexp")
    Elastic_meth.search(all_index, query)

    # I search for persons called Maria
    query = {"bool": {"must": [
        {"regexp": {"values": ".*foaf.*"}},
        {"match": {"values": "maria"}},
        {"bool": {"should": [
            {"regexp": {"values": ".*person.*"}},
            {"regexp": {"values": ".*people.*"}}
        ]}}
    ]}}
    print("Displays results about persons called Maria ")
    Elastic_meth.search(all_index, query)

    # I search for drugs in a specific endpoint
    query = {"bool": {"must": [
        {"match": {"endpoint": "https://bio2rdf.org/sparql"}},
        {"match": {"values": ".*drug.*"}}
    ]}}
    print("Displays results for drugs in bio2rdf")
    Elastic_meth.search(all_index, query)

    # I search for types
    query = {"regexp": {"values": ".*type.*"}}
    print("Displays results of types")
    Elastic_meth.search(all_index, query)

    # I search for a verb actions
    query = {"match": {"values": "healing"}}
    print("Displays results of a verb action")
    Elastic_meth.search(all_index, query)

    # I search for gene , protein and therapy
    query = {"bool": {"must": [
        {"regexp": {"values": ".*gene.*"}},
        {"regexp": {"values": ".*protein.*"}},
        {"match": {"values": "therapy"}},
    ]}}
    print("Displays results of gene, protein and therapy")
    Elastic_meth.search(all_index, query)

    # I search for hydratation, skin and cream
    query = {"bool": {"must": [
        {"regexp": {"values": ".*hydrat.*"}},
        {"regexp": {"values": ".*skin.*"}},
        {"match": {"values": "cream"}},
    ]}}
    print("Displays results of hydratation, skin and cream")
    Elastic_meth.search(all_index, query)

    # I search for hydratation, skin and cream
    query = {"bool": {"should": [
        {"regexp": {"values": ".*hydrat.*"}},
        {"regexp": {"values": ".*skin.*"}},
        {"match": {"values": "cream"}},
    ]}}
    print("Displays results of hydratation, skin and cream")
    Elastic_meth.search(all_index, query)

    """# I search for results about Aids - case doesn't count,  the exact keyword
    query = {"match": {"values": "Aids"}}
    print("Displays results about AIDS : ")
    Elastic_meth.search(all_index, query)


    # I search for results about Aids - case count, the string containing the key
    query = {"regexp": {"values": ".*Aids.*"}}
    print("Displays results about AIDS : ")
    Elastic_meth.search(all_index, query)

    # I search for results about Aids 
    query = {"regexp": {"values": ".*aids.*"}}
    print("Displays results about AIDS : ")
    Elastic_meth.search(all_index, query)

    # I search for results about Aids - the solution for regexp
    query = {"regexp": {"values": ".*(aids|Aids).*"}} 
    print("Displays results about AIDS : ")
    Elastic_meth.search(all_index, query)"""
# main()
