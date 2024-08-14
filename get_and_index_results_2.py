# -*- coding: utf-8 -*-

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

import json
import math
import time
import re
import warnings
from urllib import error
from SPARQLWrapper import SPARQLExceptions
from SPARQLWrapper import SPARQLWrapper, JSON

# internal modules
from latex import Latex
from elastic_meth_2 import Elastic_meth
from collections import Counter

"""""""""""""""""""""""""""""""""""""""""""""""""""CLASS_QUERY"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Query:
    """
    Object launched in a SPARQL query with editable parameters
    :ivar name: name of the SPARQL file.
    :type name: string
    :ivar uri: SPARQL endpoint's URI.
    :type uri: string
    :ivar graph: graph's URI targeted in the SPARQL endpoint.
    :type graph: string
    :ivar content: SPARQL query's instructions, except the limit and the offset.
    :type content: string
    :ivar iteration: number of query's iterations.
    :type iteration: int
    :ivar limit: parameter LIMIT in the SPARQL query.
    :type limit: int
    :ivar offset: parameter OFFSET in the SPARQL query.
    :type limit: int
    :ivar search_graph: True, if the query searches the graph's list of an SPARQL endpoint, else False
    :type search_graph : boolean
    """

    def __init__(self):
        """
            Initializes all the necessary attributes for a query object
        """
        self.name = ""
        self.uri = ""
        self.graph = ""
        self.content = ""
        self.iteration = 0
        self.limit = 0
        self.offset = 0
        self.search_graph = False

    def set_content(self, file):
        """
        Constructs the content of a query object from a SPARQL file
        :param file : file.sparql with a string of SPARQL instructions
        :type file : string
        """
        self.content = ""
        with open(file, 'r', encoding='utf-8') as fi:
            for line in fi:
                line = line.replace("\n", " ").strip("\'")
                self.content += line
        return self.content

    def set_limit(self, nb):
        """
        Defines the limit of a query object
        :param nb : the number of results wanted in a query
        :type nb : int
        """
        self.limit = nb
        self.content = self.content.replace(f"LIMIT 0", f"LIMIT {nb}")

    def set_offset(self, nb):
        """
        Defines the offset of a query object in attribute content
        :param nb : the step where the query begins to run for results
        :type nb : int
        """
        self.offset = nb
        self.content = self.content.replace(f"OFFSET 0", f"OFFSET {nb}")

    def next_offset(self, prec, succ):
        """
        Defines the next offset of a query object from its predecessor in attribute content
        :param prec : previous offset value
        :type prec : int
        :param succ : new offset value
        :type succ : int
        """
        self.offset = succ
        self.content = self.content.replace(f"OFFSET {prec}", f"OFFSET {succ}")

    def no_limit(self):
        """
        Defines no limit in a query object in attribute content
        value -1 is for display : indicates no limit
        """
        self.limit = -1
        self.content = self.content.replace(f"LIMIT 0", f"")

    def no_offset(self):
        """
        Defines no offset in  a query object in attribute content
        value -1 is for display : indicates no offset
        """
        self.offset = -1
        self.content = self.content.replace(f"OFFSET 0", f"")

    def header_graph(self, graph):
        """
        Defines the graph in the query object in attribute content
        :ivar graph: name of a graph that will be targeted
        """
        self.content = self.content.replace(f"<.>", f"<{graph}>")


"""""""""""""""""""""""""""""""""""""""""""""""LOG_FONCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"""
Global variables to fill the latex report all along the process
"""

report_query_graph = {}
report_each_query_section = {}
report_errors_section = {}

