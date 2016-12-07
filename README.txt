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
    * find closest noun for number slot
      (to be used for features but is not a feature)
    * find remaining single slot features
      * has the same lemma as a question object
      * is a question object
      * is in a question sentence
      * is word lemma and is near particular constant in question
        (true if this slot lemma matches feature lemma
         and this slot is near the feature constant in the template)
    * find remaining slot pair features
      * Dependency path contains: word
      * Dependency path contains: Dependency Type
      * Dependency path contains: (word, Dependency Type)
      * are the same word instance
      * have the same lemma
      * in the same sentence
      * in the same phrase
      * connected by a preposition
      * numbers are equal
      * one number is larger than the other
      * equivalent relationship ?->
        (slot pair) pair relationships?

  * Find the vector of all possible features
    * define slot signatures to determine all possible
      single slot and slot pair signatures
    * Choose an ordering for all features which
      requires knowing up front all
      * count of unique templates
      * slot/slot pair signatures
      * unigrams
      * per single slot signature
        * lemmas
        * constants
      * per slot pair signature
        * word
        * dependency type

  * Perform Parameter estimation for the weight vector theta
    * theta has one real valued weight for each
      feature in the vector of all possible features
    * maximize the conditional log-likelihood of the training data
      where for each word problem all derivations which are "valid"
      are included
      * valid is either: correct answer, or correct system of equations
      * focus on correct system of equations since that is what is referred
        to as supervised learning in the paper and gives better results
    * use L-BFGS to perform the maximization
      https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.fmin_l_bfgs_b.html#scipy.optimize.fmin_l_bfgs_b

  * Choose the most likely answer for a word problem
    * use beam search over the possible derivations for that word problem
      using the set of unique templates
    * compute the probability of each derivation using the parameter weight vector theta
    * add together the probabilities for derivations with the same answer
    * pick the answer with highest probability

  * Perform 5-fold cross validation
