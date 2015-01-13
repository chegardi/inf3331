import subprocess, re, argparse, os

def preprocess(args, verbose):
    """
Handles a possible preprocess before compiling.

Parameters
----------
args : ArgumentParser
    The arguments parsed

verbose : boolean
    Be loud about what to do
    """
    if verbose:
        print "Preprocessing file '%s'" % args.preprocess
        pre_args = "python prepro.py -v -f -o %s %s" % (args.compilefile, args.preprocess[0])
    else:
        pre_args = "python prepro.py -f -o %s %s" % (args.compilefile, args.preprocess[0])
    preproc = subprocess.Popen(pre_args, shell=True,\
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    preout, preerr = preproc.communicate()
    if verbose:
        print preout

def compile(compilefile, interaction, verbose):
    """
Compiles latex file with given arguments.

Parameters
----------
args : ArgumentParser
    The arguments passed and processed

interaction : string
    Interaction-mode for passing to pdflatex

verbose : boolean
    Be loud about what you do
    """
    if verbose:
        print "Compiling file '%s'" % compilefile
    if interaction:
        interaction = "-interaction=nonstopmode"
    else:
        interaction = "-halt-on-error"

    # Uses subprocess to compilate given file
    proc = subprocess.Popen("pdflatex -file-line-error %s %s"\
                        % (interaction, compilefile), shell=True,\
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = proc.communicate()    
    
    # Checks for error messages in format ERROR:LINENUMBER:ERRORMESSAGE
    pattern = re.compile(".*:\d+:.*\n", re.MULTILINE)
    match = re.search(pattern, out)
    if match:
        if verbose:
            print "Printing error messages:"
        messages = re.findall(pattern,out)
        for message in messages:
            print message[:len(message)-2]
            # the "list" ending is to remove '\n' for better looking print
    elif not os.path.isfile(compilefile[:-5] + ".pdf"):
        if verbose:
            print "Compilation UNsuccessful"
    else:
        if verbose:
            print "Compilation successful."
    printout(out, verbose)

def printout(out, verbose):
    """
Prints out information about compilation

Parameters
----------
out : string
    The whole output from pdflatex-compilation

verbose : boolean
    Be loud about what to do
    """
    if verbose:
        print "Last two lines from latex own output:"
    line_pattern = re.compile(".*\n|\n{2}", re.MULTILINE)
    line_match = re.search(line_pattern, out)
    if line_match:
        all_matches = re.findall(line_pattern, out)
        two_lines = all_matches[len(all_matches)-2:]
        for line in two_lines:
            print "%s" % line[:len(line)-2]
            # the [:len(line)-2] removes last to "endlines" from output

if __name__ == '__main__':
    """
This function compiles a latex file.
It aim is to reduce the spam from pdflatex terminal print to a more sensible output.
    """
    parser = argparse.ArgumentParser(description="A latex compiler shortening terminal output to more meaningful printing, and added functionality")
    parser.add_argument("-v", "--verbosity", help="Be loud about what to do", action="store_true")
    parser.add_argument("-i", "--interaction", help="Sets pdflatex to interaction=nonstopmode to True", action="store_true")
    parser.add_argument("-p", "--preprocess", nargs=1, help="Will preprocess using python prepro.py\nwith compilefile as 'outfile'-name, and -f enabled. See prepro.py -h for details")
    parser.add_argument("compilefile", help="The latex-file to be compiled")
    args = parser.parse_args()
    verbose = args.verbosity
    interaction = args.interaction
    
    # Run preprocess (if enabled)
    if args.preprocess:
        preprocess(args, verbose)

    # Run compilation
    compile(args.compilefile, interaction, verbose)



