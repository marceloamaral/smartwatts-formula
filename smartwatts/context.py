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

# Last modified : 17 March 2022

##############################
#
# Imports
#
##############################

from enum import Enum

##############################
#
# Classes
#
##############################
from typing import Optional

from powerapi.quantity import PowerAPIQuantity, W, Hz, ms, MHz

from smartwatts.topology import CPUTopology


class SmartWattsFormulaScope(Enum):
    """ Enum used to set the scope of the SmartWatts formula. """

    CPU = "cpu"
    DRAM = "dram"


class SmartWattsFormulaConfig:
    """ Global config of the SmartWatts formula """

    def __init__(self,  rapl_event: str, min_samples_required: int, history_window_size: int,
                 cpu_topology: CPUTopology = CPUTopology(tdp=125 * W, freq_bclk=100 * MHz, ratio_min=100*MHz,
                                                         ratio_max=4000 * MHz, ratio_base=2300*MHz),
                 scope: SmartWattsFormulaScope = SmartWattsFormulaScope.CPU,
                 real_time_mode: bool = False, error_threshold: PowerAPIQuantity = 2*W,
                 reports_frequency: PowerAPIQuantity = 2*ms, core_domain_value: Optional[str] = None,
                 socket_domain_value: Optional[str] = None):
        """ Initialize a new formula config object

            Args:
                scope: Scope of the formula
                reports_frequency: Frequency at which the reports (in milliseconds)
                rapl_event: RAPL event to use as reference
                error_threshold: Error threshold (in Watt)
                cpu_topology: Topology of the CPU
                min_samples_required: Minimum amount of samples required before trying to learn a power model
                history_window_size: Size of the history window used to keep samples to learn from
                core_domain_value: The core domain value to use as reference
                socket_domain_value: The socket domain value to use as reference
        """

        self.scope = scope
        self.reports_frequency = reports_frequency
        self.rapl_event = rapl_event
        self.error_threshold = error_threshold
        self.cpu_topology = cpu_topology
        self.min_samples_required = min_samples_required
        self.history_window_size = history_window_size
        self.real_time_mode = real_time_mode
        self.core_domain_value = core_domain_value
        self.socket_domain_value = socket_domain_value
