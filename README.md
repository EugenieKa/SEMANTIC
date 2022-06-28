***

# INDEX

***

**IDE and hardware**

**Libraries and modules**

**Program structure**

- Program files

- Program versions
- Interdependent files and execution
- Others files and directories

**SPARQL queries and getting json result**

- Class Query
- Log functions (Latex report)
- Query functions
- Results functions
- Graph functions

**ES Indexation**

- Extracting and indexing functions
- How partitioning works
- About Connection Time Out - err Raise None
- Settings and mappings

**Main in get_index_results_{x}**

-----------------------------------------------------------------------------------------

"ES" will be used in the document for terms "elastic search"

********************************************************************************
# IDE and hardware

********************************************************************************

Pycharm Community Edition 3.3
Python 3.10.4
ES client : https://elasticsearch-py.readthedocs.io/en/v8.2.3/
SparqlWrapper interface : https://sparqlwrapper.readthedocs.io/en/latest/main.html
Elastic search 8.2.0
Kibana 8.2.2

OS : Windows 10 Professional
Processor :Intel(R) Core(TM) i5-2500 CPU @ 3.30GHz   3.30 GHz
RAM : 10 GB


********************************************************************************
# Libraries and modules

********************************************************************************
All libraries/ modules are in the Pycharm file tree under:
> External folders > Python 3.9 > site-packages

The most important libraries and built-in modules explicitly used in the
program (and not implicitly by others API client or libraries)

- SPARQLWrapper interface to send queries to SPARQL endpoints and get results
- elasticsearch, elastic_transport, elasticsearch.helpers
- urllib3
- json
- math
- time
- re
- warnings
- datetime

Custom modules
- latex
- elastic_meth_{x}

Libraries are must be put here :

Windows path: C:\Users\Username\PycharmProjects\SPARQUUS\venv\Lib\site-packages

********************************************************************************
# Program structure

********************************************************************************

The program consists in two parts. Each one can be executed separately :
get_index_results{x}.py and elastic_meth{x}.py

This structure has been implemented in order to separate getting/indexation results from elastic search researches in database

