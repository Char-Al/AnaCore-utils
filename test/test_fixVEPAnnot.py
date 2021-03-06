#!/usr/bin/env python3

__author__ = 'Frederic Escudie'
__copyright__ = 'Copyright (C) 2020 IUCT-O'
__license__ = 'GNU General Public License'
__version__ = '1.0.0'
__email__ = 'escudie.frederic@iuct-oncopole.fr'
__status__ = 'prod'

import os
import pysam
import subprocess
import tempfile
import unittest
import uuid

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(TEST_DIR)
BIN_DIR = os.path.join(APP_DIR, "bin")
os.environ['PATH'] = BIN_DIR + os.pathsep + os.environ['PATH']


########################################################################
#
# FUNCTIONS
#
########################################################################
class FixVEPAnnot(unittest.TestCase):
    def setUp(self):
        tmp_folder = tempfile.gettempdir()
        unique_id = str(uuid.uuid1())

        # Temporary files
        self.tmp_cosmic = os.path.join(tmp_folder, unique_id + "_db.vcf")
        self.tmp_cosmic_bz = os.path.join(tmp_folder, unique_id + "_db.vcf.gz")
        self.tmp_cosmic_index = os.path.join(tmp_folder, unique_id + "_db.vcf.gz.tbi")
        self.tmp_input = os.path.join(tmp_folder, unique_id + "_in.vcf")
        self.tmp_output = os.path.join(tmp_folder, unique_id + "_out.vcf")

        # Exec command
        self.cmd = [
            "fixVEPAnnot.py",
            "--annotations-field", "TESTANN",
            "--input-cosmic", self.tmp_cosmic_bz,
            "--input-variants", self.tmp_input,
            "--output-variants", self.tmp_output
        ]

        # Create db file
        content = """##fileformat=VCFv4.1
##source=COSMICv92
##reference=GRCh38
##fileDate=20200701
##INFO=<ID=GENE,Number=1,Type=String,Description="Gene name">
##INFO=<ID=STRAND,Number=1,Type=String,Description="Gene strand">
##INFO=<ID=GENOMIC_ID,Number=1,Type=String,Description="Genomic Mutation ID">
##INFO=<ID=LEGACY_ID,Number=1,Type=String,Description="Legacy Mutation ID">
##INFO=<ID=CDS,Number=1,Type=String,Description="CDS annotation">
##INFO=<ID=AA,Number=1,Type=String,Description="Peptide annotation">
##INFO=<ID=HGVSC,Number=1,Type=String,Description="HGVS cds syntax">
##INFO=<ID=HGVSP,Number=1,Type=String,Description="HGVS peptide syntax">
##INFO=<ID=HGVSG,Number=1,Type=String,Description="HGVS genomic syntax">
##INFO=<ID=CNT,Number=1,Type=Integer,Description="How many samples have this mutation">
##INFO=<ID=SNP,Number=0,Type=Flag,Description="classified as SNP">
##INFO=<ID=OLD_VARIANT,Number=.,Type=String,Description="Original chr:pos:ref:alt encoding">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
10	87933223	COSV64291751	A	G	.	.	GENE=PTEN;STRAND=+;LEGACY_ID=COSM5144;CDS=c.464A>G;AA=p.Y155C;HGVSC=ENST00000371953.7:c.464A>G;HGVSP=ENSP00000361021.3:p.Tyr155Cys;HGVSG=10:g.87933223A>G;CNT=15
10	87933223	COSV64292375	A	C	.	.	GENE=PTEN;STRAND=+;LEGACY_ID=COSM6492634;CDS=c.464A>C;AA=p.Y155S;HGVSC=ENST00000371953.7:c.464A>C;HGVSP=ENSP00000361021.3:p.Tyr155Ser;HGVSG=10:g.87933223A>C;CNT=1
10	87933224	COSV64303803	TG	T	.	.	GENE=PTEN;STRAND=+;LEGACY_ID=COSM5371246;CDS=c.469del;AA=p.E157Kfs*2;HGVSC=ENST00000371953.7:c.469del;HGVSP=ENSP00000361021.3:p.Glu157LysfsTer2;HGVSG=10:g.87933228del;CNT=2;OLD_VARIANT=10:87933227:GG/G
10	87933224	COSV64288964	T	TG	.	.	GENE=PTEN;STRAND=+;LEGACY_ID=COSM5002;CDS=c.469dup;AA=p.E157Gfs*23;HGVSC=ENST00000371953.7:c.469dup;HGVSP=ENSP00000361021.3:p.Glu157GlyfsTer23;HGVSG=10:g.87933228dup;CNT=10;OLD_VARIANT=10:87933228:G/GG
10	87933224	COSV64299113	T	TGG	.	.	GENE=PTEN;STRAND=+;LEGACY_ID=COSM6942459;CDS=c.468_469dup;AA=p.E157Gfs*3;HGVSC=ENST00000371953.7:c.468_469dup;HGVSP=ENSP00000361021.3:p.Glu157GlyfsTer3;HGVSG=10:g.87933227_87933228dup;CNT=2;OLD_VARIANT=10:87933228:G/GGG
10	87933225	COSV64288799	G	A	.	.	GENE=PTEN;STRAND=+;LEGACY_ID=COSM5103;CDS=c.466G>A;AA=p.G156R;HGVSC=ENST00000371953.7:c.466G>A;HGVSP=ENSP00000361021.3:p.Gly156Arg;HGVSG=10:g.87933225G>A;CNT=1
10	87933225	COSV64297412	G	T	.	.	GENE=PTEN;STRAND=+;LEGACY_ID=COSM6950506;CDS=c.466G>T;AA=p.G156W;HGVSC=ENST00000371953.7:c.466G>T;HGVSP=ENSP00000361021.3:p.Gly156Trp;HGVSG=10:g.87933225G>T;CNT=2
12	25245350	COSV55505818	CC	AA	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM512;CDS=c.34_35delinsTT;AA=p.G12F;HGVSC=ENST00000256078.8:c.34_35delinsTT;HGVSP=ENSP00000256078.4:p.Gly12Phe;HGVSG=12:g.25245350_25245351delinsAA;CNT=61;OLD_VARIANT=12:25245349:ACC/AAA
12	25245350	COSV55573070	CC	AG	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM514;CDS=c.34_35delinsCT;AA=p.G12L;HGVSC=ENST00000256078.8:c.34_35delinsCT;HGVSP=ENSP00000256078.4:p.Gly12Leu;HGVSG=12:g.25245350_25245351delinsAG;CNT=12;OLD_VARIANT=12:25245349:ACC/AAG
12	25245350	COSV55505818	CC	AA	.	.	GENE=KRAS_ENST00000311936;STRAND=-;LEGACY_ID=COSM512;CDS=c.34_35delinsTT;AA=p.G12F;HGVSC=ENST00000311936.7:c.34_35delinsTT;HGVSP=ENSP00000308495.3:p.Gly12Phe;HGVSG=12:g.25245350_25245351delinsAA;CNT=61;OLD_VARIANT=12:25245349:ACC/AAA
12	25245350	COSV55505818	CC	AA	.	.	GENE=KRAS_ENST00000556131;STRAND=-;LEGACY_ID=COSM512;CDS=c.34_35delinsTT;AA=p.G12F;HGVSC=ENST00000556131.1:c.34_35delinsTT;HGVSP=ENSP00000451856.1:p.Gly12Phe;HGVSG=12:g.25245350_25245351delinsAA;CNT=61;OLD_VARIANT=12:25245349:ACC/AAA
12	25245350	COSV55505818	CC	AA	.	.	GENE=KRAS_ENST00000557334;STRAND=-;LEGACY_ID=COSM512;CDS=c.34_35delinsTT;AA=p.G12F;HGVSC=ENST00000557334.5:c.34_35delinsTT;HGVSP=ENSP00000452512.1:p.Gly12Phe;HGVSG=12:g.25245350_25245351delinsAA;CNT=61;OLD_VARIANT=12:25245349:ACC/AAA
12	25245350	COSV55721374	CC	TT	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM13643;CDS=c.34_35delinsAA;AA=p.G12N;HGVSC=ENST00000256078.8:c.34_35delinsAA;HGVSP=ENSP00000256078.4:p.Gly12Asn;HGVSG=12:g.25245350_25245351delinsTT;CNT=2;OLD_VARIANT=12:25245349:ACC/ATT
12	25245350	COSV55518031	CC	TA	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM25081;CDS=c.34_35delinsTA;AA=p.G12Y;HGVSC=ENST00000256078.8:c.34_35delinsTA;HGVSP=ENSP00000256078.4:p.Gly12Tyr;HGVSG=12:g.25245350_25245351delinsTA;CNT=3;OLD_VARIANT=12:25245349:ACC/ATA
12	25245350	COSV55560425	CC	AT	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM34144;CDS=c.34_35delinsAT;AA=p.G12I;HGVSC=ENST00000256078.8:c.34_35delinsAT;HGVSP=ENSP00000256078.4:p.Gly12Ile;HGVSG=12:g.25245350_25245351delinsAT;CNT=8;OLD_VARIANT=12:25245349:ACC/AAT
12	25245350	COSV55870110	CC	TG	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM7335307;CDS=c.34_35delinsCA;AA=p.G12H;HGVSC=ENST00000256078.8:c.34_35delinsCA;HGVSP=ENSP00000256078.4:p.Gly12His;HGVSG=12:g.25245350_25245351delinsTG;CNT=1;OLD_VARIANT=12:25245349:ACC/ATG
12	25245350	COSV55632632	CCAGC	TCAGT	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM6948220;CDS=c.31_35delinsACTGA;AA=p.A11_G12delinsTD;HGVSC=ENST00000256078.8:c.31_35delinsACTGA;HGVSP=ENSP00000256078.4:p.Ala11_Gly12delinsThrAsp;HGVSG=12:g.25245350_25245354delinsTCAGT;CNT=1;OLD_VARIANT=12:25245349:ACCAGC/ATCAGT
12	25245350	COSV55528088	CC	GA	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM6959652;CDS=c.34_35delinsTC;AA=p.G12S;HGVSC=ENST00000256078.8:c.34_35delinsTC;HGVSP=ENSP00000256078.4:p.Gly12Ser;HGVSG=12:g.25245350_25245351delinsGA;CNT=1;OLD_VARIANT=12:25245349:ACC/AGA
12	25245350	COSV55497419	C	A	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM520;CDS=c.35G>T;AA=p.G12V;HGVSC=ENST00000256078.8:c.35G>T;HGVSP=ENSP00000256078.4:p.Gly12Val;HGVSG=12:g.25245350C>A;CNT=10787
12	25245350	COSV55726551	C	CT	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM5751774;CDS=c.34_35insA;AA=p.G12Efs*22;HGVSC=ENST00000256078.8:c.34_35insA;HGVSP=ENSP00000256078.4:p.Gly12GlufsTer22;HGVSG=12:g.25245350_25245351insT;CNT=1
12	25245350	COSV55497479	C	G	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM522;CDS=c.35G>C;AA=p.G12A;HGVSC=ENST00000256078.8:c.35G>C;HGVSP=ENSP00000256078.4:p.Gly12Ala;HGVSG=12:g.25245350C>G;CNT=2502
12	25245350	COSV55497369	C	T	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM521;CDS=c.35G>A;AA=p.G12D;HGVSC=ENST00000256078.8:c.35G>A;HGVSP=ENSP00000256078.4:p.Gly12Asp;HGVSG=12:g.25245350C>T;CNT=15834
12	25245350	COSV55556313	C	CCCA	.	.	GENE=KRAS;STRAND=-;LEGACY_ID=COSM6853641;CDS=c.34_35insTGG;AA=p.A11_G12insV;HGVSC=ENST00000256078.8:c.34_35insTGG;HGVSP=ENSP00000256078.4:p.Ala11_Gly12insVal;HGVSG=12:g.25245351_25245352insCAC;CNT=1;OLD_VARIANT=12:25245351:C/CCAC
17	60663077	COSV59954590	A	G	.	.	GENE=PPM1D;STRAND=+;LEGACY_ID=COSM301389;CDS=c.1343A>G;AA=p.N448S;HGVSC=ENST00000305921.7:c.1343A>G;HGVSP=ENSP00000306682.2:p.Asn448Ser;HGVSG=17:g.60663077A>G;CNT=1
17	60663077	COSV59954119	AT	A	.	.	GENE=PPM1D;STRAND=+;LEGACY_ID=COSM2793542;CDS=c.1349del;AA=p.L450*;HGVSC=ENST00000305921.7:c.1349del;HGVSP=ENSP00000306682.2:p.Leu450Ter;HGVSG=17:g.60663083del;CNT=21;OLD_VARIANT=17:60663082:TT/T
17	60663077	COSV100011144	A	AT	.	.	GENE=PPM1D;STRAND=+;LEGACY_ID=COSM8946569;CDS=c.1349dup;AA=p.L450Ffs*6;HGVSC=ENST00000305921.7:c.1349dup;HGVSP=ENSP00000306682.2:p.Leu450PhefsTer6;HGVSG=17:g.60663083dup;CNT=1;OLD_VARIANT=17:60663083:T/TT
3	179234296	COSV55997332	CA	AT	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM7339147;CDS=c.3139_3140delinsAT;AA=p.H1047I;HGVSC=ENST00000263967.3:c.3139_3140delinsAT;HGVSP=ENSP00000263967.3:p.His1047Ile;HGVSG=3:g.179234296_179234297delinsAT;CNT=2;OLD_VARIANT=3:179234295:ACA/AAT
3	179234296	COSV55876499	C	T	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM774;CDS=c.3139C>T;AA=p.H1047Y;HGVSC=ENST00000263967.3:c.3139C>T;HGVSP=ENSP00000263967.3:p.His1047Tyr;HGVSG=3:g.179234296C>T;CNT=105
3	179234296	COSV55912376	C	A	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM5029128;CDS=c.3139C>A;AA=p.H1047N;HGVSC=ENST00000263967.3:c.3139C>A;HGVSP=ENSP00000263967.3:p.His1047Asn;HGVSG=3:g.179234296C>A;CNT=1
3	179234297	COSV55977801	ATCA	GTCG	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM6949965;CDS=c.3140_3143delinsGTCG;AA=p.H1047_H1048delinsRR;HGVSC=ENST00000263967.3:c.3140_3143delinsGTCG;HGVSP=ENSP00000263967.3:p.His1047_His1048delinsArgArg;HGVSG=3:g.179234297_179234300delinsGTCG;CNT=4;OLD_VARIANT=3:179234296:CATCA/CGTCG
3	179234297	COSV55888015	A	C	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM249874;CDS=c.3140A>C;AA=p.H1047P;HGVSC=ENST00000263967.3:c.3140A>C;HGVSP=ENSP00000263967.3:p.His1047Pro;HGVSG=3:g.179234297A>C;CNT=2
3	179234297	COSV55873195	A	G	.	.	GENE=PIK3CA_ENST00000643187;STRAND=+;LEGACY_ID=COSM775;CDS=c.*220A>G;AA=p.?;HGVSC=ENST00000643187.1:c.*220A>G;HGVSG=3:g.179234297A>G;CNT=3596
3	179234297	COSV55888015	A	C	.	.	GENE=PIK3CA_ENST00000643187;STRAND=+;LEGACY_ID=COSM249874;CDS=c.*220A>C;AA=p.?;HGVSC=ENST00000643187.1:c.*220A>C;HGVSG=3:g.179234297A>C;CNT=2
3	179234297	COSV55873195	A	G	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM775;CDS=c.3140A>G;AA=p.H1047R;HGVSC=ENST00000263967.3:c.3140A>G;HGVSP=ENSP00000263967.3:p.His1047Arg;HGVSG=3:g.179234297A>G;CNT=3596
3	179234297	COSV55873401	A	T	.	.	GENE=PIK3CA_ENST00000643187;STRAND=+;LEGACY_ID=COSM776;CDS=c.*220A>T;AA=p.?;HGVSC=ENST00000643187.1:c.*220A>T;HGVSG=3:g.179234297A>T;CNT=537
3	179234297	COSV55873401	A	T	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM776;CDS=c.3140A>T;AA=p.H1047L;HGVSC=ENST00000263967.3:c.3140A>T;HGVSP=ENSP00000263967.3:p.His1047Leu;HGVSG=3:g.179234297A>T;CNT=537
3	179234297	COSV55979567	A	AT	.	.	GENE=PIK3CA_ENST00000643187;STRAND=+;LEGACY_ID=COSM6904744;CDS=c.*221dup;AA=p.?;HGVSC=ENST00000643187.1:c.*221dup;HGVSG=3:g.179234298dup;CNT=1;OLD_VARIANT=3:179234298:T/TT
3	179234297	COSV55979567	A	AT	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM6904744;CDS=c.3141dup;AA=p.H1048Sfs*16;HGVSC=ENST00000263967.3:c.3141dup;HGVSP=ENSP00000263967.3:p.His1048SerfsTer16;HGVSG=3:g.179234298dup;CNT=1;OLD_VARIANT=3:179234298:T/TT
3	179234298	COSV55920782	T	A	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM1041524;CDS=c.3141T>A;AA=p.H1047Q;HGVSC=ENST00000263967.3:c.3141T>A;HGVSP=ENSP00000263967.3:p.His1047Gln;HGVSG=3:g.179234298T>A;CNT=13
3	179234298	COSV55875891	T	G	.	.	GENE=PIK3CA;STRAND=+;LEGACY_ID=COSM24714;CDS=c.3141T>G;AA=p.H1047Q;HGVSC=ENST00000263967.3:c.3141T>G;HGVSP=ENSP00000263967.3:p.His1047Gln;HGVSG=3:g.179234298T>G;CNT=9"""
        with open(self.tmp_cosmic, "w") as FH_out:
            FH_out.write(content)
        pysam.tabix_compress(self.tmp_cosmic, self.tmp_cosmic_bz)
        # Create index
        pysam.tabix_index(self.tmp_cosmic_bz, preset="vcf")

        # Create input file
        content = """##fileformat=VCFv4.1
##INFO=<ID=TESTANN,Number=.,Type=String,Description="Consequence annotations from Ensembl VEP. Format: Allele|Consequence|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|SIFT|PolyPhen|CLIN_SIG|Existing_variation|AF|AFR_AF|AMR_AF|EAS_AF|EUR_AF|SAS_AF|AA_AF|EA_AF|gnomAD_AF|gnomAD_AFR_AF|gnomAD_AMR_AF|gnomAD_ASJ_AF|gnomAD_EAS_AF|gnomAD_FIN_AF|gnomAD_NFE_AF|gnomAD_OTH_AF|gnomAD_SAS_AF|FILTER">
##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allele depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	test-sample
chr10	87933224	.	T	TG	100.0	.	TESTANN=G|frameshift_variant|PTEN|5728|transcript|NM_000314.6|protein_coding|5/9||NM_000314.6%3Ac.470dupG|NP_000305.3%3Ap.(Glu157GlyfsTer23)|1496-1497|465-466|155-156|-/X|-/G||||COSM4718702&COSM5002&COSM5103&COSM5371246||||||||||||||||||PASS	AD:DP	125,194:319
chr12	25245350	.	CC	AA	100.0	PASS	TESTANN=AA|missense_variant|KRAS|3845|transcript|NM_004985.4|protein_coding|2/5||NM_004985.4%3Ac.34_35delinsTT|NP_004976.2%3Ap.(Gly12Phe)|226-227|34-35|12|G/F|GGt/TTt||||COSM1140135&COSM13643&COSM25081&COSM34144&COSM4387523&COSM512&COSM514&COSM5374884&COSM5751774&COSM5751775&COSM6072204&COSM6853641&COSM6853642&COSM6904437&COSM6959652&COSM6959653||||||||||||||||||PASS,AG|missense_variant|KRAS|3845|transcript|NM_004985.4|protein_coding|2/5||NM_004985.4%3Ac.34_35delinsTC|NP_004976.2%3Ap.(Gly12Ser)|226-227|34-35|12|G/S|GGt/TCt||||COSM1140135&COSM13643&COSM25081&COSM34144&COSM4387523&COSM512&COSM514&COSM5374884&COSM5751774&COSM5751775&COSM6072204&COSM6853641&COSM6853642&COSM6904437&COSM6959652&COSM6959653||||||||||||||||||PASS	AD:DP	1302,924:2226
chr17	60663077	.	AT	A	100.0	PASS	TESTANN=-|frameshift_variant|PPM1D|8493|transcript|NM_003620.3|protein_coding|6/6||NM_003620.3%3Ac.1349delT|NP_003611.1%3Ap.(Leu450Ter)|1576|1344|448|N/X|aaT/aa||||COSM2793542&rs758630849||||||||||||||||||PASS	AD:DP	132,100:232
chr2	140702286	.	T	C	100.0	.	TESTANN=C|missense_variant|LRP1B|53353|transcript|NM_018557.2|protein_coding|39/91||NM_018557.2%3Ac.6157A>G|NP_061027.2%3Ap.(Lys2053Glu)|7129|6157|2053|K/E|Aaa/Gaa|deleterious|benign||||||||||||||||||||PASS	AD:DP	151,13:164
chr3	179234297	.	A	G	100.0	.	TESTANN=G|missense_variant|PIK3CA|5290|transcript|NM_006218.3|protein_coding|21/21||NM_006218.3%3Ac.3140A>G|NP_006209.2%3Ap.(His1047Arg)|3297|3140|1047|H/R|cAt/cGt|tolerated|benign||COSM249874&COSM775&COSM776&COSM94986&COSM94987&rs121913279||||||||||||||||||PASS	AD:DP	154,41:195"""
        with open(self.tmp_input, "w") as FH_out:
            FH_out.write(content)

    def tearDown(self):
        for curr_file in [self.tmp_cosmic, self.tmp_cosmic_bz, self.tmp_cosmic_index, self.tmp_input, self.tmp_output]:
            if os.path.exists(curr_file):
                os.remove(curr_file)

    def testResults(self):
        subprocess.check_call(self.cmd, stderr=subprocess.DEVNULL)
        observed = None
        with open(self.tmp_output) as reader:
            observed = "".join(reader.readlines()).strip()
        expected = """##fileformat=VCFv4.3
##COSMIC=92
##INFO=<ID=TESTANN,Number=.,Type=String,Description="Consequence annotations from Ensembl VEP. Format: Allele|Consequence|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|SIFT|PolyPhen|CLIN_SIG|Existing_variation|AF|AFR_AF|AMR_AF|EAS_AF|EUR_AF|SAS_AF|AA_AF|EA_AF|gnomAD_AF|gnomAD_AFR_AF|gnomAD_AMR_AF|gnomAD_ASJ_AF|gnomAD_EAS_AF|gnomAD_FIN_AF|gnomAD_NFE_AF|gnomAD_OTH_AF|gnomAD_SAS_AF|FILTER">
##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allele depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	test-sample
chr10	87933224	.	T	TG	100.0	.	TESTANN=TG|frameshift_variant|PTEN|5728|transcript|NM_000314.6|protein_coding|5/9||NM_000314.6%3Ac.470dupG|NP_000305.3%3Ap.(Glu157GlyfsTer23)|1496-1497|465-466|155-156|-/X|-/G||||COSV64288964||||||||||||||||||PASS	AD:DP	125,194:319
chr12	25245350	.	CC	AA	100.0	PASS	TESTANN=AA|missense_variant|KRAS|3845|transcript|NM_004985.4|protein_coding|2/5||NM_004985.4%3Ac.34_35delinsTT|NP_004976.2%3Ap.(Gly12Phe)|226-227|34-35|12|G/F|GGt/TTt||||COSV55505818||||||||||||||||||PASS,AG|missense_variant|KRAS|3845|transcript|NM_004985.4|protein_coding|2/5||NM_004985.4%3Ac.34_35delinsTC|NP_004976.2%3Ap.(Gly12Ser)|226-227|34-35|12|G/S|GGt/TCt||||COSV55573070||||||||||||||||||PASS	AD:DP	1302,924:2226
chr17	60663077	.	AT	A	100.0	PASS	TESTANN=A|frameshift_variant|PPM1D|8493|transcript|NM_003620.3|protein_coding|6/6||NM_003620.3%3Ac.1349delT|NP_003611.1%3Ap.(Leu450Ter)|1576|1344|448|N/X|aaT/aa||||rs758630849&COSV59954119||||||||||||||||||PASS	AD:DP	132,100:232
chr2	140702286	.	T	C	100.0	.	TESTANN=C|missense_variant|LRP1B|53353|transcript|NM_018557.2|protein_coding|39/91||NM_018557.2%3Ac.6157A>G|NP_061027.2%3Ap.(Lys2053Glu)|7129|6157|2053|K/E|Aaa/Gaa|deleterious|benign||||||||||||||||||||PASS	AD:DP	151,13:164
chr3	179234297	.	A	G	100.0	.	TESTANN=G|missense_variant|PIK3CA|5290|transcript|NM_006218.3|protein_coding|21/21||NM_006218.3%3Ac.3140A>G|NP_006209.2%3Ap.(His1047Arg)|3297|3140|1047|H/R|cAt/cGt|tolerated|benign||rs121913279&COSV55873195||||||||||||||||||PASS	AD:DP	154,41:195"""
        self.assertEqual(observed, expected)


########################################################################
#
# MAIN
#
########################################################################
if __name__ == "__main__":
    unittest.main()
