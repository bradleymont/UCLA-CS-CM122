from os.path import join
import sys
import time
from collections import defaultdict, Counter
import sys
import os
import zipfile
import argparse
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../.."))


def parse_reads_file(reads_fn):
    """
    :param reads_fn: the file containing all of the reads
    :return: outputs a list of all paired-end reads
    """
    try:
        with open(reads_fn, 'r') as rFile:
            print("Parsing Reads")
            first_line = True
            count = 0
            all_reads = []
            for line in rFile:
                count += 1
                if count % 1000 == 0:
                    print(count, " reads done")
                if first_line:
                    first_line = False
                    continue
                ends = line.strip().split(',')
                all_reads.append(ends)
        return all_reads
    except IOError:
        print("Could not read file: ", reads_fn)
        return None


"""
    TODO: Use this space to implement any additional functions you might need
"""

# breaks down the reads into kmers
def break_into_kmers(reads, k):
    kmers = []

    for read in reads:
        for i in range(0, len(read) - k + 1):
            kmers.append(read[i:(i + k)])

    return kmers

# returns a dictionary that maps each read to the amount of times it appears
def get_kmer_frequencies(kmers):
    kmer_to_frequency = {}

    for kmer in kmers:
        if kmer in kmer_to_frequency:
            kmer_to_frequency[kmer] += 1
        else:
            kmer_to_frequency[kmer] = 1

    return kmer_to_frequency

# returns an adjacency list representation of the de Bruijn graph
# even if a kmer has a frequency > 1, we still only add 1 edge (removing duplicates)
def form_de_bruijn_graph(kmer_to_frequency):
    # for each k-mer:
    #   prefix -> suffix
    adjacency_list = {}
    for kmer in kmer_to_frequency:
        prefix = kmer[:-1]
        suffix = kmer[1:]
        if prefix in adjacency_list:
            adjacency_list[prefix].append(suffix)
        else:
            adjacency_list[prefix] = [suffix]

    return adjacency_list

# returns the degrees for each node in a graph
# node -> [in-degree,out-degree]
def get_node_degrees(adjacency_list):
    node_degrees = {}
    for outgoing_node, incoming_nodes in adjacency_list.items():
        # increment the out-degree for outgoing_node by the number of incoming nodes
        if outgoing_node in node_degrees:
            node_degrees[outgoing_node][1] += len(incoming_nodes)
        else:
            node_degrees[outgoing_node] = [0, len(incoming_nodes)]

        # increment the in-degree for each incoming node by 1
        for incoming_node in incoming_nodes:
            if incoming_node in node_degrees:
                node_degrees[incoming_node][0] += 1
            else:
                node_degrees[incoming_node] = [1, 0]

    return node_degrees

# returns all maximal non-branching paths in De Bruijn Graph
def find_paths(adjacency_list):

    # find in-degrees and out-degrees for each node
    node_degrees = get_node_degrees(adjacency_list)

    # find maximal non-branching paths

    # Paths ← empty list
    paths = []

    # for each node v in graph
    for v in list(node_degrees.keys()):
        # if v is not a 1-in-1-out node
        if node_degrees[v] != [1,1]:
            # if out(v) > 0
            if node_degrees[v][1] > 0:
                # for each outgoing edge (v, w) from v
                for w in adjacency_list[v]:
                    # NonBranchingPath ← the path consisting of single edge (v, w)
                    non_branching_path = [v,w]
                    # while w is a 1-in-1-out node
                    while node_degrees[w] == [1,1]:
                        # extend NonBranchingPath by the edge (w, u)
                        u = adjacency_list[w][0]
                        non_branching_path.append(u)
                        # w ← u
                        w = u
                    # add NonBranchingPath to the set Paths
                    paths.append(non_branching_path)

    # for each isolated cycle Cycle in Graph
    #   add Cycle to Paths

    # isolated cycles won't contain any of the nodes traversed in paths, so remove those nodes from our graph
    for path in paths:
        for node in path:
            if node in adjacency_list:
                del adjacency_list[node]

    # remove any nodes that aren't 1-in-1-out nodes
    for node in list(adjacency_list.keys()):
        # if node isn't a 1-in-1-out node
        if node_degrees[node] != [1,1]:
            del adjacency_list[node]

    # adjacency_list now consists of only 1-in-1-out nodes that weren't traversed in any of our other paths
    # while adjacency_list is not empty
    while adjacency_list:
        # select any node as the starting node for our cycle
        start_node = list(adjacency_list.keys())[0]
        
        curr_node = start_node
        next_node = adjacency_list[start_node][0]

        cycle = [start_node]

        first_time_visiting_start_node = True
        while curr_node != start_node or first_time_visiting_start_node:
            first_time_visiting_start_node = False

            # remove curr_node from adjacency_list
            del adjacency_list[curr_node]

            # add next_node to cycle
            cycle.append(next_node)

            # update curr_node and next_node
            curr_node = next_node

            # make sure we haven't reached a dead end
            if next_node not in adjacency_list:
                continue
            next_node = adjacency_list[next_node][0]
        
        # add our cycle to paths
        paths.append(cycle)

    return paths

