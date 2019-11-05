#!/usr/bin/env python3
#
# Copyright (C) 2017 IUCT
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'Frederic Escudie'
__copyright__ = 'Copyright (C) 2017 IUCT-O'
__license__ = 'GNU General Public License'
__version__ = '1.2.0'
__email__ = 'escudie.frederiic@iuct-oncopole.fr'
__status__ = 'prod'

import os
import sys
import time
import random
import logging
import argparse
from anacore.sequenceIO import FastqIO, SequenceFileReader


########################################################################
#
# FUNCTIONS
#
########################################################################
def getQualities(fastq_files):
    """
    Return a random list of qualities extract from one or several fastq files.

    :param fastq_files: The paths of the fastq files.
    :type fastq_files: list
    :return: Each element is a quality string extracted from one sequence of the fastq.
    :rtype: list
    """
    qualities = list()
    for current_fastq in fastq_files:
        FH_fastq = FastqIO(current_fastq)
        for record in FH_fastq:
            qualities.append(record.quality)
        FH_fastq.close()
    random.shuffle(qualities)
    return(qualities)


########################################################################
#
# MAIN
#
########################################################################
if __name__ == "__main__":
    # Manage parameters
    parser = argparse.ArgumentParser(description='Apply qualities profile extract from existing FASTQ on sequences.')
    parser.add_argument('-r', '--random-seed', type=int, default=int(time.time()), help="The seed used for the random generator. If you want reproduce results of one execution: use the same parameters AND the same random-seed. [Default: auto]")
    parser.add_argument('-a', '--sequences-alphabet', nargs='+', default=["A", "T", "G", "C"], help="The alphabet of the input sequences. [Default: %(default)s]")
    parser.add_argument('-q', '--qual-offset', type=int, default=33, help="The position of the first quality encoding character in ASCII table (example: 33 for Illumina 1.8+). [Default: %(default)s]")
    parser.add_argument('-p', '--qual-penalty', type=int, default=0, help="The penalty applied to reduce the quality of the sequences produced. With 2, the quality of each base is decrease of 2 compared to the model. [Default: %(default)s]")
    parser.add_argument('-l', '--reads-length', type=int, help="If this option is used, the reads smaller than this are completed by random nucleotids with a minimal quality. This function simulate the noise coming from neighbors clusters on flowcell when sequenced the fragment is too small.")
    parser.add_argument('-v', '--version', action='version', version=__version__)
    group_input = parser.add_argument_group('Inputs')  # Inputs
    group_input.add_argument('-m', '--input-models', required=True, nargs='+', help='The paths of the sequences files used to retrieve the error model from qualities (format: fastq). The sequences length must be at least the same as sequences provided by --input-sequences.')
    group_input.add_argument('-s', '--input-sequences', required=True, help='The path of the sequences file containing sequences that will be altered (format: fasta or fastq).')
    group_output = parser.add_argument_group('Outputs')  # Outputs
    group_output.add_argument('-o', '--output-sequences', required=True, help='The path of the file sequence file with alterations and qualities (format: fastq).')
    group_output.add_argument('-t', '--output-trace', required=True, help='The path of the file reporting the position and the nature of each variant introduced in sequences (format: TSV).')
    args = parser.parse_args()

    # Logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s -- [%(filename)s][pid:%(process)d][%(levelname)s] -- %(message)s')
    logger = logging.getLogger(os.path.basename(__file__))

    # Random seed
    random.seed(args.random_seed)
    logger.info("Random seed used: {}".format(args.random_seed))

    # Get quality model
    logger.info("START get qualities model.")
    qualities = getQualities(args.input_models)
    logger.info("END get qualities model.")

    # Apply model
    logger.info("START apply error model.")
    nb_qualities = len(qualities)
    idx_qual = 0
    FH_in_seq = SequenceFileReader.factory(args.input_sequences)
    FH_out_seq = FastqIO(args.output_sequences, "w")
    FH_out_trace = open(args.output_trace, "w")
    try:
        FH_out_trace.write("\t".join(["#Read_id", "Position", "Quality", "Ref", "Alt"]) + "\n")
        for record in FH_in_seq:
            # Get record quality
            record.quality = qualities[idx_qual][:len(record.string)]
            if args.qual_penalty > 0:
                new_record_qual = ""
                for curr_qual in record.quality:
                    new_nt_qual = max((2 + args.qual_offset), (ord(curr_qual) - args.qual_penalty))
                    new_record_qual += chr(new_nt_qual)
                record.quality = new_record_qual
            # Apply error rate in sequence
            new_seq = ""
            for idx_elt, elt in enumerate(record.string):  # For each position in sequence
                new_elt = elt
                elt_qual = ord(record.quality[idx_elt]) - args.qual_offset
                error_rate = 10**(-elt_qual / 10)
                if random.randint(1, 100000) <= error_rate * 100000:  # If the position has an error
                    choice_opt = [opt for opt in args.sequences_alphabet]
                    choice_opt.remove(new_elt.upper())
                    new_elt = random.choice(choice_opt)
                    FH_out_trace.write("\t".join([record.id, str(idx_elt + 1), str(elt_qual), elt, new_elt]) + "\n")
                new_seq += new_elt
            record.string = new_seq
            # Complete sequence
            if args.reads_length is not None and len(record.string) < args.reads_length:
                missing_length = args.reads_length - len(record.string)
                record.quality += "".join([chr(2 + args.qual_offset) for elt in range(missing_length)])
                record.string += "".join([random.choice(args.sequences_alphabet) for elt in range(missing_length)])
            # Write sequence
            FH_out_seq.write(record)
            # Next quality model
            idx_qual += 1
            if idx_qual >= nb_qualities:
                idx_qual = 0
    finally:
        FH_in_seq.close()
        FH_out_seq.close()
        FH_out_trace.close()
    logger.info("END apply error model.")
