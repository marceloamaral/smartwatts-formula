# Copyright (c) 2022, INRIA
# Copyright (c) 2022, University of Lille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Last modified : 21 March 2022

##############################
#
# Imports
#
##############################
from powerapi.quantity import PowerAPIQuantity, MHz, W


##############################
#
# Classes
#
##############################
class CPUTopology:
    """ This class stores the necessary information about the CPU topology """

    def __init__(self, tdp: PowerAPIQuantity, freq_bclk: PowerAPIQuantity, ratio_min: PowerAPIQuantity,
                 ratio_base: PowerAPIQuantity, ratio_max: PowerAPIQuantity):
        """ Create a new CPU topology object

            Args:
                tdp: TDP of the CPU. It is transformed to Watt
                freq_bclk: Base clock. It is transformed to MHz and divided by 100
                ratio_min: Maximum efficiency ratio. It is transformed to MHz and divided by 100
                ratio_base: Base frequency ratio. It is transformed to MHz and divided by 100
                ratio_max: Maximum frequency ratio (with Turbo-Boost). It is transformed to MHz and divided by
        """
        self.tdp = tdp.to(W)
        self.freq_bclk = freq_bclk.to(MHz) / 100
        self.ratio_min = ratio_min.to(MHz) / 100
        self.ratio_base = ratio_base.to(MHz) / 100
        self.ratio_max = ratio_max.to(MHz) / 100

    def get_min_frequency(self) -> PowerAPIQuantity:
        """ Compute and return the CPU max efficiency frequency

            Return:
                The CPU max efficiency frequency in MHz
        """

        return self.freq_bclk * self.ratio_min.magnitude

    def get_base_frequency(self) -> PowerAPIQuantity:
        """ Compute and return the CPU base frequency

            Return:
                The CPU base frequency in MHz
        """
        return self.freq_bclk * self.ratio_base.magnitude

    def get_max_frequency(self) -> PowerAPIQuantity:
        """ Compute and return the CPU maximum frequency. (Turbo-Boost included)

            Return:
                The CPU maximum frequency in MHz
        """
        return self.freq_bclk * self.ratio_max.magnitude

    def get_supported_frequencies(self):
        """ Compute the supported frequencies for this CPU
            Return:
                A list of supported frequencies in MHz
        """
        return list(range(int(self.get_min_frequency().magnitude), int(self.get_max_frequency().magnitude) + 1,
                          int(self.freq_bclk.magnitude)))
