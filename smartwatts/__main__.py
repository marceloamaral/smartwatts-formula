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

# Author : Daniel Romero Acero
# Last modified : 21 April 2022

##############################
#
# Imports
#
##############################
from powerapi.destination import InfluxDestination
from powerapi.quantity import W, MHz, GHz, ms
from powerapi.rx import HWPCReport
from powerapi.rx.source import source
from powerapi.sources import MongoSource

##############################
#
# Constants
#
##############################
INFLUX_URI = "localhost"
INFLUX_PORT = 8086
INFLUX_DBNAME = "db_benchmarks_rx_output"

MONGO_URI = "mongodb://localhost:27017/"
MONGO_COLLECTION_NAME = "collection_test_data_set"
MONGO_DATABASE_NAME = "db_data_set_for_testing"

##############################
#
# Functions
#
##############################
from smartwatts.context import SmartWattsFormulaConfig, SmartWattsFormulaScope
from smartwatts.topology import CPUTopology
from smartwatts.rx_formula import Smartwatts


def create_smartwatts_config() -> SmartWattsFormulaConfig:
    """ Creates a configuration """

    # CPU Topology
    # Kaby Lake R topology (CPU @ 1.9GHz) - Data set origin
    cpu_topology = CPUTopology(tdp=125 * W, freq_bclk=1900 * MHz, ratio_min=400 * MHz, ratio_max=4200 * MHz,
                               ratio_base=1900 * MHz)

    return SmartWattsFormulaConfig(rapl_event="RAPL_ENERGY_PKG", min_samples_required=10, history_window_size=60,
                                   cpu_topology=cpu_topology, real_time_mode=False, scope=SmartWattsFormulaScope.CPU,
                                   socket_domain_value="0", reports_frequency=1000 * ms)


if __name__ == "__main__":
    # We prepare the chain

    # Source

    mongo_source = MongoSource(uri=MONGO_URI, db_name=MONGO_DATABASE_NAME,
                               collection_name=MONGO_COLLECTION_NAME,
                               report_type=HWPCReport, stream_mode=False)
    # Destination
    influx_destination = InfluxDestination(uri=INFLUX_URI, port=INFLUX_PORT, db_name=INFLUX_DBNAME)

    # Formula
    smartwatts_formula = Smartwatts(create_smartwatts_config())

    # We process the hwpc reports
    source(mongo_source).pipe(smartwatts_formula).subscribe(influx_destination)

    # We close the source
    mongo_source.close()
    print("Processing ended !")
