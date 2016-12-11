Final Project for CS 446 UIUC Fall 2016

Goal is to create a machine learning system which can solve math word problems
For more details see proposal.txt and papers_work_is_based_on/*.pdf

How to use:

To download the code and data used in the paper that inspired this work:
./download_provided_code.sh

To generate NLP parsed data from a set of word problems:
store them in the proper format in data/questions.json
./generate_parse_xml.sh

If unable to use the provided scripts to parse the data,
the original data set is parsed and can be extracted:
tar -xzf sample_parses.tar.gz


Before running the Python code:
./setup_venv.sh
source venv/bin/activate

To find the set of unique templates:
python main.py find-template-set

will output to unique_templates.json
takes about an hour

To extract the feature vector:
python main.py extract-features -i {question index}

TODOs
  * find remaining features
    * find remaining slot pair features
      * Dependency path contains: word
      * Dependency path contains: Dependency Type
      * Dependency path contains: (word, Dependency Type)
      * connected by a preposition
      * equivalent relationship ?->
        (slot pair) pair relationships?

  * understand if L-BFGS is working
    https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.fmin_l_bfgs_b.html#scipy.optimize.fmin_l_bfgs_b

  * Perform 5-fold cross validation
