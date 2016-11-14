#!/usr/bin/env python
import re # for handling regex commands
import subprocess
import argparse
import os
import textwrap

packages = "%s" % ("\\usepackage{fancyvrb}\n"\
    +"\\usepackage{framed}\n"\
    +"\\usepackage{color}\n"\
    +"\\providecommand{\\shadedwbar}{}\n"\
    +"\\definecolor{shadecolor}{rgb}{0.87843, 0.95686, 1.0}\n"\
    +"\\renewenvironment{shadedwbar}{\n"\
    +"\\def\FrameCommand{\\color[rgb]{0.7,     0.95686, 1}\\vrule width 1mm\\normalcolor\\colorbox{shadecolor}}\\FrameRule0.6pt\n"\
    +"\\MakeFramed {\\advance\\hsize-2mm\\FrameRestore}\\vskip3mm}{\\vskip0mm\\endMakeFramed}\n"\
    +"\\providecommand{\\shadedquoteBlueBar}{}\n"\
    +"\\renewenvironment{shadedquoteBlueBar}[1][]{\n"\
    +"\\bgroup\\rmfamily\n"\
    +"\\fboxsep=0mm\\relax\n"\
    +"\\begin{shadedwbar}\n"\
    +"\\list{}{\\parsep=-2mm\\parskip=0mm\\topsep=0pt\\leftmargin=2mm\n"\
    +"\\rightmargin=2\\leftmargin\\leftmargin=4pt\\relax}\n"\
    +"\\item\\relax}\n"\
    +"{\\endlist\\end{shadedwbar}\\egroup}\n")

def begin_shaded_verbatim(fancy):
    """
Prints correct begin{Verbatim} to file

Parameters
----------
fancy : boolean
    Produces fancy verbatim if true

Returns
-------
Start of verbatim : string
    """
    if fancy:
        return "\\begin{shadedquoteBlueBar}\n" \
                        + "\\fontsize{9pt}{9pt}\n" \
                        + "\\begin{Verbatim}\n"
    else:
        return "\\begin{verbatim}\n"

def end_shaded_verbatim(fancy):
    """
Prints correct end{verbatim} to file

Parameters
----------
fancy : boolean
    Produces fancy verbatim if true

Returns
-------
End of Verbatim : string
    """
    if fancy:
        return "\\end{Verbatim}\n" \
                        + "\\end{shadedquoteBlueBar}\n" \
                        + "\\noindent\n"
    else:
        return "\\end{verbatim}\n\\noindent\n"

def begin_execution_verbatim(fancy):
    """
Prints correct begin{Verbatim} to file

Parameters
----------
fancy : boolean
    Produces fancy verbatim if true

Returns
-------
Start of execution environment : string
    """
    if fancy:
        return "\\begin{Verbatim}[numbers=none,frame=lines,label=\\fbox{{Terminal}},fontsize=\\fontsize{9pt}{9pt},labelposition=topline,framesep=2.5mm,framerule=0.7pt]\n"
    else:
        return "\\begin{verbatim}\n"

def end_execution_verbatim(fancy):
    """
Prints correct end{Verbatim} to file

Parameters
----------
fancy : boolean
    Produces fancy verbatim if true

Returns
-------
End of execution-environment : string

Example
-------
>>> end_execution_verbatim(False) 
'\\\\end{verbatim}\\n\\\\noindent\\n'
    """
    if fancy:
        return "\\end{Verbatim}\n" \
+ "\\noindent\n"
    else:
        return "\\end{verbatim}\n\\noindent\n"

