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
__email__ = 'frederic.escudie@iuct-oncopole.fr'
__status__ = 'prod'

import os
import sys
import uuid
import tempfile
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.abspath(os.path.dirname(CURRENT_DIR))
sys.path.append(LIB_DIR)
if os.getenv('PYTHONPATH') is None: os.environ['PYTHONPATH'] = LIB_DIR
else: os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + os.pathsep + LIB_DIR

from vcf import VCFRecord, VCFIO


########################################################################
#
# FUNCTIONS
#
########################################################################
class TestVCFIO(unittest.TestCase):
    def setUp(self):
        tmp_folder = tempfile.gettempdir()
        unique_id = str(uuid.uuid1())

        # Temporary files
        self.tmp_variants = os.path.join( tmp_folder, unique_id + ".vcf")

        # Create VCF
        spec_example = """##fileformat=VCFv4.2
##fileDate=20090805"
##source=myImputationProgramV3.1
##reference=file:///seq/references/1000GenomesPilot-NCBI36.fasta
##contig=<ID=20,length=62435964,assembly=B36,md5=f126cdf8a6e0c7f379d618ff66beb2da,species="Homo sapiens",taxonomy=x>
##phasing=partial
##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">
##INFO=<ID=AA,Number=1,Type=String,Description="Ancestral Allele">
##INFO=<ID=DB,Number=0,Type=Flag,Description="dbSNP membership, build 129">
##INFO=<ID=H2,Number=0,Type=Flag,Description="HapMap2 membership">
##FILTER=<ID=q10,Description="Quality below 10">
##FILTER=<ID=s50,Description="Less than 50% of samples have data">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
##FORMAT=<ID=HQ,Number=2,Type=Integer,Description="Haplotype Quality">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	NA00001	NA00002	NA00003
20	14370	rs6054257	G	A	29	PASS	NS=3;DP=14;AF=0.5;DB;H2	GT:GQ:DP:HQ	0|0:48:1:51,51	1|0:48:8:51,51	1/1:43:5:.,.
20	17330	.	T	A	3	q10	NS=3;DP=11;AF=0.017	GT:GQ:DP:HQ	0|0:49:3:58,50	0|1:3:5:65,3	0/0:41:3
20	1110696	rs6040355	A	G,T	67	PASS	NS=2;DP=10;AF=0.333,0.667;AA=T;DB	GT:GQ:DP:HQ	1|2:21:6:23,27	2|1:2:0:18,2	2/2:35:4
20	1230237	.	T	.	47	PASS	NS=3;DP=13;AA=T	GT:GQ:DP:HQ	0|0:54:7:56,60	0|0:48:4:51,51	0/0:61:2
20	1234567	microsat1	GTC	G,GTCT	50	PASS	NS=3;DP=9;AA=G	GT:GQ:DP	0/1:35:4	0/2:17:2	1/1:40:3"""
        with open(self.tmp_variants, "w") as FH_variants:
            FH_variants.write( spec_example )

    def testIter(self):
        with VCFIO(self.tmp_variants) as FH_vcf:
            # Header
            self.assertEqual( FH_vcf.samples, ["NA00001", "NA00002", "NA00003"] )
            self.assertEqual( sorted(list(FH_vcf.format.keys())), sorted(["GT", "GQ", "DP", "HQ"]) )
            self.assertEqual( sorted(list(FH_vcf.info.keys())), sorted(["NS", "DP", "AF", "AA", "DB", "H2"]) )
            # Records
            expected_records = ["20_14370_G_A", "20_17330_T_A", "20_1110696_A_G,T", "20_1230237_T_.", "20_1234567_GTC_G,GTCT"]
            readed_records = list()
            for variant in FH_vcf:
                readed_records.append(
                    "_".join([variant.chrom, str(variant.pos), variant.ref, ",".join(variant.alt)])
                )
            self.assertEqual( expected_records, readed_records )

    def tearDown(self):
        # Clean temporary files
        for curr_file in [self.tmp_variants]:
            if os.path.exists(curr_file):
                os.remove(curr_file)


