This repository contains code and corpora for the twitter robot-journalists [@DaMataNews](https://twitter.com/DaMataNews), [@DaMataReporter](https://twitter.com/DaMataReporter) and [@CoronaReporter](https://twitter.com/CoronaReporter). This work was described in the following articles:

## DaMata: A Robot-Journalist Covering the Brazilian Amazon Deforestation
_INLG 2020 -  13th International Conference on Natural Language Generation_  
URL: https://www.aclweb.org/anthology/2020.inlg-1.15


## Towards Fully Automated News Reporting in Brazilian Portuguese
_ENIAC 2020 - XVII Encontro Nacional de Inteligência Artificial e Computacional_  
DOI: https://doi.org/10.5753/eniac.2020.12158



# Requirements

Dependencies to run the code may be installed by the following command:

```
pip install -r requirements.txt
```

# Database

Non-linguistic data about COVID-19 in Brazil and Deforestation in the Legal Amazon area extracted from the web and stored in a private [MongoDB](https://www.mongodb.com/) database, accessed by the [MongoEngine ORM](http://mongoengine.org/) framework. So in order to run the code, make sure to set up a MongoDB database and update the login info on [the db/model.py file](https://github.com/BotsDoBem/DEMO_INPE_COVID/blob/master/db/model.py#L11). Source data for COVID-19 can be retrieved from [Worldometers website](https://www.worldometers.info/coronavirus/country/brazil/) and data for Amazon deforestation can be retrieved from [INPE Terrabrasilis](http://terrabrasilis.dpi.inpe.br/homologation/file-delivery/download/deter-amz/daily) platform.

# Paths

In the [paths.py](https://github.com/BotsDoBem/DEMO_INPE_COVID/blob/master/paths.py) file, you will see the path for several important files, such as the structuring, lexicalization, references grammas as well as the lexicon and the Twitter API login info. In this file, make sure to add the proper files and keys before run the code.

# Execution

Once all the dependencies are solved, the robot-journalist can be tested on the Jupyter files [covid19.ipynb](https://github.com/BotsDoBem/DEMO_INPE_COVID/blob/master/covid19.ipynb) and [deter.ipynb](https://github.com/BotsDoBem/DEMO_INPE_COVID/blob/master/deter.ipynb). To be executed on a production environmente, the publisher.py files for [COVID-19](https://github.com/BotsDoBem/DEMO_INPE_COVID/blob/master/covid19/publisher.py) and [Deforestation](https://github.com/BotsDoBem/DEMO_INPE_COVID/blob/master/inpe_deter/publisher.py) can be executed.