def import_script(in_file, in_line, fancy, verbose):
    """
Handles the command '%@import [filename "regex"]',
which imports code from current or 'filename' document
according to regex-expression.
Or '%@exec' which prints out execution-style of following code.

Parameters
----------
in_file : file
    The latex document currently being read from

in_line : string
    The current line being processed

fancy : boolean
    Use fancy verbatim

verbose : boolean
    Be loud about what to do

Returns
-------
script : string
    """
    content = ""
    # %@import file regex found
    if len(in_line.split()) > 1:
        args = in_line.split()[1:]
        script_filename = args[0]
        regex = in_line.split("\"")[-2]
        if verbose:
            print "Opening file '%s' to import script matching pattern '%s'" % (script_filename, regex)
        # Open script file
        script_file = open(script_filename, 'r')
        script = script_file.read()
        script_file.close()
        if verbose:
            print "File-len: %d" % len(script)

        # Filter with regex
        pattern = re.compile(r"%s" % regex)
        matches = re.findall(pattern, script)
        matched_content = ""
        if verbose:
            print matches
        # Group from regex found
        if len(matches) > 0:
            # Add verbatim-environment
            content += "%s" % begin_shaded_verbatim(fancy)
            # Add matched content groups
            matched_content = ""
            for match in matches:
                for group in match:
                    matched_content += "%s" % group
            # Add verbatim-environment end
            content += '\n'.join(map(textwrap.TextWrapper(width=70, subsequent_indent=' '*14).fill, matched_content.split('\n')))
            content += "\n" + end_shaded_verbatim(fancy)
            if verbose:
                print "Above pattern found in '%s', and imported" % script_filename
        # No group found, check regex vs. code
        else:
            content += "%s%s%s" % (
                "\\subsection*{ERROR}\n",
                "No code were found at this point with regex: %s," % regex,
                "please check your original file '%s'." % in_file.name)
            if verbose:
                print "File not imported, as pattern were not found in '%s'" % script_filename

    # %@exec with no file found, writing code with nice terminal-format (if fancy)
    elif in_line[:6] == '%@exec':
        in_line = in_file.readline()
        content += "%s%s%s" % (begin_execution_verbatim(fancy),
                               in_line,
                               end_execution_verbatim(fancy))
        if verbose and fancy:
            print "Added code-exec from '%s' in latex-terminal" % in_file.name
        elif verbose:
            print "Added code-exec from '%s' in verbatim" % in_file.name

    # regular %@import, for shaded blue (if fancy) output
    else:
        in_line = in_file.readline()
        content += begin_shaded_verbatim(fancy)
        while in_line[:2] != '%@':
            content += in_line
            in_line = in_file.readline()
        content += end_shaded_verbatim(fancy)
        if verbose and fancy:
            print "Shaded code from '%s' added" % in_file.name
        elif verbose:
            print "Code from '%s' added in verbatim" % in_file.name
    return content