# returns the contigs formed by the maximal non-branching paths
def form_contigs(paths):
    contigs = []

    for path in paths:
        contig = path[0] # add the entire first kmer to the contig
        for i in range(1, len(path)):
            contig += path[i][-1] # add the end of each kmer to the contig
        contigs.append(contig)

    return contigs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='basic_assembly.py takes in data for homework assignment 3 consisting '
                                                 'of a set of reads and aligns the reads to the reference genome.')
    parser.add_argument('-r', '--reads', required=True, dest='reads_file',
                        help='File containg sequencing reads.')
    parser.add_argument('-o', '--outputFile', required=True, dest='output_file',
                        help='Output file name.')
    parser.add_argument('-t', '--outputHeader', required=True, dest='output_header',
                        help='String that needs to be outputted on the first line of the output file so that the\n'
                             'online submission system recognizes which leaderboard this file should be submitted to.\n'
                             'This HAS to be one of the following:\n'
                             '1) spectrum_A_1_chr_1 for 10K spectrum reads practice data\n'
                             '2) practice_A_2_chr_1 for 10k normal reads practice data\n'
                             '3) hw3all_A_3_chr_1 for project 3 for-credit data\n')
    args = parser.parse_args()
    reads_fn = args.reads_file

    input_reads = parse_reads_file(reads_fn)
    if input_reads is None:
        sys.exit(1)

    """
    TODO: Call functions to do the actual assembly here
    """

    ###### STEP 1: CONVERT FROM READ-PAIRS TO SINGLE READS ######
    # in order to avoid issues with variable length read pairs, we will
    # consider each part of the read pair as its own independent read
    # therefore, we "flatten" the input_reads list so each read is its own entry
    input_reads = [read for read_pair in input_reads for read in read_pair]

    ###### STEP 2: BREAK DOWN READS INTO SMALLER K-MERS ######
    # currently, our reads are 50-mers
    # we will use k = 25 to break them down into 25-mers
    kmers = break_into_kmers(input_reads, 25)

    ###### STEP 3: REMOVE INFREQUENT KMERS ######
    # any kmer with low frequency has a high probability of being erroneous
    
    # first, map each kmer to the amount of times it occurs
    kmer_to_frequency = get_kmer_frequencies(kmers)

    # then, remove any kmers with a frequency <= 3 - we assume they're erroneous
    kmer_to_frequency = {kmer: freq for kmer, freq in kmer_to_frequency.items() if freq > 3}

    ###### STEP 4: CONSTRUCT DE BRUIJN GRAPH ######
    # adjacency list representation of the de Bruijn graph
    # Note: we also remove duplicate edges from the de Bruijn graph
    adjacency_list = form_de_bruijn_graph(kmer_to_frequency)

    ###### STEP 5: FIND ALL MAXIMAL NON-BRANCHING PATHS IN DE BRUIJN GRAPH ######
    paths = find_paths(adjacency_list)

    ###### STEP 6: FORM CONTIGS FROM MAXIMAL NON-BRANCHING PATHS ######
    contigs = form_contigs(paths)

    output_fn = args.output_file
    zip_fn = output_fn + '.zip'
    with open(output_fn, 'w') as output_file:
        output_file.write('>' + args.output_header + '\n')
        output_file.write('>ASSEMBLY\n')
        output_file.write('\n'.join(contigs))
    with zipfile.ZipFile(zip_fn, 'w') as myzip:
        myzip.write(output_fn)
