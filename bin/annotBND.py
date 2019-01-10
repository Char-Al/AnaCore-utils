#!/usr/bin/env python3
#
# Copyright (C) 2018 IUCT-O
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
__copyright__ = 'Copyright (C) 2018 IUCT-O'
__license__ = 'GNU General Public License'
__version__ = '1.0.0'
__email__ = 'escudie.frederic@iuct-oncopole.fr'
__status__ = 'prod'


import os
import sys
import logging
import argparse
import warnings
from anacore.gtf import loadModel
from anacore.genomicRegion import Intron
from anacore.annotVcf import AnnotVCFIO, VCFIO
from anacore.region import Region, splittedByRef


########################################################################
#
# FUNCTIONS
#
########################################################################
def getRegionGeneAnnot(region, genes_by_chr):
    """
    """
    annotations = []
    container_genes = genes_by_chr[record.chrom].getContainers(variant_region)
    for curr_gene in container_genes:
        container_transcripts = curr_gene.children.getContainers(variant_region)
        if len(container_transcripts) == 0:
            warnings.warn("The breakpoint {} is contained by gene {} but by 0 of these transcripts.".format(region, curr_gene))
        else:
            for curr_transcript in container_transcripts:
                curr_annot = {
                    "SYMBOL": curr_gene.name,
                    "Gene": curr_gene.annot["id"],
                    "Feature": curr_transcript.annot["id"],
                    "Feature_type": "Transcript",
                    "STRAND": None,
                    "EXON": None,
                    "INTRON": None,
                    "CDS_position": None,
                    "Protein_position": None
                }
                if curr_transcript.strand is not None:
                    curr_annot["STRAND"] = ("1" if curr_transcript.strand == "+" else "-1")
                subregion, subregion_idx = curr_transcript.getSubFromRefPos(region.start)
                if issubclass(subregion.__class__, Intron):  # On intron
                    curr_annot["INTRON"] = "{}/{}".format(
                        subregion_idx,
                        len(curr_transcript.children) - 1
                    )
                else:  # On exon
                    curr_annot["EXON"] = "{}/{}".format(
                        subregion_idx,
                        len(curr_transcript.children)
                    )
                    if len(curr_transcript.proteins) > 1:
                        raise Exception("The management of several proteins for one transcript is not implemented. The transcript {} contains several proteins {}.".format(curr_transcript, curr_transcript.proteins))
                    if len(curr_transcript.proteins) > 0:
                        curr_annot["CDS_position"] = curr_transcript.proteins[0].getNtPosFromRefPos(region.start)
                        if curr_annot["CDS_position"] is not None:
                            curr_annot["Protein_position"] = curr_transcript.proteins[0].getPosOnRegion(region.start)[0]
                annotations.append(curr_annot)
    return annotations

def annotBNDStream(record):
    """
    """
    # Get position relative to the break
    is_before_break = []
    for bnd_idx, alt in enumerate(record.alt):
        if alt.startswith("[") or alt.startswith("]"):
            is_before_break.append(False)
        else:
            is_before_break.append(True)
    if len(set(is_before_break)) > 1:
        record_name = record.id if record.id is not None else record.getName()
        raise Exception("The breakend {} has severeal fusion partners with different break's configuration.".format(record_name))
    is_before_break = is_before_break[0]
    # Set BND_stream
    genes = set([annot["Gene"] for annot in record.info["ANN"]])
    for annot in record.info["ANN"]:
        if annot["STRAND"] is not None:
            annot["BND_stream"] = "down"
            if annot["STRAND"] == "1":
                if is_before_break:
                    annot["BND_stream"] = "up"
            else:
                if not is_before_break:
                    annot["BND_stream"] = "up"


########################################################################
#
# MAIN
#
########################################################################
if __name__ == "__main__":
    # Manage parameters
    parser = argparse.ArgumentParser(description='Annotate BND in a VCF with content of a GTF.')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    group_input = parser.add_argument_group('Inputs')  # Inputs
    group_input.add_argument('-a', '--input-annotations', required=True, help='Path to the file containing the annotations of genes and transcript for the reference used in variant calling. (format: GTF).')
    group_input.add_argument('-i', '--input-variants', required=True, help='Path to the file containing variants. (format: VCF).')
    group_output = parser.add_argument_group('Outputs')  # Outputs
    group_output.add_argument('-o', '--output-variants', required=True, help='Path to the annotated file. (format: VCF).')
    args = parser.parse_args()

    # Logger
    logging.basicConfig(format='%(asctime)s - %(name)s [%(levelname)s] %(message)s')
    log = logging.getLogger(os.path.basename(__file__))
    log.setLevel(logging.INFO)
    log.info("Command: " + " ".join(sys.argv))

    # Load annotations
    log.info("Load model from {}.".format(args.input_annotations))
    genes = loadModel(args.input_annotations, "genes")
    genes_by_chr = splittedByRef(genes)

    # Annot variants
    log.info("Annot variants in {}.".format(args.input_variants))
    with AnnotVCFIO(args.output_variants, "w") as FH_out:
        with VCFIO(args.input_variants) as FH_in:
            # Header
            FH_out.copyHeader(FH_in)
            FH_out.ANN_titles = ["SYMBOL", "Gene", "Feature", "Feature_type", "STRAND", "EXON", "INTRON", "CDS_position", "Protein_position"]
            FH_out.info["ANN"] = {
                "type": str,
                "type_tag": "String",
                "number": None,
                "number_tag": ".",
                "description": "Consequence annotations. Format: " + "|".join(FH_out.ANN_titles)
            }
            FH_out._writeHeader()
            # Records
            for record in FH_in:
                variant_region = Region(record.pos, None, None, record.chrom, record.getName())
                if record.info["SVTYPE"] == "BND":
                    record.info["ANN"] = getRegionGeneAnnot(variant_region, genes_by_chr)
                    annotBNDStream(record)
                FH_out.write(record)
    log.info("End process.")

    #~ strand_by_id = {}
    #~ with VCFIO(args.input_variants) as FH_in:
        #~ for record in FH_in:
            #~ for bnd_idx, bnd_id in enumerate(record.info["MATEID"]):
                #~ strand_by_id[bnd_id] = "+" if record.alt[bnd_idx].startswith("[") or record.alt[bnd_idx].endswith("[") else "-"