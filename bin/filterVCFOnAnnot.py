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
__version__ = '1.7.0'
__email__ = 'escudie.frederic@iuct-oncopole.fr'
__status__ = 'prod'

import argparse
from anacore.annotVcf import AnnotVCFIO, getAlleleRecord, HeaderFilterAttr


########################################################################
#
# FUNCTIONS
#
########################################################################
def getKeptConsequences(allele_record, alt_in_annot_format, valid_consequences, annotation_field="ANN"):
    kept_conseq = list()
    for annot_idx, annot in enumerate(allele_record.info[annotation_field]):
        is_filtered = True
        if alt_in_annot_format == annot["Allele"] and annot["Consequence"] is not None:
            consequences = annot["Consequence"].split("&")  # For multi-consequence allele: Example: 'start_lost&NMD_transcript_variant'
            for current_csq in consequences:
                if current_csq in valid_consequences:
                    is_filtered = False
        if not is_filtered:
            kept_conseq.append(annot)
    return kept_conseq

def isPolymophism(allele_record, alt_in_annot_format, checked_pop_tags, min_AF=0.01, annotation_field="ANN"):
    is_polymorphism = False
    for collocated_var in allele_record.info[annotation_field]:
        if alt_in_annot_format == collocated_var["Allele"]:
            for pop_freq in checked_pop_tags:
                if pop_freq in collocated_var and collocated_var[pop_freq] is not None:
                    frequencies = collocated_var[pop_freq].split("&")  # For multi-reference SNP. Example: {'Existing_variation': 'rs7367494&rs34188929', 'Gene': 'ENSG00000184908', 'Allele': 'T', ..., 'ExAC_SAS_AF': '0.9253&0.9253', 'AF': '0.8299', 'EAS_AF': '0.9980&0.9980'}
                    for current_freq in frequencies:
                        if float(current_freq) >= min_AF:
                            is_polymorphism = True
    return is_polymorphism

def getVEPAlt(ref, alt):
    alleles = [ref] + alt
    # Replace empty marker by empty string
    for idx, cur_allele in enumerate(alleles):
        if cur_allele == "-":
            alleles[idx] = ""
    # Select shorter allele
    shorter_allele = alleles[0]
    for current_alt in alleles[1:]:
        if len(current_alt) < len(shorter_allele):
            shorter_allele = current_alt
    # Trim alleles
    trim = True
    while len(shorter_allele) != 0 and shorter_allele != "" and trim:
        for cur_allele in alleles:
            if len(cur_allele) == 0:
                trim = False
            elif cur_allele[0] != shorter_allele[0]:
                trim = False
        if trim:
            shorter_allele = shorter_allele[1:]
            for idx, cur_allele in enumerate(alleles):
                alleles[idx] = cur_allele[1:]
    # Replace empty by empty_marker
    for idx, cur_allele in enumerate(alleles):
        if cur_allele == "":
            alleles[idx] = "-"
    return alleles[1:]


