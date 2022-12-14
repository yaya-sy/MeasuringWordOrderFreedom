"""
Module implementing a function for downloading\
Universal Dependencies corpora from githubs.
"""
from urllib.request import urlretrieve
from pathlib import Path
from argparse import ArgumentParser

import yaml
from tqdm import tqdm

def download_conll_corpora(config: str, output_directory: str) -> None:
    """
    Download Universal Dependencies corpora\
    using a config file. This file must contain\
    the urls of the corpora for each language.

    Parameters
    ----------
    - config: str
        The config file containing the urls of the Universal Dependencies\
        corpora for each language.
    - output_directory: str
        The folder where the downloaded corpora will be stored.
    """
    output_directory = Path(output_directory)
    output_directory.mkdir(exist_ok=True, parents=True)

    with open(config, "r") as config_file:
        corpora = yaml.safe_load(config_file)
    for language in tqdm(corpora, total=len(corpora)):
        for url in corpora[language]:
            urlretrieve(url, output_directory / f'{language}.conllu')

def main():
    parser = ArgumentParser()
    parser.add_argument("-c", "--configs", help="File containing the urls of the corpora for each language.")
    parser.add_argument("-o", "--output_directory", help="Where the output files will be stored.")

    args = parser.parse_args()
    download_conll_corpora(args.configs, args.output_directory)

if __name__ == "__main__":
    main()