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
__version__ = '1.0.0'
__email__ = 'escudie.frederic@iuct-oncopole.fr'
__status__ = 'prod'

from jflow.component import Component
from jflow.abstraction import MultiMap

from weaver.function import ShellFunction


class FilterVCFOnCount (Component):

    def define_parameters(self, in_variants, min_AF=0.02, min_DP=120, mode="tag"):
        # Parameters
        self.add_parameter('min_AF', 'The minimum allele frequency to validate the variant.', type=float, default=min_AF)
        self.add_parameter('min_DP', 'The minimum depth in sample to validate the variant.', type=int, default=min_DP)
        self.add_parameter('mode', 'In mode "tag" if the variant does not fit criteria a tag is added in FILTER field. In mode "remove" if the variant does not fit criteria it is removed from the output.', choices=["tag", "remove"], default=mode)

        # Files
        self.add_input_file_list("in_variants", "Path to the variants file (format: VCF).", default=in_variants, required=True)
        self.add_output_file_list("out_variants", "Path to the outputted variants file (format: VCF).", pattern='{basename_woext}.vcf', items=self.in_variants)
        self.add_output_file_list("stderr", "Path to the stderr file (format: txt).", pattern='{basename_woext}.stderr', items=self.in_variants)

    def process(self):
        cmd = self.get_exec_path("filterVCFOnCount.py") + \
            " --mode " + self.mode + \
            " --DP-threshold " + str(self.min_DP) + \
            " --AF-threshold " + str(self.min_AF) + \
            " --input-variants $1" + \
            " --output-variants $2" + \
            " 2> $3"
        filter_fct = ShellFunction(cmd, cmd_format='{EXE} {IN} {OUT}')
        MultiMap(filter_fct, inputs=[self.in_variants], outputs=[self.out_variants, self.stderr])