Knowing that getting/indexation is long, it aims to get result in an reasonable time for ES queries
(also because it's nonsense to get and index sparql results each time before making any ES research)

--------------------------------------------------------------------------------
## Program files

***

get_index_results_{x}.py contains :
--class Query
--methods applicable to SPARQL query and results
--report generation function (see 4.2 log function section)
--program to get results with SparqlWrapper
--the program to launch indexation in ES database

elastic_meth_{x}.py contains :
--class Elastic_meth with ES methods, including indexation methods
--the program to launch ES queries

Note : get_index_result{x} is calling static methods from elastic_meth{x} but it performs  getting and formatting sparql results, partitioning and ES indexation in its main().



--------------------------------------------------------------------------------
Program versions
--------------------------------------------------------------------------------

***

There are 3 versions of the program, see the difference below 
The last version used and updated is get_index_result_1

get_index_result_1 :
- get distinct results

- index a json array of 'value' fields
  ES index ex:

  ```
   { values : [ "http://value", "digesnetvalue38"]}
  ```

  

get_index_result_2 :
- get raw results

- index graphs and a json array of 'value' fields
  --> UNFINISHED :
  ----problem with the entity_type results which are indexed twice
  ----the report generation is not updated and stops after getting sparql results step
  ES index ex: 

  ```
  {graph : "http://oof_graph45", values : [ "http://value", "Role Status"]}
  ```

  

get_index_results_3 :
- get distinct results

- index a json object with types of values (in sparql query) and 'value' fields
  ES index ex: 

  ```
  { values : { "property" : "http://value1", "range" : "http://value2"}}
  ```

  

--------------------------------------------------------------------------------
## Interdependent files and execution

***

- get_index_result_1 and elastic_meth_1 work together
elastic_meth_1 is imported in get_index_result_1 by default
-> OPERATIONAL
- get_index_result_2 and elastic_meth_2 work together
elastic_meth_2 is imported in get_index_result_2 by default
!!!!----> UNFINISHED - will not work properly
- get_index_results_3 and elastic_meth_3 work together
  elastic_meth_3 is imported in get_index_result_3 by default
  -> OPERATIONAL

To execute get_index_results{x}, main() function of elastic_meth_{x}.py must be a comment

To execute elastic_meth{x}, you have to uncomment its main() function




--------------------------------------------------------------------------------
Others files and directories
--------------------------------------------------------------------------------

***

### latex.py 

is class Latex, a class of all static methods to write into a
latex document, anywhere in the program. Just need an import :

>> ex : from latex import Latex

Latex.py works for all program versions

endpoint.txt is document that contains all medical endpoints tested :
- ones that work well,
- those that didn't work
- the ones where it took eternity to see a result

### directory query 

contains all files .sparql which are SPARQL queries (to modify them, see section 4.3 Query functions)

### directory reports 

contains all reports after indexation with get_index_result_1

### directory libraries

contains client, libraries and modules of the project



********************************************************************************
# SPARQL queries and getting json result

********************************************************************************
--------------------------------------------------------------------------------
## CLASS QUERY

***

A class to create a Query object containing methods to parameter the query
A Query object contains a sparql query in his attribute 'content'

To modify content, write on the sparql file directly
To modify others parameters, please refers to the planned methods in the Query class (all are documented in the file)

On sparl query file, it is recommended to not change or erase 'graph <.>' : the whole program is searching results based on this pattern



--------------------------------------------------------------------------------
LOG FUNCTIONS (Latex report)
--------------------------------------------------------------------------------

***

Here are basically variables used for the report which are all dictionaries to store data to report

The report is always written in file "report.tex"
Warning : each time your launch the program, it will overwritten "report.tex"

The file is open and close several times at some progression steps, both in get_index_result{x} and in elastic_meth{x}
It seems inconvenient to insert an input asking user many times the same name of file during the process (and pausing it in addition)

Simply rename to save it, after a launch on an endpoint once it is produced.

### Tips about latex document

1 - As data in this program are full of special characters, to avoid incompatibility with their different effects in python code and in latex code:
Always use the method Latex.format_special_char() function to introduce values that may have special character(s) in it.

2 - The compilation of "report.tex" with - pdflatex report.tex - will work well
If :

- no Latex.newline() is put before and after titles like Latex.section() or
Latex.subsection()
- no Latex.newline() is put in a bullet list (itemize)
- no Latex.newline() is put when the next line is not a basic string
- no Latex.newline() is put before the end of document

3 - The latex document is explicitly close with Latex.close_content()

To execute a Latex function in the document, it is necessary to open "report.tex" as a variable and then to use the variable to perform the writing
ex :

```
pen = open("report.tex", "a", encoding="utf-8")
pen.write(Latex.section(Latex.format_special_char("Querying endpoint
													https://bio2rdf.org/sparql")
pen.write(Latex.format_special_char("entity_type_44#trick.sparql"))
pen.write(Latex.newline())
pen.write("Hello World")
pen.write(Latex.close_content()) # close the document latex structure
pen.close() # close the document in python program
```

Note : the "a" parameter at opening is to write additional content, and not overwrite it (like "w" does)



--------------------------------------------------------------------------------
QUERY FUNCTIONS
--------------------------------------------------------------------------------

***

- Function setting_query() creates a Query object and configures it to prepare/modify the file .sparql to be sent, with wanted paramaters
- Function setting_sparql() creates a SparqlWrapper object and configure it through SparqlWrapper methods before sending it to the server

- Function launch_query() basically send the sparql query and convert its response into json results


In this function, Query object is the sparql query plus others attributes that is set and short after the SparqlWrapper object use some of Query object attributes and its own parameters to send the fitting sparql query for the server

Note that, this functions contains a big part of exceptions and errors management

### Exceptions

Exceptions are treated separately in order to format them properly then include them in the report.tex

There were particular ways to store data about exceptions

For e.g, some were not considered as exceptions like warnings, SPARQLExceptions were forbidden to be stored but all have been found and stored thanks to a very prolix code

Displaying information while getting results for a sparql query on endpoint is deactivated (uncommented) because of the long length of json results
But is activated to find graphs in endpoint



--------------------------------------------------------------------------------
RESULTS FUNCTIONS
--------------------------------------------------------------------------------

***

display_results() : displays results in the terminal (useful to observe json result structure and syntax)

It displays dictionary json results only
It can display any list on the program (optionnal)

count_results() : counts number of results in json results dictionary



--------------------------------------------------------------------------------
GRAPH FUNCTIONS
--------------------------------------------------------------------------------

***

extract_graph() :  aims to extract the list of graphs from and endpoint.
This function is composed of two others functions :

Graphset notion : a graph set is a tuple containing results number, query name, and its json results, in this order
It is produced when a sparql graph query search graphs in an endpoint

graphset_with_more_results() : aims to determine within the three sparql query of getting graphs which one got the most result

listing_graph(): creates list of graphs from the sparql graph query that got most results



********************************************************************************
# ES Indexation

********************************************************************************
--------------------------------------------------------------------------------
Extracting and indexing functions
--------------------------------------------------------------------------------

***

extracting_values_from_result():

In get_index_result_1.py and in get_index_result_2.py : extracts values from a json result and puts them in a list

In get_index_result_3.py : extracts fields 'value' and its type (ex: class, property,
individual, label and so on) from a json result and create a new compact json result

indexing_elastic_search(): launches indexation and check if partitions are needed according to values size

indexing_by_partition(): executes the partitioning selected by the function beforehand and proceed to indexation

Note that, these partitions are subpartitions split in 3 groups
_under 200 000, indexation with no partition
_between 200 000 and 1 500 000
_superior to 1 500 00



--------------------------------------------------------------------------------
How partitioning works
--------------------------------------------------------------------------------

***

There are two levels of partitions.

The first partition execute itself in the main program. It splits results of a big query into several independent queries with the same name plus a number.
They are treated for indexation as different queries : it permits to unload data sending and avoid Connection Time Out : raise Err None

The superior limit that ES can handle for one query is around 2 000 000
Partitions are slices of the big results counting 2 000 000 results or more

At the last final point of indexation, the  independent split queries loose their number to be the indexed under the original name of query, which is also name of index.

Volume under 2 000 000, are either index directly, or concerned by subpartitions process above mentioned

As seen in the previous section, there are subpartitions. It permits for average volumes to be index by subpartitions and for the little to be indexed directly.

Subpartition doesn't create independent queries from the original one. The query results are slices and send for indexation part by part. It aims to keep a good pace for indexation without Connection Time Out that can occurs sometimes.



--------------------------------------------------------------------------------
About Connection Time Out - err Raise None
--------------------------------------------------------------------------------

***

With all the dispositions made, it happens rarely. If it happens, just relaunch the program after a few seconds or minutes. It can be useful too to shutdown and restart ES,
(or simply work with a more powerful PC)



--------------------------------------------------------------------------------
Settings and mappings
--------------------------------------------------------------------------------

***

Settings have been customized to ease ES searches with tokenizer letter and filter lowercase
Mappings have not been modified and is set by default

If there is a need of accessing independently each value of the values field for any reason, it exists one solution among others that consists on customizing mappings : the type of values, "text", must be turn into "nested"



********************************************************************************
# Main

********************************************************************************

It contains list of endpoints interrogated
It contains list of graph queries
It contains list of sparql queries

The program gives results for the selected endpoint by its number. There is no loop to querying all endpoints and indexing their results in one shot due to the fact that one crash is killing all the previous efforts, sometimes at the very end

Note that partitioning in partition (not subpatitioning) is executed in it.