def generate_report(endpoint, more_res, l_graph, dis_res) -> None:
    """
    generate a latex document by default report.tex about all events by getting results from endpoint
    :param endpoint: SPARQL uri endpoint
    :param more_res: SPARQL query that got most results in searching graphs in an endpoint
    :param l_graph: list of graphs that have been found with the query
    :param dis_res: total amount of distinct results found on the endpoint
    """
    title = f"Report on querying Sparql endpoints"
    doc_name = input("nom du rapport .tex : ")  # ------------------------------check this out-------------------------
    Latex.create_log_document(doc_name, title)
    note = open(doc_name, "a", encoding="utf-8")

    # report - note about the endpoint requested
    note.write(Latex.part(Latex.format_special_char("Sparql Endpoint : " + endpoint)))
    # report - graphs researched
    note.write(Latex.section("Graphs research"))

    # report - all results about graphs search
    note.write(Latex.subsection("Queries for graphs and results"))
    if report_query_graph == {}:
        note.write(Latex.format_special_char(f"No exploitable results"))
    else:
        for graph, res in report_query_graph.items():
            note.write(Latex.format_special_char(f"graph {graph} returned : {res} results \n"))
            note.write(Latex.newline())
        if len(more_res) == 2:
            note.write(Latex.format_special_char(f"The {more_res[1]} returns more results ({more_res[0]})\n"))

    # report - list of graphs
    if len(more_res) == 2:
        note.write(Latex.subsection(Latex.format_special_char(f"Graphs from {more_res[1]} \n")))
        k = 1
        for graph in l_graph:
            note.write(Latex.format_special_char(f"graph {k} - {graph} \n"))
            note.write(Latex.newline())
            k += 1
    else:
        note.write(Latex.subsection(Latex.format_special_char(f"Graphs on {endpoint} \n")))
        note.write(Latex.format_special_char(f"No list of graphs"))
    note.write(Latex.next_page())
    note.write(Latex.section(Latex.format_special_char(f"Querying {endpoint}")))
    note.write(Latex.subsection("Results by query"))

    # report - note about each query and its results
    for key, value in report_each_query_section.items():
        note.write(Latex.format_special_char(f"Query {key} - total distinct results : {value}\n"))
        note.write(Latex.newline())
    note.write(Latex.newline())
    note.write(Latex.format_special_char(f"Total of unique results found {dis_res} on {endpoint} \n"))

    # report - all errors during the process
    note.write(Latex.subsection("Error Log"))
    if report_errors_section == {}:
        note.write("No errors encountered during the process\n")
        note.write(Latex.newline())
    else:
        note.write(Latex.itemize_begin())
        for graph, problem in report_errors_section.items():
            note.write(Latex.item())
            note.write(str(graph))
            note.write(str(problem))
        note.write(Latex.itemize_end())
    note.write(f"Number of errors : {len(report_errors_section)}" + "\n")

    # report - elastic search indexation - UNCOMPLETED
    note.write(Latex.section("Elastic search indexation"))
    note.close()


""""""""""""""""""""""""""""""""""""""""""""""QUERY_FONCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def setting_sparql(uri, time_out, returned_format, sparql_instructions):
    """ Set the SPARQL query through SPARQL Wrapper
    :param uri : SPARQL endpoint URI
    :type : string
    :param time_out : time given to reach out the server
    :type : int
    :param returned_format : the results format awaited
    :type : string
    :param sparql_instructions: the query's instructions sent to server
    :type : string
    :return a ready-to-use SparqlWrapper Object
    """
    sparql = SPARQLWrapper(uri)
    sparql.setTimeout(time_out)
    sparql.setReturnFormat(returned_format)
    sparql.setQuery(sparql_instructions)
    return sparql


def setting_query(file, endpoint, graph, limit, target_graph):
    """ Creates an object Query with all the attributes that need to be edited
    :param file : name of the sparql file
    :type : string
    :param endpoint : SPARQL endpoint URI
    :type : string
    :param graph : endpoint's graph URI
    :type : string
    :param limit : number of results wanted
    :type : int
    :param target_graph : True, if the query aims to search a graph's list, else False
    :type : boolean
    :return a ready-to-use Query Object
    """
    q = Query()
    q.name = file
    q.uri = endpoint
    q.graph = graph
    q.set_content(file)
    q.header_graph(graph)
    q.set_limit(limit)
    q.search_graph = target_graph
    return q


# launch a sparql query on an endpoint
def launch_query(q, k):
    """ Launches a SPARQL query
    :param q: a Query Object
    :param k: graph index targeted in the query
    :return: results, number of results, and if necessary the name of the query
    """

    try:
        q.no_limit(), q.no_offset()
        sparql = setting_sparql(q.uri, 3600, JSON, q.content)

        # sending and getting converted results in json - counting raw results founded
        res = sparql.queryAndConvert()
        nb_res = count_results(res)

        # activate the filter to catch a warning as an exception
        warnings.filterwarnings("error")

        # displaying raw results of any query (of graphs, of json results)
        if q.search_graph is False:
            pass
            # print(f"endpoint : {q.uri} requete : {q.name} graph {k} {q.graph} raw results : {nb_res}")
        else:
            print(f"endpoint : {q.uri} requete : {q.name} raw results : {nb_res}")
        return nb_res, q.name, res

    # all errors catched that can occur in the process of getting json results
    # - Runtime warnings from (Sparql) Wrapper file
    # - HTTP Errors
    # - Specific Exceptions from SPARQL (Wrapper) Exceptions file
    # - other miscellaneous exceptions
    # returns empty and null values
    except RuntimeWarning as run:
        report_errors_section["RuntimeWarning : "] = Latex.format_special_char(str(run))
        return 0, "", {}
    except error.HTTPError as ehttp:
        print(ehttp)
        if q.search_graph is False:
            key = Latex.format_special_char(f"Error on {q.name} graph {k} {q.graph} : ")
        else:
            key = Latex.format_special_char(f"Error on  {q.name} : ")
        report_errors_section[key] = Latex.format_special_char(str(ehttp))
        return 0, "", {}
    except Exception as e:
        if isinstance(e, SPARQLExceptions.EndPointInternalError) or \
                isinstance(e, SPARQLExceptions.EndPointNotFound) or \
                isinstance(e, SPARQLExceptions.URITooLong) or \
                isinstance(e, SPARQLExceptions.QueryBadFormed) or \
                isinstance(e, SPARQLExceptions.Unauthorized):
            print(e.args)
            errors = Latex.clean_error_wrapper(e.args[0])
            if q.search_graph is False:
                key = Latex.format_special_char(f"Error on graph {q.graph} {q.name} : ")
            else:
                key = Latex.format_special_char(f"Error on  {q.name} : ")
            value = Latex.format_special_char(f"{errors[0]} \n {errors[1]}")
            report_errors_section[key] = value
            return 0, "", {}
        else:
            print(e)
            report_errors_section[e] = str(e.args)
            return 0, "", {}


""""""""""""""""""""""""""""""""""""""""""""""RESULTS_FONCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def display_results(res) -> None:
    """
    displays results of a sparql query, either a json dict or json list
    :param res: a json result
    """
    i = 0
    if isinstance(res, dict):
        for r in res["results"]["bindings"]:
            print(f"res {i + 1}", r)
            i += 1
    elif isinstance(res, list):
        for elem in res:
            print(f"res {i + 1}", elem)
            i += 1