def execute_script(in_file, in_line, fancy, verbose):
    """
Executes the file after %@exec with given parameters

Parameters
----------
latex_file : file
    The latex document currently being pre-processed

in_line : string
    Current line being processed

fancy : boolean
    Use fancy verbatim

verbose : boolean
    Be loud about what to do

Returns
-------
executed script : string
"""
    content = ""
    args = in_line.split()[1:]
    if verbose:
        print "Running %s script within '%s'" % (args[0], in_file.name)
    content += "%s" %(
        begin_execution_verbatim(fancy)
        + "$ ")
    for parameter in args:
        content += "%s " % parameter
    content += "\n"
    try:
        proc = subprocess.Popen((args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = proc.communicate()
        out_write = out.split('\n')       
        for line in out_write[:-1]:
            content += '\n'.join(map(textwrap.TextWrapper(width=70).fill, line.split('\n')))
#            content += "{0}\n".format(line)
        
    except OSError:
        print "! ! ! - - - ! ! !\n    File '%s' not found, check if path is correct" % args[0]
        content += "ERROR:%s_NOT_FOUND" % args[0]
    content += end_execution_verbatim(fancy)
    return content

def execute_code(in_file, in_line, fancy, verbose):
    """
Executes written code from the un-processed latex-file and prints the
terminal-values into the new pre-processed file.

Parameters
----------
in_file : file
    The latex document currently being pre-processed

in_line : string
    Current line being processed

fancy : boolean
    Use fancy verbatim

verbose : boolean
    Be loud about what to do

Returns
-------
executed code : string
    """
    content = ""
    if verbose:
        print "Executing code found in '%s'." % in_file.name
    command = in_line[2:]
    fake_filename = in_line.split()[1]
    fake_file = open(fake_filename, 'w')
    content += "%s" % (
        begin_shaded_verbatim(fancy)
        + "$ %s" % command)
    in_line = in_file.readline()
    while in_line.split()[0] != '%@':
        fake_file.write(in_line)
        content += in_line
        in_line = in_file.readline()
    fake_file.close()
    content += end_shaded_verbatim(fancy)
    content += execute_script(in_file, ('%@exec '+command), fancy, verbose)
    os.remove(fake_filename)
    if verbose:
        print "Executed (and removed) '%s' before writing output to '%s'" % (fake_filename, out_file.name)
    return content

def handle_command(in_file, in_line, fancy, verbose):
    """
Handle pre-processor command from un-processed file

Parameters
----------
in_file : file
    The latex document currently being pre-processed

in_line : string
    The current line being worked on in latex document

fancy : boolean
    Use fancy verbatim

verbose : boolean
    Be loud about what to do

Returns
-------
The content to write : string
    """
    content = ""
    if len(in_line)>3: # command may exist after %@
        if verbose:
            print "Additional functionality found, processing command: '%s'" % in_line[:-1]
        command = in_line.split()
        # %@import or %@exec-standalone found
        if command[0] == '%@import' or (command[0] == '%@exec' and len(command) == 1):
            content = import_script(in_file, in_line, fancy, verbose)
        # %@exec file found
        elif command[0] == '%@exec':
            content = execute_script(in_file, in_line, fancy, verbose)
        # %@python or %@bash found
        elif command[0] == '%@python' or command[0] == '%@bash':
            content = execute_code(in_file, in_line, fancy, verbose)
        # %@show found
        elif command[0] == '%@show':
            content = "%%Command '%@show' not implemented, skipped to last line; %@fi.\n"
            if verbose:
                print "Command '%@show' not implemented, skipping to last line; '%@fi'"
            in_line = in_file.readline()
            while in_line[:4] != '%@fi':
                in_line = in_file.readline()
        # %@command not found
        else:
            content = "%%Command '%s' not found.\n" % command[0]
    return content
                
def include_files(new_filepath, out_file, fancy, verbose):
    """
Un-processed file input/includes other files in need
of pre-processing. This function opens and handles
these new files before continuing with original file.

Parameters
----------
new_filepath : string
    Path to the new file to be included

out_file : file
    The file to write pre-processes to

fancy : boolean
    Use fancy verbatim if true

verbose : boolean
    Be loud about what to do
    """
    if verbose:
        print "'\input{...}' or '\include{...}' command found, including file '%s'" % new_filepath
    new_file = open(new_filepath, 'r')
    new_line = new_file.readline()
    handle_lines(new_file, out_file, new_line, fancy, verbose)

def handle_lines(in_file, out_file, in_line, fancy, verbose):
    """
Handle lines of un-processed file, and executes
correct writing to pre-processed file

Parameters
----------
in_file : file
    Current file being read(preprocessed)

out_file : file
    The file to write pre-processes to

in_line : string
    current line being processed

fancy : boolean
    Use fancy verbatim

verbose : boolean
    Be loud about what to do
    """
    file_content = ""
    if verbose:
        print "Handling filelines in '%s'..." % in_file.name
    while in_line:
        # %@ command found
        if len(in_line) > 2 and in_line[:2] == '%@':
            out_file.write(handle_command(in_file, in_line, fancy, verbose))
        # \input or \include found, handle new file
        elif in_line[:6] == '\input' or in_line[:8] == '\include':
            pattern = re.compile("(?<=\{)(.*)(?=\})", re.MULTILINE)
            match = re.search(pattern, in_line)
            include_files(match.group(), out_file, fancy, verbose)
        # regular print from old-to-new file
        else:
            out_file.write(in_line)
        in_line = in_file.readline()
    in_file.close()
    if verbose:
        print "All lines read in '%s'" % in_file.name

if __name__ == "__main__":
    """
Function ran if standalone.
    """
    # Argument Parser
    parser = argparse.ArgumentParser(description="Program preprocesses a latex-file ('infile') and produces a new latex-file ('outfile') with additional functionality")
    parser.add_argument("infile", help="Name of the latex-file you want preprocessed")
    parser.add_argument("-o", "--outfile", nargs=1, help="Name of the new file (cannot be equal to infile)")
    parser.add_argument("-f", "--fancy_verbatim", help="produces more fancy verbatim", action="store_true")
    parser.add_argument("-v", "--verbosity", help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    verbose = args.verbosity
    fancy = args.fancy_verbatim
    
    # To show doctest!
    if verbose:
        import doctest
        doctest.testmod()

    if verbose:
        print "Opening first file; '%s'" % args.infile
    # Original latex-file unprocessed
    in_file = open(args.infile, 'r')

    # Outfile name given
    if args.outfile:
        # outfile given with xtex format
        if re.search(re.compile(".*\.xtex"), args.outfile[0]):
            out_filename = args.outfile[0]
            if verbose:
                print "'%s' given with .xtex format" % out_filename
        # outfile given without xtex format, adding
        else:
            out_filename = args.outfile[0]+".xtex"
            if verbose:
                print "'%s' given without .xtex format, added .xtex" % out_filename
    # default outfile-name
    else:
        out_filename = args.infile[:-4] + ".xtex"
    # equal filenames cannot coexist
    if args.infile == out_filename:
        print "Your provided infile and outfile is equal, please provide different name(s)"

    else:
        if verbose:
            print "Creating/opening '%s' to write preprocess to" % out_filename
        out_file = open(out_filename, 'w')
        in_line = in_file.readline()
        # \documentclass is needed before anything else
        while in_line[:14] != "\documentclass":
            out_file.write(in_line)
            in_line = in_file.readline()
        out_file.write(in_line)
        # fancy Verbatim needs additional packages
        if fancy:
            if verbose:
                print "Fancy verbatim enabled - importing needed packages..."
            out_file.write(packages)
            if verbose:
                print "Packages imported"

        # Commence preprocessing
        in_line = in_file.readline()
        handle_lines(in_file, out_file, in_line, fancy, verbose)
        out_file.close()
        if verbose:
            print "Preprocessing complete and written to '%s'." % out_file.name
