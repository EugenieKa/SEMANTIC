"""

  Author:
  * Eugenie Karadjoff
  <eugenie.karadjoff@gmail.com> -- it will change in the near future, but works properly right now

  Organization and its members involved:
  LORIA - Laboratoire LOrrain de Recherche en Informatique et ses Applications (France) -- Team K :
  * Mathieu d'Aquin <mathieu.daquin@loria.fr>
  * Emmanuel Nauer <emmanuel.Nauer@loria.fr>

  :purpose:
  * SEMANTIC project is pythom program that allows its users to make research on semantic web.
  It connects to any SPARQL endpoints, then extracts, sort and compile data in nosql database, and open
  possibility to launch researches upon them
  for every .py files, please refers to readme file because they are 3 versions of it for
  each function ( extract, search)

  lass Latex is a bunch of static methods for programs when they want to produce a plain- text document

  :license: without license, the default copyright laws apply.

  last update : July 2022

"""


class Latex:

    @staticmethod
    def preambule():
        """
        structures the parameters of the latex document
        :return: string of parameters
        """
        p = r"\documentclass[a4paper,12pt]{article}" + "\n"
        p += r"\usepackage[utf8]{inputenc}" + "\n"
        p += r"\usepackage[T1]{fontenc}" + "\n"
        p += r"\usepackage{parskip}" + "\n\n"
        return p

    @staticmethod
    def header(t):
        """
        structures the header of latex document : title, author and date
        :return: string of structure
        """
        p = r"\title" + "{" + f"{t}" + "}\n"
        p += r"\date{\today}" + "\n\n"
        return p

    @staticmethod
    def open_content():
        """
        :return: code of beginning of a latex document
        """
        return r"\begin{document}" + "\n"

    @staticmethod
    def close_content():
        """
        :return: code of ending of a latex document
        """
        return r"\end{document}" + "\n"

    @staticmethod
    def part(title_part):
        """
        :return: code of a latex document part
        """
        return r"\part{" + f"{title_part}" + "}\n"

    @staticmethod
    def section(title_section):
        """
        :return: code of a latex document section
        """
        return r"\section{" + f"{title_section}" + "}\n"

    @staticmethod
    def subsection(title_subsection):
        """
        :return: code of a latex document section
        """
        return r"\subsection{" + f"{title_subsection}" + "}\n"

    @staticmethod
    def newline():
        """
        :return: code of a latex newline
        """
        return r"\newline" + "\n"

    @staticmethod
    def bold(text):
        """
        :return: code of a text put in bold
        """
        return r"\textbf{" + f"{text}" + "}"

    @staticmethod
    def next_page():
        """
        :return: code of a page break
        """
        return r"\newpage" + "\n"

    @staticmethod
    def itemize_begin():
        """
        :return: code of a bullet list beginning
        """
        return r"\begin{itemize}" + "\n"

    @staticmethod
    def itemize_end():
        """
        :return: code of a bullet list ending
        """
        return r"\end{itemize}" + "\n"

    @staticmethod
    def item():
        """
        :return: code of an item in a bullet list
        """
        return r"\item "

    @staticmethod
    def format_special_char(text):
        """
        formats any string output with special chars into a compatible one to incorporate in a latex document
        :return: string formatted
        """
        text = text.replace(r"\n", " ")
        special_char = ["&", "%", "$", "#", "_"]
        for char in special_char:
            if char in text:
                new_char = r"\ ".strip() + f"{char}"
                text = text.replace(char, new_char)
        return text

    @staticmethod
    def create_log_document(file, t):
        """
        creates the Latex document and initialize it
        """
        with open(file, "w", encoding="utf-8") as log:
            log.write(Latex.preambule())
            log.write(Latex.open_content())
            log.write(Latex.header(t))

    @staticmethod
    def clean_error_wrapper(error_response):
        """
        shortens HTTP error code 500 output for latex document
        :return: list of errors indications
        """
        part = ""
        list_error = []
        for c in error_response:
            if c != ".":
                part += c
            else:
                part.split()
                list_error.append(part)
                part = ""
        del list_error[2:]
        return list_error