def count_results(res):
    """
    counts results of a sparql query, either a json dict or json list
    :param res: a json result
    :return: number of json results
    """
    i = 0
    if isinstance(res, dict):
        for _ in res["results"]["bindings"]:
            i += 1
    elif isinstance(res, list):
        for _ in res:
            i += 1
    return i


""""""""""""""""""""""""""""""""""""""""""""""GRAPH_FONCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def extract_graph(dic, endp):
    """
    displays the graph query with most results on an SPARQL endpoint
    extracts a graph list from the SPARQL endpoint
    :param dic: dictionary of graph sets
    :param endp: SPARQL endpoint URI
    :return: a list of graphs names for the query with the most results, and the query itself
    """

    def graphset_with_more_results(d):
        """
        determines the graph set with more results
        a graph set is a tuple returned by a sparql query (number of results, query name, json result)
        :param d: a graph sets dictionary
        :return: a tuple of (the highest number of results, its query name, its json results)
        """
        maxi = 0
        for k in d:
            if k >= maxi:
                maxi = k
        return maxi, d[maxi][0], d[maxi][1]

    def listing_graph(res):
        """
        creates a graph list from a json result, from a graph query sent to SPARQL endpoint
        :param res: json result
        :return: a list of graphs names
        """
        l_graph = []
        for r in res["results"]["bindings"]:
            for k, val in r.items():
                for s_key, s_val in val.items():
                    graph = s_val
                    if graph != 'uri':
                        graph = graph.strip(',')
                        l_graph.append(graph)
        return l_graph

    try:
        max_res = graphset_with_more_results(dic)
        if max_res != ((),):
            print(f"endpoint {endp} : more results ({max_res[0]}) for {max_res[1]}\n")

            # report - store the query with a maximum results
            more_result_query = max_res[0], max_res[1]

            return listing_graph(max_res[2]), more_result_query
        else:
            print("no corresponding query to get a graphs list")
    except Exception as e:
        key = "Error while getting graphs list or query with most results \n"
        report_errors_section[key] = f" {e} as a result"
        print("An error has occurred to get graphs list and/or query with most results")


""""""""""""""""""""""""""""""""""""""""""""""INDEXATION_FUNCTIONS"""""""""""""""""""""""""""""""""""""""""""""""""""""


def extracting_values_from_result(res):
    """
    extracts values (uri) from a json result and puts them in list
    :param res: json result
    :return: a list of the json result values
    """
    excluded_values = {"type", "xml:lang", "graph"}
    array = []
    for key, val in res.items():
        for under_k, under_val in val.items():
            if under_k not in excluded_values:
                array.append(under_val)
    return array


def indexing_elastic_search(res_by_query, endp, div_values) -> None:
    """
    Launches the indexation and check if partitions are needed according to values size
    :param res_by_query: dictionnary, where key are query name and values a dictionnay of graphs and their values
    :param endp: string, SPARQL uri endpoint
    :param div_values: boolean, useful to index divided values parts from the same query under one query_name,
    that will be also the index name
    """
    total_values, all_values = 0, 0
    for query, graph in res_by_query.items():
        query = query.replace(".sparql", "").replace("query/", "")
        for graph, values in graph.items():
            total_values += len(values)
            Elastic_meth.store_elastic_search(query, endp, graph, values)
        print(f"Total values for query '{query}' : {total_values}")
        all_values += total_values
        total_values = 0
    print(f"Total values stored {all_values}")




"""""""""""""""""""""""""""""""""""""""""""""""""""MAIN"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def main():
    list_endpoint = ["https://data.open.ac.uk/query", "https://sparql.nextprot.org/", "http://rdf.disgenet.org/sparql/",
                     "https://genome.microbedb.jp/sparql", "https://id.nlm.nih.gov/mesh/sparql",
                     "https://sparql.proconsortium.org/virtuoso/sparql", "https://sparql.rhea-db.org/sparql",
                     "http://patho.phenomebrowser.net/sparql/", "https://bio2rdf.org/sparql"]

    list_query_graph = ["query/all_graphs_included.sparql", "query/graphs_with_a_triple_min.sparql",
                        "query/graphs_with_rdf_type.sparql"]

    list_query_endpoint = ["query/class.sparql", "query/property.sparql", "query/label_class.sparql",
                           "query/label_property.sparql", "query/subclass.sparql", "query/subproperty.sparql",
                           "query/property_domain.sparql", "query/property_range.sparql",
                           "query/indi_range_property.sparql", "query/indi_domain_property.sparql",
                           "query/entity_type.sparql"]

    # endp = an endpoint to explore - choose its number in list and replace it in list_endpoint[number]
    endp = list_endpoint[0]
    distinct_res = set()
    res_by_graph, compared_query, res_by_query = {}, {}, {}
    nb_raw_res, all_raw_res = 0, 0
    divided_values = False

    # searching graphs inside endpoints --------------------------------------------------------------------------------
    for i in range(len(list_query_graph)):
        nb, q, res = launch_query(setting_query(list_query_graph[i], endp, None, 100, True), None)
        if res != {}:
            compared_query[nb] = q, res
            # report - store the query and its results
            report_query_graph[q] = nb

    # getting graph query with most results and its list of graphs
    list_graph, more_result_query = extract_graph(compared_query, endp)

    # querying endpoint -----------------------------------------------------------------------------------------------
    start = time.time()
    for j in range(10, 11):
        # querying graphs
        for k in range(len(list_graph)):
            nb, q, res = launch_query(setting_query(list_query_endpoint[j], endp, list_graph[k], 0, False), k + 1)
            if res != {} and nb != 0:
                # constructing a sef of distinct string results from the ongoing graph
                for r in res["results"]["bindings"]:
                    nb_raw_res += 1
                    # new json object cleaned with graph name and its values
                    values = extracting_values_from_result(r)
                    try:
                        if list_graph[k] not in res_by_graph :
                            res_by_graph[list_graph[k]] = values
                        else:
                            res_by_graph[list_graph[k]] += values
                    except Exception as e:
                        print("error")
                        print(e)

            # storing results by graphs, by query
            if list_query_endpoint[j] not in res_by_query:
                res_by_query[list_query_endpoint[j]] = res_by_graph
            else:
                res_by_query[list_query_endpoint[j]] |= res_by_graph
            res_by_graph = {}


        all_raw_res += nb_raw_res
        # displaying results by query
        print(f"Total of raw results found {nb_raw_res} for {list_query_endpoint[j]}")
        nb_raw_res = 0

        # report - store total results and distinct by query
        report_each_query_section[list_query_endpoint[j]] = nb_raw_res

    # display all unique results found on the SPARQL endpoint
    print(f"Total of raw results found {all_raw_res} on endpoint {endp}")
    end = time.time()
    duration = end - start
    print(f"Getting results for {endp} took {math.floor(duration / 60)} min (exactly {duration} sec)")

    # generating the latex report - name of report will be asked
    # generate_report(endp, more_result_query, list_graph, all_raw_res)

    # storing result in elastic search --------------------------------------------------------------------------------
    begin = time.time()
    indexing_elastic_search(res_by_query, endp, divided_values)
    finish = time.time()
    print(f"Indexation for {endp} took {math.floor((finish - begin) / 60)} min (exactly {finish - begin} sec)")
main()
