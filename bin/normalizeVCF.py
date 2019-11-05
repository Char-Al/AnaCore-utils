#!/usr/bin/env python3
#
# Copyright (C) 2017 IUCT-O
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
__version__ = '1.4.0'
__email__ = 'escudie.frederic@iuct-oncopole.fr'
__status__ = 'prod'

import os
import sys
import logging
import argparse
from anacore.vcf import VCFIO, getAlleleRecord, HeaderInfoAttr
from anacore.sequenceIO import FastaIO


########################################################################
#
# FUNCTIONS
#
########################################################################
def getSeqByChr(genome_path):
    """
    Return by chromosome name the sequence of this chromosome.

    :param genome_path: Path to the genome file (format: fasta).
    :type genome_path: str
    :return: By chromosome name the sequence of this chromosome in uppercase.
    :rtype: dict
    """
    genome_by_chr = dict()
    FH_seq = FastaIO(genome_path)
    for record in FH_seq:
        genome_by_chr[record.id] = record.string.upper()
    FH_seq.close()
    return genome_by_chr


def normAndMove(genome_path, in_variant_file, out_variant_file, trace_unstandard):
    """
    Write in a new file the normalized version of each variant. The normalization constists in three steps:
      1- The variants with multiple alternative alleles are splitted in one record by alternative allele.
      2- In each allele the empty allele marker is replaced by a dot and alternative and reference allele are reduced to the minimal string (example: ATG/A becomes TG/. ; AAGC/ATAC becomes AG/TA.).
      3- The allele is replaced by the most upstream allele that can have the same alternative sequence (example: a deletion in homopolymer is moved to first nucleotid of this homopolymer).

    :param genome_path: Path to the genome file (format: fasta).
    :type genome_path: str
    :param in_variant_file: Path to the variants file (format: VCF).
    :type in_variant_file: str
    :param out_variant_file: Path to the normalized variants file (format: VCF).
    :type out_variant_file: str
    :param trace_unstandard: True if you want to keep the trace of the variant before standardization in INFO.
    :type trace_unstandard: bool
    """
    genome_by_chr = getSeqByChr(genome_path)
    with VCFIO(out_variant_file, "w") as FH_out:
        with VCFIO(in_variant_file) as FH_in:
            # Header
            FH_out.copyHeader(FH_in)
            if trace_unstandard:
                FH_out.info["UNSTD"] = HeaderInfoAttr("UNSTD", type="String", number="1", description="The variant id (chromosome:position=reference/alternative) before standardization.")
            FH_out.writeHeader()
            # Records
            for record in FH_in:
                curr_chrom = genome_by_chr[record.chrom]
                for alt_idx, alt in enumerate(record.alt):
                    alt_record = getAlleleRecord(FH_in, record, alt_idx)
                    if trace_unstandard:
                        alt_record.info["UNSTD"] = "{}:{}={}/{}".format(alt_record.chrom, alt_record.pos, alt_record.ref, "/".join(alt_record.alt))
                    FH_out.write(alt_record.getMostUpstream(curr_chrom))


def normOnly(in_variant_file, out_variant_file, trace_unstandard):
    """
    Write in a new file the normalized version of each variant. The normalization constists in two steps:
      1- The variants with multiple alternative alleles are splitted in one record by alternative allele.
      2- In each allele the empty allele marker is replaced by a dot and alternative and reference allele are reduced to the minimal string (example: ATG/A becomes TG/. ; AAGC/ATAC becomes AG/TA.).

    :param in_variant_file: Path to the variants file (format: VCF).
    :type in_variant_file: str
    :param out_variant_file: Path to the normalized variants file (format: VCF).
    :type out_variant_file: str
    :param trace_unstandard: True if you want to keep the trace of the variant before standardization in INFO.
    :type trace_unstandard: bool
    """
    with VCFIO(out_variant_file, "w") as FH_out:
        with VCFIO(in_variant_file) as FH_in:
            # Header
            FH_out.copyHeader(FH_in)
            if trace_unstandard:
                FH_out.info["UNSTD"] = HeaderInfoAttr("UNSTD", type="String", number="1", description="The variant id (chromosome:position=reference/alternative) before standardization.")
            FH_out.writeHeader()
            # Records
            for record in FH_in:
                for alt_idx, alt in enumerate(record.alt):
                    alt_record = getAlleleRecord(FH_in, record, alt_idx)
                    if trace_unstandard:
                        alt_record.info["UNSTD"] = "{}:{}={}/{}".format(alt_record.chrom, alt_record.pos, alt_record.ref, "/".join(alt_record.alt))
                    alt_record.normalizeSingleAllele()
                    FH_out.write(alt_record)


########################################################################
#
# MAIN
#
########################################################################
if __name__ == "__main__":
    # Manage parameters
    parser = argparse.ArgumentParser(description='Splits alternatives alleles of one variants in multi-lines and removes unecessary reference and alternative nucleotids and move indel to most upstream position.')
    parser.add_argument('-t', '--trace-unstandard', action='store_true', help='Use this option to add "UNSTD" tag in record INFO. This tag contains the trace of the variant before standardization: chromosome:position=reference/alternative.')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    group_input = parser.add_argument_group('Inputs')  # Inputs
    group_input.add_argument('-i', '--input-variants', required=True, help='The path to the variant file (format: VCF).')
    group_input.add_argument('-g', '--input-genome', help='Genome reference used in variant calling to produced the inputed VCF (format: fasta). With this option all the indel are moved at their maximum upstream. This is used only in comparison for amplicon analysis. Example with repeat: TGATCATGATGTC with variant ATG/. on position 9 becomes ATG/. on position 6. Example with shift: ATTCCTCAAATAAGATAT with variant AATAA/. on position 8 becomes AAATA/. on position 7.')
    group_output = parser.add_argument_group('Outputs')  # Outputs
    group_output.add_argument('-o', '--output-variants', required=True, help='The path to the outputted file (format: VCF).')
    args = parser.parse_args()

    # Logger
    logging.basicConfig(format='%(asctime)s -- [%(filename)s][pid:%(process)d][%(levelname)s] -- %(message)s')
    log = logging.getLogger(os.path.basename(__file__))
    log.setLevel(logging.INFO)
    log.info("Command: " + " ".join(sys.argv))

    # Process
    if args.input_genome is None:
        normOnly(args.input_variants, args.output_variants, args.trace_unstandard)
    else:
        normAndMove(args.input_genome, args.input_variants, args.output_variants, args.trace_unstandard)
    log.info("End of job")
