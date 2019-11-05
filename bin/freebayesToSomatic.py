#!/usr/bin/env python3
#
# Copyright (C) 2019 IUCT-O
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
__copyright__ = 'Copyright (C) 2019 IUCT-O'
__license__ = 'GNU General Public License'
__version__ = '1.1.0'
__email__ = 'escudie.frederic@iuct-oncopole.fr'
__status__ = 'prod'

import os
import sys
import logging
import argparse
from anacore.vcf import VCFIO, HeaderInfoAttr


########################################################################
#
# MAIN
#
########################################################################
if __name__ == "__main__":
    # Manage parameters
    parser = argparse.ArgumentParser(description='Update/remove germline fields coming from freebayes to a somatic version (reduce genotype influence).')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    group_input = parser.add_argument_group('Inputs')  # Inputs
    group_input.add_argument('-i', '--input-variants', required=True, help='The path to the variants file (format: VCF).')
    group_output = parser.add_argument_group('Outputs')  # Outputs
    group_output.add_argument('-o', '--output-variants', required=True, help='The path to the outputted variants file (format: VCF).')
    args = parser.parse_args()

    # Logger
    logging.basicConfig(format='%(asctime)s -- [%(filename)s][pid:%(process)d][%(levelname)s] -- %(message)s')
    log = logging.getLogger(os.path.basename(__file__))
    log.setLevel(logging.INFO)
    log.info("Command: " + " ".join(sys.argv))

    # Process
    with VCFIO(args.output_variants, "w") as FH_out:
        with VCFIO(args.input_variants) as FH_in:
            # Header
            FH_out.copyHeader(FH_in)
            FH_out.info["AD"] = HeaderInfoAttr(
                id="AD",
                number="A",
                type="Integer",
                description="Allele depth"
            )
            FH_out.info["AF"] = HeaderInfoAttr(
                id="AF",
                number="A",
                type="Float",
                description="Allele frequency"
            )
            FH_out.info["DP"] = HeaderInfoAttr(
                id="DP",
                number="1",
                type="Integer",
                description="Total depth"
            )
            FH_out.writeHeader()
            # Records
            for record in FH_in:
                fields = ["DP", "AD", "AF"]
                for curr_field in fields:
                    if curr_field in record.info:
                        del(record.info[curr_field])
                record.info["DP"] = record.getPopDP()
                record.info["AD"] = record.getPopAltAD()
                record.info["AF"] = [round(elt, 5) for elt in record.getPopAltAF()]
                FH_out.write(record)
    log.info("End of job")
