import sys
import argparse
import numpy as np
import time
import zipfile

KMER_SIZE = 48
ERROR_THRESHOLD = 2

def parse_reads_file(reads_fn):
    """
    :param reads_fn: the file containing all of the reads
    :return: outputs a list of all paired-end reads

    HINT: This might not work well if the number of reads is too large to handle in memory
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


def parse_ref_file(ref_fn):
    """
    :param ref_fn: the file containing the reference genome
    :return: a string containing the reference genome
    """
    try:
        with open(ref_fn, 'r') as gFile:
            print("Parsing Ref")
            first_line = True
            ref_genome = ''
            for line in gFile:
                if first_line:
                    first_line = False
                    continue
                ref_genome += line.strip()
        return ref_genome
    except IOError:
        print("Could not read file: ", ref_fn)
        return None


"""
    TODO: Use this space to implement any additional functions you might need
"""

# maps each kmer in a reference genome to the positions that it occurs
def index_genome(reference):
    index = {}

    part_size = int(KMER_SIZE / 3)

    for i in range(len(reference) - part_size + 1):
        kmer = reference[i:(i + part_size)]
        if kmer in index:
            index[kmer].append(i)
        else:
            index[kmer] = [i]

    return index

# breaks down the reads into kmers
def break_into_kmers(reads):
    kmers = []

    for read in reads:
        for i in range(len(read) - KMER_SIZE + 1):
            kmers.append(read[i:(i + KMER_SIZE)])

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

# takes in a kmer and returns its possible starting indexes in the reference genome
# Note: since we allow at most ERROR_THRESHOLD errors, one of the 3 parts must match perfectly to the reference genome
def get_possible_indices(kmer, reference_index):
    possible_indices = []

    # first divide the kmer into 1/3s
    part_size = int(KMER_SIZE / 3)
    first, second, third = kmer[0:part_size], kmer[part_size:(2 * part_size)], kmer[(2 * part_size):]

    # check to see if the first part matches perfectly
    if first in reference_index:
        # add those indices as possible start indices
        possible_indices += reference_index[first]

    # check to see if the second part matches perfectly
    if second in reference_index:
        # subtract part_size to get the start of the kmer
        second_matching_indices = [(index - part_size) for index in reference_index[second]]
        # make sure all indices >= 0
        second_matching_indices = list(filter(lambda index: index >= 0, second_matching_indices))
        possible_indices += second_matching_indices

    # check to see if the third part matches perfectly
    if third in reference_index:
        # subtract 2 * part_size to get the start of the kmer
        third_matching_indices = [(index - (2 * part_size)) for index in reference_index[third]]
        # make sure all indices >= 0
        third_matching_indices = list(filter(lambda index: index >= 0, third_matching_indices))
        possible_indices += third_matching_indices

    return possible_indices

# returns the matching sections, as well as their indices in the genome for the kmer
# Note: matching means <= ERROR_THRESHOLD mismatches
def get_matching_sections(kmer, reference, possible_indices):
    # list of (kmer, index) pairs in the reference genome that match the kmer we read
    matching_sections = []

    for index in possible_indices:
        # get the matching section of the genome
        matching_section = reference[index:(index + KMER_SIZE)]

        if len(matching_section) < KMER_SIZE:
            continue

        # get the amount of mismatches between the kmer and the matching section
        num_mismatches = sum(kmer[i] != matching_section[i] for i in range(KMER_SIZE))

        # if the # of mismatches <= ERROR_THRESHOLD mismatches
        # AND if # mismatches > 0 since there's no SNPs if it matches perfectly
        if num_mismatches > 0 and num_mismatches <= ERROR_THRESHOLD:
            # consider this section a match
            matching_sections.append((matching_section, index))

    return matching_sections

# takes in a kmer and its matching sections and returns any SNPs
def get_snps_for_kmer(kmer, matching_sections):
    # maps a location to its SNP
    kmer_snps = {}

    for ref_section, start_index in matching_sections:
        for i in range(KMER_SIZE):
            if kmer[i] != ref_section[i]:
                # we found a snp
                reference_allele = ref_section[i]
                variant_allele = kmer[i]
                location = start_index + i
                snp = [reference_allele, variant_allele, location]
                if location not in kmer_snps:
                    kmer_snps[location] = snp
    
    return kmer_snps

# takes in kmers and a reference index and returns the SNPs
def get_snps(kmers, reference_index, reference):
    # maps an index to the snp at that index
    snps = {}

    for kmer in kmers:
        # get all the possible indices that the kmer could start at
        possible_indices = get_possible_indices(kmer, reference_index)

        # remove duplicates from possible_indices
        possible_indices = list(dict.fromkeys(possible_indices))

        # get matching sections in reference genome
        # each matching section is a (kmer, index) pair
        matching_sections = get_matching_sections(kmer, reference, possible_indices)

        # if there's no matching sections, there won't be any SNPs
        if len(matching_sections) == 0:
            continue

        # find the SNPs and add them to our result
        curr_snps = get_snps_for_kmer(kmer, matching_sections)
        
        # add the SNPs to our result (avoiding adding multiple SNPs at the same location)
        for index in curr_snps:
            if index not in snps:
                snps[index] = curr_snps[index]

    # return only the SNPs
    return list(snps.values())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='basic_hasher.py takes in data for homework assignment 2 consisting '
                                     'of a genome and a set of reads and aligns the reads to the reference genome, '
                                     'then calls SNPS and indels based on this alignment.')
    parser.add_argument('-g', '--referenceGenome', required=True, dest='reference_file',
                        help='File containing a reference genome.')
    parser.add_argument('-r', '--reads', required=True, dest='reads_file',
                        help='File containg sequencing reads.')
    parser.add_argument('-o', '--outputFile', required=True, dest='output_file',
                        help='Output file name.')
    parser.add_argument('-t', '--outputHeader', required=True, dest='output_header',
                        help='String that needs to be outputted on the first line of the output file so that the\n'
                             'online submission system recognizes which leaderboard this file should be submitted to.\n'
                             'This HAS to be one of the following:\n'
                             '1) practice_W_3_chr_1 for 10K length genome practice data\n'
                             '2) practice_E_1_chr_1 for 1 million length genome practice data\n'
                             '3) hw2undergrad_E_2_chr_1 for project 2 undergrad for-credit data\n'
                             '4) hw2grad_M_1_chr_1 for project 2 grad for-credit data\n')
    args = parser.parse_args()
    reference_fn = args.reference_file
    reads_fn = args.reads_file

    input_reads = parse_reads_file(reads_fn)
    if input_reads is None:
        sys.exit(1)
    reference = parse_ref_file(reference_fn)
    if reference is None:
        sys.exit(1)

    """
        TODO: Call functions to do the actual read alignment here

    """

    # using HW1 code to start off

    ###### STEP 1: CREATE AN INDEX FOR THE GENOME ######
    # reference_index maps each 1/3 of a kmer in the reference genome to its index
    reference_index = index_genome(reference)

    ###### STEP 2: CONVERT FROM READ-PAIRS TO SINGLE READS ######
    # in order to avoid issues with variable length read pairs, we will
    # consider each part of the read pair as its own independent read
    # therefore, we "flatten" the input_reads list so each read is its own entry
    input_reads = [read for read_pair in input_reads for read in read_pair]

    ###### STEP 3: BREAK DOWN READS INTO SMALLER K-MERS ######
    # currently, our reads are 50-mers
    # we will use k = KMER_SIZE to break them down into KMER_SIZE-mers
    kmers = break_into_kmers(input_reads)

    ###### STEP 4: REMOVE INFREQUENT KMERS ######
    # any kmer with low frequency has a high probability of being erroneous

    # first, map each kmer to the amount of times it occurs
    kmer_to_frequency = get_kmer_frequencies(kmers)

    # then, remove any kmers with a frequency <= 1 - we assume they're erroneous
    kmer_to_frequency = {kmer: freq for kmer, freq in kmer_to_frequency.items() if freq > 1}

    # now, we ignore the frequencies for the following reason:
    # any kmer has a frequency of at least 2, so it will always outnumber the reference genome
    # so we convert from dictionary back into a list of kmers
    kmers = list(kmer_to_frequency.keys())

    ###### STEP 5: USE HASHING ALGORITHM TO FIND SNPS ######
    snps = get_snps(kmers, reference_index, reference)


    #snps = [['A', 'G', 3425]]
    insertions = [['ACGTA', 12434]]
    deletions = [['CACGG', 12]]

    output_fn = args.output_file
    zip_fn = output_fn + '.zip'
    with open(output_fn, 'w') as output_file:
        output_file.write('>' + args.output_header + '\n>SNP\n')
        for x in snps:
            output_file.write(','.join([str(u) for u in x]) + '\n')
        output_file.write('>INS\n')
        for x in insertions:
            output_file.write(','.join([str(u) for u in x]) + '\n')
        output_file.write('>DEL\n')
        for x in deletions:
            output_file.write(','.join([str(u) for u in x]) + '\n')
    with zipfile.ZipFile(zip_fn, 'w') as myzip:
        myzip.write(output_fn)
