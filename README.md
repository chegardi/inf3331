# LaTeX preprocessor and compiler
This is the result from a mandatory assignment in INF3331 at University of Oslo Fall2014.

The reason for creating the preprocessor was to increase functionality of LaTeX to comprehend reports about works in programming. As every line the preprocessor handles starts with '%', a regular LaTeX compiler will still manage to handle docuemts written with the preprocess executions, as they are treated as comments in all other cases other than when ran through prepro.py.
The compiler is actually just a method of creating the .pdf document from any LaTeX source code (that preferably have been preprocessed, but it is not necessary). The main feature of the compiler is to reduce the amount of output created by pdflatex to the only information desirable - successful or not.

# Usage

## Prepro

``` terminal
usage: prepro.py [-h] [-o OUTFILE] [-f] [-v] infile

Program preprocesses a latex-file ('infile') and produces a new latex-file
('outfile') with additional functionality

positional arguments:
  infile                Name of the latex-file you want preprocessed

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        Name of the new file (cannot be equal to infile)
  -f, --fancy_verbatim  produces more fancy verbatim
  -v, --verbosity       increase output verbosity
```

## Compile

``` terminal
usage: compile.py [-h] [-v] [-i] [-p PREPROCESS] compilefile

A latex compiler shortening terminal output to more meaningful printing, and
added functionality

positional arguments:
  compilefile           The latex-file to be compiled

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbosity       Be loud about what to do
  -i, --interaction     Sets pdflatex to interaction=nonstopmode to True
  -p PREPROCESS, --preprocess PREPROCESS
                        Will preprocess using python prepro.py with
                        compilefile as 'outfile'-name, and -f enabled. See
                        prepro.py -h for details
```
