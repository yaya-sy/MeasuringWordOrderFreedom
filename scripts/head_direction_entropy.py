"""This module implements a class for estimating\
    the Head Direction Entropy metric developed\
    by (Futrell et al., 2015)"""

# standard python packages
from typing import Iterable, Iterator, List, Tuple
from pathlib import Path
from collections import defaultdict
from math import log2
from argparse import ArgumentParser
# non native packages
import pandas as pd

PoS = str
Head = int
Relation = str

LocalTree = Tuple[PoS, Head, Relation]
UtteranceTree = List[LocalTree]

WORD_ORDER_VARIABLES: list = ["INITIAL", "FINAL"]

class HeadDirectionEntropy:
    """
    This class implements the Head Direction Entropy for\
    measuring the degree of freedom of the word order.
    (Futrell et al., 2015) proposes to measure this by looking how well\
    the word order of a given sentence can be predicted
    given its tree.
    """

    def trees(self,
              conll_file: str
              ) -> Iterator[UtteranceTree]:
        """
        Retrieve local trees relevant for computing\
        the head direction entropy.

        Parameters
        ----------
        - conll_file: str
            Path to the conll file on which\
            estimate the head direction entropy.
        
        Returns
        -------
        Iterator:
            A generator over sentence trees seen\
            as a list of local subtrees.
        """

        utterance_trees: list = []
        with open(conll_file, "r") as trees_file:
            for line in trees_file :
                line: str = line.strip()
                if line.startswith("#") or not line :
                    if utterance_trees : 
                        yield utterance_trees
                        utterance_trees: list = []
                        continue
                    continue
                idx, _, _, pos, _, _, head, relation = line.split("\t")[:8]
                if "-" in idx : 
                    continue
                utterance_trees.append((pos, int(head), relation))
    
    def joint_counts(self,
                     utterance_trees: Iterable[UtteranceTree],
                     max_sentences: int=1_000
                     ) -> defaultdict:
        """
        Compute the joint counts of the variable describing\
        the triplets (pos, head, relation) and of the binary variable\
        describing the relative position of a dependant and its head\
        (possible values are "initial", or "final").

        Parameters
        ----------
        - sentences: Iterable
            Iterable containing the triplets for each sentence.
        
        Returns
        -------
        - defaultdict:
            Dictionnary associating each triplet the number\
            of time the dependant preceeds or follows its head.
        """
        count_table: defaultdict = defaultdict(lambda: defaultdict(int))
        sentences_counter = 1
        for sentence in utterance_trees:
            if max_sentences is not None and sentences_counter > max_sentences:
                continue
            for idx, (pos, head, relation) in enumerate(sentence, 1):
                dependant_pos = pos
                head = int(head)
                if head == 0 or pos == "PUNCT":
                    continue
                head_direction = WORD_ORDER_VARIABLES[int(idx > head)]
                head_pos, *_ = sentence[head - 1]
                count_table[(dependant_pos, head_pos, relation)][head_direction] += 1
            sentences_counter += 1
        return count_table
    
    def compute_total_tree_features(self,
                                    count_table: defaultdict
                                    ) -> int:
        """Sum all the number of occurencies of each triplet."""
        return sum(sum(count_table[feature].values()) for feature in count_table)
    
    def head_direction_entropy(self,
                               joint_counts_table: defaultdict
                               ) -> float:
        """
        Compute the Head Direction Entropy from the joint counts\
        of the variables.

        Parameters
        ----------
        - joint_counts_table:
            The joint counts between the variable describing the trees and\
            the binary variable describing the head direction ("INITIAL" or "FINAL").
        
        Returns
        -------
        - float:
            The conditional entropy of the head direction given the trees.
        """
        conditional_entropy = 0.0
        total_tree_features = self.compute_total_tree_features(joint_counts_table)
        for tree_feature in joint_counts_table:
            seen_tree_feature = sum(joint_counts_table[tree_feature].values())
            prob_tree_feature = seen_tree_feature / total_tree_features
            for direction in joint_counts_table[tree_feature]:
                prob_direction_given_tree = joint_counts_table[tree_feature][direction] / seen_tree_feature
                entropy_direction_given_tree = prob_direction_given_tree * log2(prob_direction_given_tree)
                conditional_entropy -= prob_tree_feature * entropy_direction_given_tree
        return conditional_entropy
    
    def __call__(self, conll_file, max_sentences=1_000) -> float:
        """
        Run the estimation of the degree word order freedom\
        given the sentences.
        
        Parameters
        ----------
        sentences: Iterable
            Each word of each sentence is represented as a triplet\
            containing its POS, its head and their relation.
        
        Return
        ------
        - float:
            Entropy to be interpreted as measuring\
            the degree of word order freedom.
        """
        utterances_tree: UtteranceTree = self.trees(conll_file)
        joint_counts_table: defaultdict = self.joint_counts(utterances_tree, max_sentences)
        return self.head_direction_entropy(joint_counts_table)

def parse_arguments():
    """Get the arguments from command line."""
    parser = ArgumentParser()
    parser.add_argument("-c", "--corpora_folder", help="File containing the conll copora.")
    parser.add_argument("-o", "--output_path", help="Where the results will be stored.")
    return parser.parse_args()

def main():
    """
    Call the head direction entropy estimator\
    from conll corpora.
    """
    args = parse_arguments()
    output_path = Path(args.output_path)
    output_path.mkdir(exist_ok=True, parents=True)
    entropy_estimator = HeadDirectionEntropy()
    results = []
    for conll_file in Path(args.corpora_folder).glob("*.conllu"):
        language = conll_file.stem
        entropy_1000 = entropy_estimator(conll_file, 1000)
        entropy_all = entropy_estimator(conll_file, None)
        language_results = {
                            "language" : language,
                            "entropy_1000" : entropy_1000,
                            "entropy_all" : entropy_all
                            }
        results.append(language_results)
    print(results)
    pd.DataFrame(results).to_csv(output_path / "restults.csv")



if __name__ == "__main__":
    main()