########################################################################
#
# MAIN
#
########################################################################
# format see http://www.ensembl.org/info/docs/tools/vep/vep_formats.html#json
if __name__ == "__main__":
    # Manage parameters
    parser = argparse.ArgumentParser(description='Filters variants and their annotations on annotations. In "remove" mode the annotations are deleted if they not fit criteria and the variant is removed if none of his annotations fit criterias.')
    parser.add_argument('-f', '--annotation-field', default="ANN", help='Field used to store annotations. [Default: %(default)s]')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    group_filter = parser.add_argument_group('Filters')  # Filters
    group_filter.add_argument('-m', '--mode', default="tag", choices=["tag", "remove"], help='Select the filter mode. In mode "tag" if the variant does not fit criteria a tag "CSQ" and/or "popAF" is added in FILTER field. In mode "remove" if the variant does not fit criteria it is removed from the output. [Default: %(default)s]')
    group_filter.add_argument('-p', '--polym-populations', default=["AF", "AFR_AF", "AMR_AF", "EAS_AF", "EUR_AF", "SAS_AF", "AA_AF", "EA_AF", "ExAC_AF", "ExAC_Adj_AF", "ExAC_AFR_AF", "ExAC_AMR_AF", "ExAC_EAS_AF", "ExAC_FIN_AF", "ExAC_NFE_AF", "ExAC_OTH_AF", "ExAC_SAS_AF", "gnomAD_AF", "gnomAD_AFR_AF", "gnomAD_AMR_AF", "gnomAD_ASJ_AF", "gnomAD_EAS_AF", "gnomAD_FIN_AF", "gnomAD_NFE_AF", "gnomAD_OTH_AF", "gnomAD_SAS_AF"], help='Populations frequencies used as reference for polymorphism detection. [Default: %(default)s]')
    group_filter.add_argument('-l', '--polym-threshold', type=float, default=0.01, help='Minimum frequency in population to tag allele as polymorphism. [Default: %(default)s]')
    group_filter.add_argument('-k', '--kept-consequences', default=["TFBS_ablation", "TFBS_amplification", "TF_binding_site_variant", "regulatory_region_ablation", "regulatory_region_amplification", "transcript_ablation", "splice_acceptor_variant", "splice_donor_variant", "stop_gained", "frameshift_variant", "stop_lost", "start_lost", "transcript_amplification", "inframe_insertion", "inframe_deletion", "missense_variant", "protein_altering_variant"], nargs='+', help='The variants without one of these consequences are tagged as CSQ (see http://www.ensembl.org/info/genome/variation/predicted_data.html). [Default: %(default)s]')
    group_input = parser.add_argument_group('Inputs')  # Inputs
    group_input.add_argument('-i', '--input-variants', required=True, help='The path to the file containing variants annotated with VEP v88+ (format: VCF).')
    group_output = parser.add_argument_group('Outputs')  # Outputs
    group_output.add_argument('-o', '--output-variants', required=True, help='The path to the filtered file (format: VCF).')
    args = parser.parse_args()

    # Process
    with AnnotVCFIO(args.input_variants, "r", args.annotation_field) as FH_in:
        with AnnotVCFIO(args.output_variants, "w") as FH_out:
            # Header
            FH_out.copyHeader(FH_in)
            FH_out.filter["popAF"] = HeaderFilterAttr("popAF", "The variant is present with more of " + str(args.polym_threshold * 100) + "% in one of the following population: '" + "' ".join(args.polym_populations) + "'.")
            FH_out.filter["CSQ"] = HeaderFilterAttr("CSQ", "The variant has no consequence corresponding at one in the following list: '" + "' ".join(args.kept_consequences) + "'.")
            FH_out.writeHeader()
            # Records
            for record in FH_in:
                VEP_alt = getVEPAlt(record.ref, record.alt)
                for alt_idx, alt in enumerate(record.alt):
                    alt_record = getAlleleRecord(FH_in, record, alt_idx)
                    alt_record.normalizeSingleAllele()
                    # Evaluates polymorphism
                    is_polymophism = isPolymophism(alt_record, VEP_alt[alt_idx], args.polym_populations, args.polym_threshold, FH_in.annot_field)
                    # Evaluates consequences
                    valid_consequences = getKeptConsequences(alt_record, VEP_alt[alt_idx], args.kept_consequences, FH_in.annot_field)
                    # Filter the variant allele
                    if args.mode == "tag":
                        if alt_record.filter is None or len(alt_record.filter) == 0 or alt_record.filter[0] == "PASS":
                            alt_record.filter = list()
                        if is_polymophism:
                            alt_record.filter.append("popAF")
                        if len(valid_consequences) == 0:
                            alt_record.filter.append("CSQ")
                        if len(alt_record.filter) == 0:
                            alt_record.filter.append("PASS")
                        FH_out.write(alt_record)
                    else:
                        if not is_polymophism and len(valid_consequences) > 0:
                            alt_record.info[FH_in.annot_field] = valid_consequences
                            if alt_record.filter is None:
                                alt_record.filter = ["PASS"]
                            FH_out.write(alt_record)
