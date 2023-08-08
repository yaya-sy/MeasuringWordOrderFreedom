# MeasuringWordOrderFreedom

![image info](./results/plot.jpg)

Reproducing the results of the Head Direction Entropy for measuring the degree of word order freedom in human languages. This metric is presented in details in [Quantifying Word Order Freedom in Dependency Corpora](https://aclanthology.org/W15-2112) (Futrell et al., 2015)

## Activate the conda environment

I advise to use a conda environment. You can create it by using the following command-line:

```bash
conda env create -f environment.yml
```

and activate it:
```bash
conda activate word-order
```

## Download the data

You can use the given corpora urls for each language (see the `configs/configs.yml` file) for downloading the data:

```bash
python scripts/download_conllu_corpora.py -c configs/configs.yml -o data 
```

where:

`-c The config file containing the urls of the Universal Dependencies corpora for each language.`

`-o The folder where the downloaded corpora will be stored.`

## Run the estimation of the Head Direction Entropies

Run this command line in order to produce the results:

```bash
python scripts/head_direction_entropy.py -c data/ -o results/
```

where:

`-c Folder containing the conllu copora.`

`-o Where the results will be stored.`

## Plot

You can use the r notebook in `scripts/plot.Rmd` for reproducing the figure.
