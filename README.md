# Tools implemented for the [COST-ELTeC project](https://github.com/COST-ELTeC/)

This README contains the list, description and the usage of the tools that can be found in this repository. 

## Process COST-ELTeC corpus with [the _e-magyar_ digital language processing toolchain](http://e-magyar.hu/en/intro) (process_corpus.py)

- Install requirements in `requirements.txt`
- Clone https://github.com/COST-ELTeC/WG2-Sample.git to the __WG2-Sample__ directory
- Install https://github.com/dlt-rilmta/emtsv.git to the __emtsv__ directory
- `python3 process_corpus.py > output.csv`

## Create a stratified random sample from the processed corpus for manual examination (stratified_random_sampler.py)

- Install requirements in `requirements.txt`
- `python3 output.csv sample.csv 3 30 50000` for 50000 token sample of sentences that each have >= 3 and < 30 token equally for each document

## License

The tools in this repository are licensed under the LGPL 3.0 license.
