#!/usr/bin/env python3

__author__ = 'Frederic Escudie'
__copyright__ = 'Copyright (C) 2019 IUCT-O'
__license__ = 'GNU General Public License'
__version__ = '1.0.0'
__email__ = 'escudie.frederic@iuct-oncopole.fr'
__status__ = 'prod'

import os
import uuid
import tempfile
import unittest
import subprocess
from anacore.vcf import VCFIO, VCFRecord, HeaderInfoAttr
from anacore.sequenceIO import FastaIO, Sequence

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(TEST_DIR)
BIN_DIR = os.path.join(APP_DIR, "bin")
os.environ['PATH'] = BIN_DIR + os.pathsep + os.environ['PATH']


########################################################################
#
# FUNCTIONS
#
########################################################################
class FilterVCFHomopolym(unittest.TestCase):
    def setUp(self):
        tmp_folder = tempfile.gettempdir()
        unique_id = str(uuid.uuid1())

        # Temporary files
        self.tmp_sequences = os.path.join(tmp_folder, unique_id + ".fasta")
        self.tmp_faidx = os.path.join(tmp_folder, unique_id + ".fasta.fai")
        self.tmp_variants = os.path.join(tmp_folder, unique_id + ".vcf")
        self.tmp_output = os.path.join(tmp_folder, unique_id + "_out.vcf")

        # Exec command
        self.cmd = [
            "filterVCFHomopolym.py",
            "--mode", "remove",
            "--homopolym-length", "4",
            "--input-variants", self.tmp_variants,
            "--input-reference", self.tmp_sequences,
            "--output-variants", self.tmp_output
        ]

        # Create fasta
        with FastaIO(self.tmp_sequences, "w") as FH_seq:
            #                                                    12  16  20  24  28  32  36  40  44  48  52  56  60  64  68  72  76  80  84  88  92  96  100
            #                                          2 4 6 8 10| 14| 18| 22| 26| 30| 34| 38| 42| 46| 50| 54| 58| 62| 66| 70| 74| 78| 82| 86| 90| 94| 98| 102
            #                                          | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
            FH_seq.write(Sequence("artificial_chr1", "CGAATATGATCCAGCAATAAAAAGTTCCTACAGGAAAAAAGTAGAAAGAGAAACCTGTCTCTTGGATATTCTCGACACAGCAGGTCAAG"))
            FH_seq.write(Sequence("artificial_chr2", "CGAATATGATCCAGCAATAAAAAGCTCCTACAGGCAAAAGTAGGCAAAGAGAAACCTGTCTCTTGGATATTCTCGACACAGCAGGTCAA"))
            FH_seq.write(Sequence("artificial_chr3", "CGAATATGATCCAGCAATGAAAATTCCTACAGGTAAAACGTAGAAAGAGAAACCTGTCTCTTGGATATTCTCGACACAGCAGGTCAAG"))
            FH_seq.write(Sequence("artificial_chr4", "CGAATATGATCCAGCAATAAAAAGTTCCTACAGGAAAAAAGTAGAAAGAGAAACCTGTCAAAAGGATATTCTCGACAAAACAGCAGAAAGTCAAG"))
            FH_seq.write(Sequence("artificial_chr5", "CGAATATGATCCAGTAATAAAAAGTTCCTACAGGAAAAAAGTAGAAAGAGAAACCTGTCTCTTGGATATTCTCGACACAGCAGGTCAAG"))
            FH_seq.write(Sequence("artificial_chr6", "CGAATATGATCCAGCAATAAAAAGTTCCTACAGGAAAAAAGTAGAAAGCACAACCTGTCTCTTGGAAAATCTCGACACAGCAGGTAAAACAATGCAGTAAAT"))
        """
        Variant	before_start	before_end	before_seq	after_start	after_end	after_seq
        alt_00	10	13	TCCA	15	18	CAAT
        alt_01	20	23	AAAA	25	28	TTCC
        alt_02	30	33	ACAG	35	38	AAAA
        alt_03	40	43	AGTA	45	48	AAAG
        alt_04	10	13	TCCA	16	19	AATA
        alt_05	20	23	AAAA	26	29	TCCT
        alt_06	30	33	ACAG	36	39	AAAA
        alt_07	40	43	GTAG	46	49	AAAG
        alt_08	11	14	CCAG	15	18	CAAT
        alt_09	20	23	AAAA	24	27	TTCC
        alt_10	31	34	AGGT	35	38	AAAA
        alt_11	40	43	GTAG	44	47	AAAG
        alt_12	11	14	CCAG	15	18	CAAT
        alt_13	20	23	AAAA	24	27	GTTC
        alt_14	31	34	CAGG	35	38	AAAA
        alt_15	41	44	GTAG	45	48	AAAG
        alt_16	50	53	GAAA	57	60	GTCA
        alt_17	60	63	AAAA	67	70	TATT
        alt_18	70	73	TCTC	77	80	AAAA
        alt_19	80	83	ACAG	87	90	AAAG
        alt_20	11	14	CCAG	16	19	AATA
        alt_21	20	23	AAAA	25	28	TTCC
        alt_22	31	34	CAGG	36	39	AAAA
        alt_23	40	43	AGTA	45	48	AAAG
        alt_24	11	14	CCAG	17	20	ATAA
        alt_25	19	22	AAAA	26	29	TCCT
        alt_26	29	32	TACA	35	38	AAAA
        alt_27	38	41	AAAG	45	48	AAAG
        alt_28	50	53	ACAA	61	64	CTTG
        alt_29	66	69	AAAA	76	79	CACA
        alt_30	76	79	CACA	86	89	AAAA
        alt_31	88	91	AACA	99	102	AAAT
        """

        # Create faidx
        with open(self.tmp_faidx, "w") as FH_fai:
            FH_fai.write("""artificial_chr1	89	17	89	90
artificial_chr2	89	124	89	90
artificial_chr3	88	231	88	89
artificial_chr4	95	337	95	96
artificial_chr5	89	450	89	90
artificial_chr6	102	557	102	103""")

        # Create VCF
        with VCFIO(self.tmp_variants, "w") as FH_var:
            FH_var.info = {"is_filtered": HeaderInfoAttr("is_filtered", "1 if the variant is adjacent to an homopolymer.", type="Integer", number="1")}
            FH_var.writeHeader()
            self.variants = [
                # Substit single nt
                VCFRecord("artificial_chr1", 14, "alt_00", "G", ["T"], None, None, {"is_filtered": 0}),  # Without adjacent homopolymers
                VCFRecord("artificial_chr1", 24, "alt_01", "G", ["T"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers upstream
                VCFRecord("artificial_chr1", 34, "alt_02", "G", ["T"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers downstream
                VCFRecord("artificial_chr1", 44, "alt_03", "G", ["T"], None, None, {"is_filtered": 0}),  # Adjacent too short homopolymers
                # Substit multi nt
                VCFRecord("artificial_chr2", 14, "alt_04", "GC", ["TA"], None, None, {"is_filtered": 0}),  # Without adjacent homopolymers
                VCFRecord("artificial_chr2", 24, "alt_05", "GC", ["TA"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers upstream
                VCFRecord("artificial_chr2", 34, "alt_06", "GC", ["TA"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers downstream
                VCFRecord("artificial_chr2", 44, "alt_07", "GC", ["TA"], None, None, {"is_filtered": 0}),  # Adjacent too short homopolymers
                # Ins single nt
                VCFRecord("artificial_chr3", 14, "alt_08", "G", ["GT"], None, None, {"is_filtered": 0}),  # Without adjacent homopolymers
                VCFRecord("artificial_chr3", 23, "alt_09", "A", ["AT"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers upstream
                VCFRecord("artificial_chr3", 34, "alt_10", "T", ["TA"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers downstream
                VCFRecord("artificial_chr3", 43, "alt_11", "G", ["GT"], None, None, {"is_filtered": 0}),  # Adjacent too short homopolymers
                # Ins multi nt
                VCFRecord("artificial_chr4", 14, "alt_12", "G", ["GTA"], None, None, {"is_filtered": 0}),  # Without adjacent homopolymers
                VCFRecord("artificial_chr4", 23, "alt_13", "A", ["ATA"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers upstream
                VCFRecord("artificial_chr4", 34, "alt_14", "G", ["GTA"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers downstream
                VCFRecord("artificial_chr4", 44, "alt_15", "G", ["GTC"], None, None, {"is_filtered": 0}),  # Adjacent too short homopolymer
                VCFRecord("artificial_chr4", 54, "alt_16", "CCT", ["ATCCAGA"], None, None, {"is_filtered": 0}),  # Without adjacent homopolymers
                VCFRecord("artificial_chr4", 64, "alt_17", "GGA", ["CTCCAGT"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers upstream
                VCFRecord("artificial_chr4", 74, "alt_18", "GAC", ["ATCCAGT"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers downstream
                VCFRecord("artificial_chr4", 84, "alt_19", "CAG", ["ATCCAGT"], None, None, {"is_filtered": 0}),  # Adjacent too short homopolymer
                # Del single nt
                VCFRecord("artificial_chr5", 14, "alt_20", "GT", ["G"], None, None, {"is_filtered": 0}),  # Without adjacent homopolymers
                VCFRecord("artificial_chr5", 23, "alt_21", "AG", ["A"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers upstream
                VCFRecord("artificial_chr5", 34, "alt_22", "GA", ["G"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers downstream
                VCFRecord("artificial_chr5", 43, "alt_23", "AG", ["A"], None, None, {"is_filtered": 0}),  # Adjacent too short homopolymers
                # # Del multi nt
                VCFRecord("artificial_chr6", 14, "alt_24", "GCA", ["G"], None, None, {"is_filtered": 0}),  # Without adjacent homopolymers
                VCFRecord("artificial_chr6", 23, "alt_25", "AGT", ["C"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers upstream
                VCFRecord("artificial_chr6", 32, "alt_26", "AGG", ["A"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers downstream
                VCFRecord("artificial_chr6", 42, "alt_27", "TAG", ["C"], None, None, {"is_filtered": 0}),  # Adjacent too short homopolymer
                VCFRecord("artificial_chr6", 54, "alt_28", "CCTGTCT", ["GAA"], None, None, {"is_filtered": 0}),  # Without adjacent homopolymers
                VCFRecord("artificial_chr6", 70, "alt_29", "TCTCGA", ["CCC"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers upstream
                VCFRecord("artificial_chr6", 80, "alt_30", "GCAGGT", ["CCC"], None, None, {"is_filtered": 1}),  # Adjacent homopolymers downstream
                VCFRecord("artificial_chr6", 92, "alt_31", "ATGCAGT", ["CCC"], None, None, {"is_filtered": 0}),  # Adjacent too short homopolymer
            ]
            for idx, curr_var in enumerate(self.variants):
                FH_var.write(curr_var)

    def tearDown(self):
        # Clean temporary files
        for curr_file in [self.tmp_sequences, self.tmp_faidx, self.tmp_variants, self.tmp_output]:
            if os.path.exists(curr_file):
                os.remove(curr_file)

    def testResults(self):
        # Execute command
        subprocess.check_call(self.cmd, stderr=subprocess.DEVNULL)

        # Validate results
        expected = [curr_var.id for curr_var in self.variants if curr_var.info["is_filtered"] == 0]
        observed = list()
        with VCFIO(self.tmp_output) as FH_results:
            for record in FH_results:
                observed.append(record.id)
        self.assertEqual(
            sorted(expected),
            sorted(observed)
        )


########################################################################
#
# MAIN
#
########################################################################
if __name__ == "__main__":
    unittest.main()
