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
  for every .py files, please refers to readme file because they are 3 versions

  :license: without license, the default copyright laws apply.

  last update : July 2022

"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.helpers import reindex
from datetime import datetime
from latex import Latex
import time


"""""""""""""""""""""""""""""""""""""""""""""""""""QUERY_ES"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Elastic_meth:

    @staticmethod
    def config_and_create_index(index_name) -> None:
        """
        creates an index with custom settings : tokenizer letter and filter lowercase
        :param index_name: the index name
        :type index_name : str
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
        es.indices.create(index=index_name, settings=settings)

        # report - creation of index
        note = open("report.tex", "a", encoding="utf-8")
        note.write(Latex.format_special_char(f"Index '{index_name}' has been successfully created"))
        note.write(Latex.newline())
        note.close()

        es.close()

    @staticmethod
    def check_index_exists(index):
        """
        checks if an index already exists or not
        :param index: name of the index
        :type index: str
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
        :type index: str
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
        :type source: str
        :param destination: name of index receiving reindexation data - wether it exists or not
        :type destination: str
        """
        es = Elasticsearch('http://localhost:9200')
        reindex(client=es, source_index=source, target_index=destination, chunk_size=500)

        # report - about reindexation
        note = open("report.tex", "a", encoding="utf-8")
        note.write(Latex.section("Reindexation"))
        note.write(f" root index {source}, destination index {destination}\n")
        note.write(Latex.newline())
        note.close()
        es.close()

    @staticmethod
    def create_document(index, endpoint, values):
        """
        creates a document with all its fields implementing a json list of values
        :param index: name of the index
        :type index: str
        :param endpoint: SPARQL uri endpoint
        :type endpoint: str
        :param values: json values and types
        :type values: dict
        :return: json document
        """
        document = {
            "_index": f"{index}",
            "timestamp": datetime.now(),
            "endpoint": f"{endpoint}",
            "values": values
        }
        return document

    @staticmethod
    def count_document(index):
        """
        counts results number stored in the index
        :param index: name of the index
        :type index: str
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
        :type index: str
        :return: an int, the last identifier
        """
        last_tag = Elastic_meth.count_document(index)['count']
        return last_tag

    @staticmethod
    def store_elastic_search(index, endpoint, results) -> None:
        """
        :param index: name of the index
        :type index: str
        :param endpoint: SPARQL uri endpoint
        :type endpoint: str
        :param results: list of json dictionary of values and types
        :type endpoint: list

        """
        es = Elasticsearch('http://localhost:9200')

        def bulking_indexing():
            def generate_data():
                for r in results:
                    yield {
                        "_index": f"{index}",
                        "timestamp": datetime.now(),
                        "endpoint": f"{endpoint}",
                        "values": r
                    }

            bulk(es, generate_data())

        start = time.time()
        if not Elastic_meth.check_index_exists(index):
            Elastic_meth.config_and_create_index(index)
            print("Index created")
        else:
            note = open("report.tex", "a", encoding="utf-8")
            note.write(Latex.format_special_char(f"Index '{index}' already exits and will be completed"))
            note.write(Latex.newline())
            note.close()
        bulking_indexing()
        end = time.time()
        print(f"Storing {len(results)} results in index {index} took {end - start} secs")

        # report - bulk indexation
        note = open("report.tex", "a", encoding="utf-8")
        note.write(Latex.format_special_char(f"Storing {len(results)} results in index '{index}' "
                                             f"took {round(end - start, 3)} secs \n"))
        note.write(Latex.newline())
        note.write(Latex.newline())
        note.close()

        Elastic_meth.refresh_index(index)
        es.close()

    @staticmethod
    def search(l_index, es_query) -> None:
        """
        searches matching results in index(es) from elastic search query
        :param l_index: index(es) targeted
        :type l_index: list
        :param es_query: json elastic search query
        :type es_query: dict
        """
        es = Elasticsearch('http://localhost:9200')
        resp = es.search(index=l_index, query=es_query, size=50)
        print(f"Got {resp['hits']['total']['value']} Hits :")
        x = 1
        for hit in resp['hits']['hits']:
            print(hit)
            print(f"res {x}"  "%(endpoint)s %(values)s" % hit["_source"])
            x += 1
        es.close()

"""""""""""""""""""""""""""""""""""""""""""""""""""MAIN"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def main():
    all_index = ["class", "property", "label_class", "label_property", "subclass", "subproperty", "property_domain",
                 "property_range", "indi_range_property", "indi_domain_property", "entity_type"]


