import sys
import argparse
import time
import zipfile

KMER_SIZE = 25
ERROR_THRESHOLD = 3

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

# slides a kmer along the reference genome and returns the section
# of the genome that has <= ERROR_THRESHOLD differences from the kmer
# return value: (genome section, starting index)
# returns (None, None) if no match exists
def find_kmer_match(kmer, reference):
    for i in range(len(reference) - len(kmer) + 1):
        # get the current piece of the genome
        curr_section = reference[i:(i + KMER_SIZE)]

        # get the amount of mismatches between the current section and the kmer
        num_mismatches = sum(kmer[j] != curr_section[j] for j in range(KMER_SIZE))

        # if the number of mismatches is below the threshold
        if num_mismatches <= ERROR_THRESHOLD:
            # then we consider it a match
            return (curr_section, i) # return the starting index of the current section

    return (None, None)

# returns the SNPs for the provided kmer, piece of the reference genome, and start index of the reference piece
def get_snps_for_kmer(kmer, reference_match, match_start_index):
    kmer_snps = []

    for i in range(KMER_SIZE):
        kmer_base = kmer[i]
        reference_base = reference_match[i]

        # if the kmer base differs from the reference genome base
        if kmer_base != reference_base:
            # we found an SNP
            snp = [reference_base, kmer_base, (i + match_start_index)]
            # add it to result
            kmer_snps.append(snp)

    return kmer_snps

# returns the SNPs by comparing each kmer to the reference genome
# we assume a read matches if it differs with any section of the genome by '<= ERROR_THRESHOLD' bases
def get_snps(kmers, reference):

    # maps an index to the snp at that index
    indexToSNP = {}

    for kmer in kmers:

        # get the starting index of the matching section of the reference genome
        reference_match, match_start_index = find_kmer_match(kmer, reference)

        # continue if the kmer doesn't match up with any part of the genome
        if match_start_index == None:
            continue

        # get the SNPs for that specific kmer
        curr_snps = get_snps_for_kmer(kmer, reference_match, match_start_index)

        # append those to the rest of the SNPs (ignore duplicates)
        for snp in curr_snps:
            index = snp[2]
            if index not in indexToSNP:
                indexToSNP[index] = snp

    # return only the SNPs
    return list(indexToSNP.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='basic_aligner.py takes in data for homework assignment 1 consisting '
                                     'of a genome and a set of reads and aligns the reads to the reference genome, '
                                     'then calls SNPs based on this alignment')
    parser.add_argument('-g', '--referenceGenome', required=True, dest='reference_file',
                        help='File containing a reference genome.')
    parser.add_argument('-r', '--reads', required=True, dest='reads_file',
                        help='File containg sequencing reads.')
    parser.add_argument('-o', '--outputFile', required=True, dest='output_file',
                        help='Output file name.')
    parser.add_argument('-t', '--outputHeader', required=True, dest='output_header',
                        help='String that needs to be outputted on the first line of the output file so that the '
                             'online submission system recognizes which leaderboard this file should be submitted to.'
                             'This HAS to be practice_W_1_chr_1 for the practice data and hw1_W_2_chr_1 for the '
                             'for-credit assignment!')
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

    ###### STEP 1: CONVERT FROM READ-PAIRS TO SINGLE READS ######
    # in order to avoid issues with variable length read pairs, we will
    # consider each part of the read pair as its own independent read
    # therefore, we "flatten" the input_reads list so each read is its own entry
    input_reads = [read for read_pair in input_reads for read in read_pair]

    ###### STEP 2: BREAK DOWN READS INTO SMALLER K-MERS ######
    # currently, our reads are 50-mers
    # we will use k = KMER_SIZE to break them down into KMER_SIZE-mers
    kmers = break_into_kmers(input_reads, KMER_SIZE)

    ###### STEP 3: REMOVE INFREQUENT KMERS ######
    # any kmer with low frequency has a high probability of being erroneous

    # first, map each kmer to the amount of times it occurs
    kmer_to_frequency = get_kmer_frequencies(kmers)

    # then, remove any kmers with a frequency <= 1 - we assume they're erroneous
    kmer_to_frequency = {kmer: freq for kmer, freq in kmer_to_frequency.items() if freq > 1}

    # now, we ignore the frequencies for the following reason:
    # any kmer has a frequency of at least 2, so it will always beat the reference genome in the consensus algorithm
    # so we convert from dictionary back into a list of kmers
    kmers = list(kmer_to_frequency.keys())

    ###### STEP 3: USE CONSENSUS MAPPING ALGORITHM TO FIND SNPS ######
    # Note: we will use a threshold of ERROR_THRESHOLD mismatches for matching up reads to the reference genome
    # (if a read has at most ERROR_THRESHOLD differences with a section of the genome, we consider it a match)
    snps = get_snps(kmers, reference)

    #snps = [['A', 'G', 3425]]

    output_fn = args.output_file
    zip_fn = output_fn + '.zip'
    with open(output_fn, 'w') as output_file:
        header = '>' + args.output_header + '\n>SNP\n'
        output_file.write(header)
        for x in snps:
            line = ','.join([str(u) for u in x]) + '\n'
            output_file.write(line)

        tails = ('>' + x for x in ('STR', 'CNV', 'ALU', 'INV', 'INS', 'DEL'))
        output_file.write('\n'.join(tails))

    with zipfile.ZipFile(zip_fn, 'w') as myzip:
        myzip.write(output_fn)
