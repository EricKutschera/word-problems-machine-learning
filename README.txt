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