class TestVCFRecord(unittest.TestCase):
    def setUp(self):
        tmp_folder = tempfile.gettempdir()
        unique_id = str(uuid.uuid1())

        # Temporary files
        self.tmp_variants = os.path.join( tmp_folder, unique_id + ".vcf")

        # AD, AF and DP evaluation
        self.freq_data = dict()
        self.freq_data["wout_spl_rAD_aAF"] = """##fileformat=VCFv4.0
##INFO=<ID=AD,Number=R,Type=Integer,Description="Allele Depth">
##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##INFO=<ID=expModel,Number=1,Type=String,Description="Expected model for variant">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT
11	1	wout_spl_rAD_aAF_1	A	T	29	PASS	expModel=model_0;AD=90,10;DP=100	.
11	2	wout_spl_rAD_aAF_2	A	T	29	PASS	expModel=model_0;AF=0.1;AD=90,10	.
11	3	wout_spl_rAD_aAF_3	A	T	29	PASS	expModel=model_0;AF=0.1;DP=100	.
11	1	wout_spl_rAD_aAF_4	A	T,G	29	PASS	expModel=model_1;AD=85,10,5;DP=100	.
11	2	wout_spl_rAD_aAF_5	A	T,G	29	PASS	expModel=model_1;AF=0.1,0.05;AD=85,10,5	.
11	3	wout_spl_rAD_aAF_6	A	T,G	29	PASS	expModel=model_1;AF=0.1,0.05;DP=100	."""
        self.freq_data["wout_spl_aAD_rAF"] = """##fileformat=VCFv4.0
##INFO=<ID=AD,Number=A,Type=Integer,Description="Allele Depth">
##INFO=<ID=AF,Number=R,Type=Float,Description="Allele Frequency">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##INFO=<ID=expModel,Number=1,Type=String,Description="Expected model for variant">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT
11	1	wout_spl_aAD_rAF_1	A	T	29	PASS	expModel=model_0;AD=10;DP=100	.
11	2	wout_spl_aAD_rAF_2	A	T	29	PASS	expModel=model_0;AF=0.9,0.1;AD=10	.
11	3	wout_spl_aAD_rAF_3	A	T	29	PASS	expModel=model_0;AF=0.9,0.1;DP=100	.
11	1	wout_spl_aAD_rAF_4	A	T,G	29	PASS	expModel=model_1;AD=10,5;DP=100	.
11	2	wout_spl_aAD_rAF_5	A	T,G	29	PASS	expModel=model_1;AF=0.85,0.1,0.05;AD=10,5	.
11	3	wout_spl_aAD_rAF_6	A	T,G	29	PASS	expModel=model_1;AF=0.85,0.1,0.05;DP=100	."""
        self.freq_data["one_spl_rAD_aAF"] = """##fileformat=VCFv4.0
##INFO=<ID=AD,Number=R,Type=Integer,Description="Allele Depth">
##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##INFO=<ID=expModel,Number=1,Type=String,Description="Expected model for variant">
##INFO=<ID=skipAD,Number=1,Type=String,Description="Variant must be skipped by AD calculation">
##INFO=<ID=skipAF,Number=1,Type=String,Description="Variant must be skipped by AF calculation">
##INFO=<ID=skipDP,Number=1,Type=String,Description="Variant must be skipped by DP calculation">
##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	splA
11	1	one_spl_rAD_aAF_1	A	T	29	PASS	expModel=model_2;skipAF=True;AD=90,10;DP=100	.	.
11	2	one_spl_rAD_aAF_2	A	T	29	PASS	expModel=model_2;skipDP=True;AF=0.1;AD=90,10	.	.
11	3	one_spl_rAD_aAF_3	A	T	29	PASS	expModel=model_2;skipAD=True;AF=0.1;DP=100	.	.
11	1	one_spl_rAD_aAF_4	A	T	29	PASS	expModel=model_2	AD:DP	90,10:100
11	2	one_spl_rAD_aAF_5	A	T	29	PASS	expModel=model_2	AF:AD	0.1:90,10
11	3	one_spl_rAD_aAF_6	A	T	29	PASS	expModel=model_2	AF:DP	0.1:100
11	1	one_spl_rAD_aAF_7	A	T,G	29	PASS	expModel=model_3;skipAF=True;AD=85,10,5;DP=100	.	.
11	2	one_spl_rAD_aAF_8	A	T,G	29	PASS	expModel=model_3;skipDP=True;AF=0.1,0.05;AD=85,10,5	.	.
11	3	one_spl_rAD_aAF_9	A	T,G	29	PASS	expModel=model_3;skipAD=True;AF=0.1,0.05;DP=100	.	.
11	1	one_spl_rAD_aAF_10	A	T,G	29	PASS	expModel=model_3	AD:DP	85,10,5:100
11	2	one_spl_rAD_aAF_11	A	T,G	29	PASS	expModel=model_3	AF:AD	0.1,0.05:85,10,5
11	3	one_spl_rAD_aAF_12	A	T,G	29	PASS	expModel=model_3	AF:DP	0.1,0.05:100"""
        self.freq_data["one_spl_aAD_rAF"] = """##fileformat=VCFv4.0
##INFO=<ID=AD,Number=A,Type=Integer,Description="Allele Depth">
##INFO=<ID=AF,Number=R,Type=Float,Description="Allele Frequency">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##INFO=<ID=expModel,Number=1,Type=String,Description="Expected model for variant">
##INFO=<ID=skipAD,Number=1,Type=String,Description="Variant must be skipped by AD calculation">
##INFO=<ID=skipAF,Number=1,Type=String,Description="Variant must be skipped by AF calculation">
##INFO=<ID=skipDP,Number=1,Type=String,Description="Variant must be skipped by DP calculation">
##FORMAT=<ID=AD,Number=A,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=AF,Number=R,Type=Float,Description="Allele Frequency">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	splA
11	1	one_spl_aAD_rAF_1	A	T	29	PASS	expModel=model_2;skipAF=True;AD=10;DP=100	.	.
11	2	one_spl_aAD_rAF_2	A	T	29	PASS	expModel=model_2;skipDP=True;AF=0.9,0.1;AD=10	.	.
11	3	one_spl_aAD_rAF_3	A	T	29	PASS	expModel=model_2;skipAD=True;AF=0.9,0.1;DP=100	.	.
11	1	one_spl_aAD_rAF_4	A	T	29	PASS	expModel=model_2	AD:DP	10:100
11	2	one_spl_aAD_rAF_5	A	T	29	PASS	expModel=model_2	AF:AD	0.9,0.1:10
11	3	one_spl_aAD_rAF_6	A	T	29	PASS	expModel=model_2	AF:DP	0.9,0.1:100
11	1	one_spl_rAD_aAF_7	A	T,G	29	PASS	expModel=model_3;skipAF=True;AD=10,5;DP=100	.	.
11	2	one_spl_rAD_aAF_8	A	T,G	29	PASS	expModel=model_3;skipDP=True;AF=0.85,0.1,0.05;AD=10,5	.	.
11	3	one_spl_rAD_aAF_9	A	T,G	29	PASS	expModel=model_3;skipAD=True;AF=0.85,0.1,0.05;DP=100	.	.
11	1	one_spl_rAD_aAF_10	A	T,G	29	PASS	expModel=model_3	AD:DP	10,5:100
11	2	one_spl_rAD_aAF_11	A	T,G	29	PASS	expModel=model_3	AF:AD	0.85,0.1,0.05:10,5
11	3	one_spl_rAD_aAF_12	A	T,G	29	PASS	expModel=model_3	AF:DP	0.85,0.1,0.05:100"""
        self.freq_data["two_spl_rAD_aAF"] = """##fileformat=VCFv4.0
##INFO=<ID=AD,Number=A,Type=Integer,Description="Allele Depth">
##INFO=<ID=AF,Number=R,Type=Float,Description="Allele Frequency">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##INFO=<ID=expModel,Number=1,Type=String,Description="Expected model for variant">
##INFO=<ID=skipAD,Number=1,Type=String,Description="Variant must be skipped by AD calculation">
##INFO=<ID=skipAF,Number=1,Type=String,Description="Variant must be skipped by AF calculation">
##INFO=<ID=skipDP,Number=1,Type=String,Description="Variant must be skipped by DP calculation">
##FORMAT=<ID=AD,Number=A,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=AF,Number=R,Type=Float,Description="Allele Frequency">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	splA	splB
11	1	two_spl_rAD_aAF_1	A	T	29	PASS	expModel=model_4	AD:DP	48,2:50	42,8:50
11	2	two_spl_rAD_aAF_2	A	T	29	PASS	expModel=model_4	AF:AD	0.04:48,2	0.16:42,8
11	3	two_spl_rAD_aAF_3	A	T	29	PASS	expModel=model_4	AF:DP	0.04:50	0.16:50
11	1	two_spl_rAD_aAF_4	A	T,G	29	PASS	expModel=model_5	AD:DP	43,2,5:50	41,8,1:50
11	2	two_spl_rAD_aAF_5	A	T,G	29	PASS	expModel=model_5	AF:AD	0.04,0.1:43,2,5	0.16,0.02:41,8,1
11	3	two_spl_rAD_aAF_6	A	T,G	29	PASS	expModel=model_5	AF:DP	0.04,0.1:50	0.16,0.02:50"""
        self.freq_data["two_spl_aAD_rAF"] = """##fileformat=VCFv4.0
##INFO=<ID=AD,Number=A,Type=Integer,Description="Allele Depth">
##INFO=<ID=AF,Number=R,Type=Float,Description="Allele Frequency">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##INFO=<ID=expModel,Number=1,Type=String,Description="Expected model for variant">
##INFO=<ID=skipAD,Number=1,Type=String,Description="Variant must be skipped by AD calculation">
##INFO=<ID=skipAF,Number=1,Type=String,Description="Variant must be skipped by AF calculation">
##INFO=<ID=skipDP,Number=1,Type=String,Description="Variant must be skipped by DP calculation">
##FORMAT=<ID=AD,Number=A,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=AF,Number=R,Type=Float,Description="Allele Frequency">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	splA	splB
11	1	two_spl_rAD_aAF_1	A	T	29	PASS	expModel=model_4	AD:DP	2:50	8:50
11	2	two_spl_rAD_aAF_2	A	T	29	PASS	expModel=model_4	AF:AD	0.96,0.04:2	0.84,0.16:8
11	3	two_spl_rAD_aAF_3	A	T	29	PASS	expModel=model_4	AF:DP	0.96,0.04:50	0.84,0.16:50
11	1	two_spl_rAD_aAF_4	A	T,G	29	PASS	expModel=model_5	AD:DP	2,5:50	8,1:50
11	2	two_spl_rAD_aAF_5	A	T,G	29	PASS	expModel=model_5	AF:AD	0.96,0.04,0.1:2,5	0.84,0.16,0.02:8,1
11	3	two_spl_rAD_aAF_6	A	T,G	29	PASS	expModel=model_5	AF:DP	0.96,0.04,0.1:50	0.84,0.16,0.02:50"""
        self.freq_expected = {
            "model_0": {
                "AF": {"pop":[0.1]},
                "AD": {"pop":[10]},
                "DP": {"pop":100}
            },
            "model_1": {
                "AF": {"pop":[0.1, 0.05]},
                "AD": {"pop":[10, 5]},
                "DP": {"pop":100}
            },
            "model_2": {
                "AF": {"splA":[0.1], "pop":[0.1]},
                "AD": {"splA":[10], "pop":[10]},
                "DP": {"splA":100, "pop":100}
            },
            "model_3": {
                "AF": {"splA":[0.1, 0.05], "pop":[0.1, 0.05]},
                "AD": {"splA":[10, 5], "pop":[10, 5]},
                "DP": {"splA":100, "pop":100}
            },
            "model_4": {
                "AF": {"splA":[0.04], "splB":[0.16], "pop":[0.1]},
                "AD": {"splA":[2], "splB":[8], "pop":[10]},
                "DP": {"splA":50, "splB":50, "pop":100}
            },
            "model_5": {
                "AF": {"splA":[0.04, 0.1], "splB":[0.16, 0.02], "pop":[0.1, 0.06]},
                "AD": {"splA":[2, 5], "splB":[8, 1], "pop":[10, 6]},
                "DP": {"splA":50, "splB":50, "pop":100}
            }
        }

    def tearDown(self):
        # Clean temporary files
        for curr_file in [self.tmp_variants]:
            if os.path.exists(curr_file):
                os.remove(curr_file)

    def testGetAF(self):
        for curr_dataset in sorted(self.freq_data):
            if not curr_dataset.startswith("wout_spl"):
                # Write test data
                content = self.freq_data[curr_dataset]
                with open(self.tmp_variants, "w") as FH_variants:
                    FH_variants.write( content )
                # Parse
                expected_records = list()
                observed_records = list()
                with VCFIO(self.tmp_variants) as FH_vcf:
                    for variant in FH_vcf:
                        if "skipAF" not in variant.info:
                            try:
                                for idx_spl, curr_spl in enumerate(FH_vcf.samples):
                                    expected_AF = self.freq_expected[variant.info["expModel"]]["AF"][curr_spl]
                                    expected_records.append( "{} {}".format(variant.id, expected_AF) )
                                    observed_records.append( "{} {}".format(variant.id, variant.getAF(curr_spl)) )
                            except:
                                raise Exception('Error in TestVCFRecord.testGetAF() for variant "' + variant.id + '".')
                # Assert
                self.assertEqual( expected_records, observed_records )

    def testGetAD(self):
        for curr_dataset in sorted(self.freq_data):
            if not curr_dataset.startswith("wout_spl"):
                # Write test data
                content = self.freq_data[curr_dataset]
                with open(self.tmp_variants, "w") as FH_variants:
                    FH_variants.write( content )
                # Parse
                expected_records = list()
                observed_records = list()
                with VCFIO(self.tmp_variants) as FH_vcf:
                    for variant in FH_vcf:
                        if "skipAD" not in variant.info:
                            try:
                                for idx_spl, curr_spl in enumerate(FH_vcf.samples):
                                    expected_AD = self.freq_expected[variant.info["expModel"]]["AD"][curr_spl]
                                    expected_records.append( "{} {}".format(variant.id, expected_AD) )
                                    observed_records.append( "{} {}".format(variant.id, variant.getAD(curr_spl)) )
                            except:
                                raise Exception('Error in TestVCFRecord.testGetAD() for variant "' + variant.id + '".')
                # Assert
                self.assertEqual( expected_records, observed_records )

    def testGetDP(self):
        for curr_dataset in sorted(self.freq_data):
            if not curr_dataset.startswith("wout_spl"):
                # Write test data
                content = self.freq_data[curr_dataset]
                with open(self.tmp_variants, "w") as FH_variants:
                    FH_variants.write( content )
                # Parse
                expected_records = list()
                observed_records = list()
                with VCFIO(self.tmp_variants) as FH_vcf:
                    for variant in FH_vcf:
                        if "skipDP" not in variant.info:
                            try:
                                for curr_spl in FH_vcf.samples:
                                    expected_DP = self.freq_expected[variant.info["expModel"]]["DP"][curr_spl]
                                    expected_records.append( "{} {}".format(variant.id, expected_DP) )
                                    observed_records.append( "{} {}".format(variant.id, variant.getDP(curr_spl)) )
                            except:
                                raise Exception('Error in TestVCFRecord.testGetDP() for variant "' + variant.id + '".')
                # Assert
                self.assertEqual( expected_records, observed_records )

    def testGetPopAD(self):
        for curr_dataset in sorted(self.freq_data):
            # Write test data
            content = self.freq_data[curr_dataset]
            with open(self.tmp_variants, "w") as FH_variants:
                FH_variants.write( content )
            # Parse
            expected_records = list()
            observed_records = list()
            with VCFIO(self.tmp_variants) as FH_vcf:
                for variant in FH_vcf:
                    try:
                        expected_AD = self.freq_expected[variant.info["expModel"]]["AD"]["pop"]
                        expected_records.append( "{} {}".format(variant.id, expected_AD) )
                        observed_records.append( "{} {}".format(variant.id, variant.getPopAD()) )
                    except:
                        raise Exception('Error in TestVCFRecord.testGetPopAD() for variant "' + variant.id + '".')
            # Assert
            self.assertEqual( expected_records, observed_records )

    def testGetPopAF(self):
        for curr_dataset in sorted(self.freq_data):
            # Write test data
            content = self.freq_data[curr_dataset]
            with open(self.tmp_variants, "w") as FH_variants:
                FH_variants.write( content )
            # Parse
            expected_records = list()
            observed_records = list()
            with VCFIO(self.tmp_variants) as FH_vcf:
                for variant in FH_vcf:
                    try:
                        expected_AF = self.freq_expected[variant.info["expModel"]]["AF"]["pop"]
                        expected_records.append( "{} {}".format(variant.id, expected_AF) )
                        observed_records.append( "{} {}".format(variant.id, variant.getPopAF()) )
                    except:
                        raise Exception('Error in TestVCFRecord.testGetPopAF() for variant "' + variant.id + '".')
            # Assert
            self.assertEqual( expected_records, observed_records )

    def testGetPopDP(self):
        for curr_dataset in sorted(self.freq_data):
            # Write test data
            content = self.freq_data[curr_dataset]
            with open(self.tmp_variants, "w") as FH_variants:
                FH_variants.write( content )
            # Parse
            expected_records = list()
            observed_records = list()
            with VCFIO(self.tmp_variants) as FH_vcf:
                for variant in FH_vcf:
                    try:
                        expected_DP = self.freq_expected[variant.info["expModel"]]["DP"]["pop"]
                        expected_records.append( "{} {}".format(variant.id, expected_DP) )
                        observed_records.append( "{} {}".format(variant.id, variant.getPopDP()) )
                    except:
                        raise Exception('Error in TestVCFRecord.testGetPopDP() for variant "' + variant.id + '".')
            # Assert
            self.assertEqual( expected_records, observed_records )

    def testStandardizeSingleAllele(self):
        # Test substitution one nt
        substitution = VCFRecord( "artificial_1", 18, None, "TC", ["TA"], 230 )
        substitution.standardizeSingleAllele()
        self.assertTrue( substitution.ref == "C" and substitution.alt[0] == "A" and substitution.pos == 19 )
        # Test substitution multi nt
        substitution = VCFRecord( "artificial_1", 18, None, "TCtgA", ["TaGCc"], 230 )
        substitution.standardizeSingleAllele()
        self.assertTrue( substitution.ref == "CTGA" and substitution.alt[0] == "AGCC" and substitution.pos == 19 )
        # Test substitution multi nt with possible remove
        substitution = VCFRecord( "artificial_1", 18, None, "TCtgATT", ["TaGGctT"], 230 )
        substitution.standardizeSingleAllele()
        self.assertTrue( substitution.ref == "CTGA" and substitution.alt[0] == "AGGC" and substitution.pos == 19 )

        # Test insertion
        insertion = VCFRecord( "artificial_1", 18, None, "T", ["TA"], 230 )
        insertion.standardizeSingleAllele()
        self.assertTrue( insertion.ref == "." and insertion.alt[0] == "A" and insertion.pos == 19 )
        # Test insertion multi nt and remove upstream and downstream
        insertion = VCFRecord( "artificial_1", 18, None, "TGAT", ["TCGAGAT"], 230 )
        insertion.standardizeSingleAllele()
        self.assertTrue( insertion.ref == "." and insertion.alt[0] == "CGA" and insertion.pos == 19 )
        # Test insertion multi nt with possible remove and downstream and without complete standardization
        insertion = VCFRecord( "artificial_1", 18, None, "TCtgATTAGC", ["TaGGctTATGCGC"], 230 )
        insertion.standardizeSingleAllele()
        self.assertTrue( insertion.ref == "CTGATTA" and insertion.alt[0] == "AGGCTTATGC" and insertion.pos == 19 )

        # Test deletion
        insertion = VCFRecord( "artificial_1", 18, None, "TA", ["T"], 230 )
        insertion.standardizeSingleAllele()
        self.assertTrue( insertion.ref == "A" and insertion.alt[0] == "." and insertion.pos == 19 )
        # Test insertion multi nt and remove upstream and downstream
        insertion = VCFRecord( "artificial_1", 18, None, "TCGAGAT", ["TGAT"], 230 )
        insertion.standardizeSingleAllele()
        self.assertTrue( insertion.ref == "CGA" and insertion.alt[0] == "." and insertion.pos == 19 )
        # Test insertion multi nt with possible remove and downstream and without complete standardization
        insertion = VCFRecord( "artificial_1", 18, None, "TaGGctTATGCGC", ["TCtgATTAGC"], 230 )
        insertion.standardizeSingleAllele()
        self.assertTrue( insertion.ref == "AGGCTTATGC" and insertion.alt[0] == "CTGATTA" and insertion.pos == 19 )

    def testGetMostUpstream(self):
        ref = "nnNNATGCCAaTgATGTTtTaAGCCGAGCCGAT" # length: 33
        # Test fix deletion
        deletion = VCFRecord( "artificial_1", 18, None, "TtTaAGC", ["T"], 230 )
        upstream = deletion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 19 and upstream.ref == "TTAAGC" and upstream.alt[0] == "." )
        # Test homopolymer deletion
        deletion = VCFRecord( "artificial_1", 18, None, "TTT", ["T"], 230 )
        upstream = deletion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 17 and upstream.ref == "TT" and upstream.alt[0] == "." )
        # Test complex deletion
        deletion = VCFRecord( "artificial_1", 25, None, "CGAgCC", ["C"], 230 )
        upstream = deletion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 22 and upstream.ref == "AGCCG" and upstream.alt[0] == "." )
        # Test deletion on start
        deletion = VCFRecord( "artificial_1", 1, None, ref[0], ["."], 230 )
        upstream = deletion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 1 and upstream.ref == "N" and upstream.alt[0] == "." )
        # Test deletion on end
        deletion = VCFRecord( "artificial_1", len(ref) - 1, None, ref[-2:], [ref[-2]], 230 )
        upstream = deletion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 33 and upstream.ref == "T" and upstream.alt[0] == "." )
        # Test fix insertion
        insertion = VCFRecord( "artificial_1", 4, None, "N", ["NGGTT"], 230 )
        upstream = insertion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 5 and upstream.ref == "." and upstream.alt[0] == "GGTT" )
        # Test homopolymer insertion
        insertion = VCFRecord( "artificial_1", 18, None, "T", ["TT"], 230 )
        upstream = insertion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 17 and upstream.ref == "." and upstream.alt[0] == "T" )
        # Test complex insertion
        insertion = VCFRecord( "artificial_1", 25, None, "C", ["CGAgCC"], 230 )
        upstream = insertion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 22 and upstream.ref == "." and upstream.alt[0] == "AGCCG" )
        # Test insertion on start
        insertion = VCFRecord( "artificial_1", 1, None, ".", ["A"], 230 )
        upstream = insertion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 1 and upstream.ref == "." and upstream.alt[0] == "A" )
        # Test insertion on end
        insertion = VCFRecord( "artificial_1", len(ref), None, ref[-1], [ref[-1] + "G"], 230 )
        upstream = insertion.getMostUpstream( ref )
        self.assertTrue( upstream.pos == 34 and upstream.ref == "." and upstream.alt[0] == "G" )

    def testGetMostDownstream(self):
        ref = "nnNNATGCCAaTgATGTTtTaAGCCGAGCCGAT" # length: 33
        # Test fix deletion
        deletion = VCFRecord( "artificial_1", 18, None, "TtTaAGC", ["T"], 230 )
        downstream = deletion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 19 and downstream.ref == "TTAAGC" and downstream.alt[0] == "." )
        # Test homopolymer deletion
        deletion = VCFRecord( "artificial_1", 18, None, "TTT", ["T"], 230 )
        downstream = deletion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 19 and downstream.ref == "TT" and downstream.alt[0] == "." )
        # Test complex deletion
        deletion = VCFRecord( "artificial_1", 25, None, "CGAgCC", ["C"], 230 )
        downstream = deletion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 28 and downstream.ref == "GCCGA" and downstream.alt[0] == "." )
        # Test deletion on start
        deletion = VCFRecord( "artificial_1", 1, None, ref[0], ["."], 230 )
        downstream = deletion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 4 and downstream.ref == "N" and downstream.alt[0] == "." )
        # Test deletion on end
        deletion = VCFRecord( "artificial_1", len(ref) - 1, None, ref[-2:], [ref[-2]], 230 )
        downstream = deletion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 33 and downstream.ref == "T" and downstream.alt[0] == "." )
        # Test fix insertion
        insertion = VCFRecord( "artificial_1", 4, None, "N", ["NGGTT"], 230 )
        downstream = insertion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 5 and downstream.ref == "." and downstream.alt[0] == "GGTT" )
        # Test homopolymer insertion
        insertion = VCFRecord( "artificial_1", 18, None, "T", ["TT"], 230 )
        downstream = insertion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 21 and downstream.ref == "." and downstream.alt[0] == "T" )
        # Test complex insertion
        insertion = VCFRecord( "artificial_1", 25, None, "C", ["CGAgCC"], 230 )
        downstream = insertion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 33 and downstream.ref == "." and downstream.alt[0] == "GCCGA" )
        # Test insertion on start
        insertion = VCFRecord( "artificial_1", 1, None, ".", ["A"], 230 )
        downstream = insertion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 1 and downstream.ref == "." and downstream.alt[0] == "A" )
        # Test insertion on end
        insertion = VCFRecord( "artificial_1", len(ref), None, ref[-1], [ref[-1] + "G"], 230 )
        downstream = insertion.getMostDownstream( ref )
        self.assertTrue( downstream.pos == 34 and downstream.ref == "." and downstream.alt[0] == "G" )


########################################################################
#
# MAIN
#
########################################################################
if __name__ == "__main__":
    unittest.main()
