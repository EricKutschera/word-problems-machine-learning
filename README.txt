Final Project for CS 446 UIUC Fall 2016

Goal is to create a machine learning system which can solve math word problems
For more details see proposal.txt and papers_work_is_based_on/*.pdf

The structure of this README is:
  * How to use:
      provides commands to run which demonstrate the functionality

  * Tour of code:
      Provides a brief description of each source file

How to use:

  * To download the code and data used in the paper that inspired this work:
    $ ./download_provided_code.sh

  * To generate NLP parsed data from a set of word problems:
    store them in the proper format in data/questions.json
    $ ./generate_parse_xml.sh

    Generating the NLP data takes about 4 minutes

  * If unable to use the provided scripts to parse the data,
    the original data set is parsed and can be extracted:
    $ tar -xzf sample_parses.tar.gz

  * Before running the Python code:
    $ ./setup_venv.sh
    $ source venv/bin/activate

  * To view a json representation of a processed question
    provide the iIndex number of the problem from data/questions.json
    $ python main.py print -i {iIndex}
    $ python main.py print -i 2598

    The result for 2598 is committed to the repo in pretty printed
    form as printed_2598.json
    The extracted template can be viewed in this output

  * To find the set of unique templates:
    $ python main.py find-template-set

    This can take about two hours and will output to unique_templates.json
    A pretty printed version is committed to the repo

  * To extract a feature vector for an example derivation:
    $ python main.py extract-features

    An example output is pretty printed and committed to the repo as:
    derivation_features.json

  * To identify how many unique templates there are for any number
    of specific word problems
    $ python main.py count-unique -u {iIndex 1} {iIndex 2} {iIndex 3} ...

    Looking at unique_templates.json there is a "wp_template_map"
    which indicates that problems 6149, 15, and 17 all share a template
    but 7 has a different template

    $ python main.py count-unique -u 6149 15 17
    will show that there is one template

    $ python main.py count-unique -u 6149 7
    will show there are two unique templates

  * You can start an evaluation procedure to train on some data
    and report correct classifications over a test fold

    $ python main.py fold -nf {number of folds} -tf {test fold}

    Due to the computational costs of the procedure, it is only looking
    at 5 of the 514 examples

    To train on examples 0->3 and test on example 4
    $ python main.py fold -nf 5 -tf 0

    This portion requires additional work before it will work correctly
    Making the call above will show some output, but it will take a long
    time and will not likely make any correct classifications


Tour of code:

  * main.py:
      makes calls into other files to generate useful output

  * template.py:
    provides implementation of:
      * generalizing a system of equations into a template
      * Comparing two templates for equality to determine the
        set of unique templates

  * optimize.py:
      Sets up the inputs necessary to call into the L-BFGS library
      function which we are using.

  * classifier.py:
      Defines the Log Likelihood of the data and the gradient of that Likelihood.
      Those are the inputs the L-BFGS optimization procedure requires
      to choose the best parameter vector, Theta.
      It also implements the validation function used for pruning the
      beam search.

  * beam.py:
      Provides the implementation of beam search over the space of
      all possible derivations.

  * derivation.py:
      Provides the functions to iteratively fill in a derivation
      for a word problem. This is what governs the ordering of the
      beam search.

  * features.py:
      Provides the definition of all features that we use.
      It defines the ordering of those features for the vector Theta.
      It provides a function to evaluate all of the features for a
      given derivation.

  * nlp.py:
      Provides objects which hold the information extracted from
      the XML files the NLP utility we are using outputs.
      It also provides functions for extracting information
      used in feature extraction and template induction.

  * parse_tree.py:
      The NLP utility we use provides each sentence with a parse tree.
      That tree is given in string form using parens for nesting.
      This file converts that string into a tree object.

  * equation.py:
      Provides a representation for a single equation.
      Handles the conversion for a string into the format of
      the symbolic mathematics library Sympy

  * word_problem.py:
      links together the labeled example, nlp, and template

  * labeled_example.py:
      Provides an interface to the labeled data used as input
      which is parsed from data/questions.json

  * slot_signatures.py:
      simply holds the tuples of information which identify slots and slot pairs

  * util.py:
      helper function used in multiple files

  * text_to_int.py:
      code borrowed from the internet to convert text into integers
      used for finding numbers in the problem text
