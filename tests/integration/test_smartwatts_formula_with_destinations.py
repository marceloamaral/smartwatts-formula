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
# Last modified : 19 April 2022

##############################
#
# Imports
#
##############################
from datetime import datetime

import pytest as pytest
from powerapi.destination import InfluxDestination

from powerapi.quantity import MHz, W
from powerapi.rx import Source
from powerapi.rx.hwpc_reports_group import HWPCReportsGroup, GROUPS_CN
from powerapi.rx.report import TARGET_CN
from powerapi.rx.reports_group import TIMESTAMP_CN, SENSOR_CN, DATE_FORMAT, TIME_CN
from powerapi.rx.source import source

from smartwatts.context import SmartWattsFormulaConfig, SmartWattsFormulaScope
from smartwatts.rx_formula import RAPL_GROUP, MSR_GROUP, MPERF_EVENT, APERF_EVENT, CORE_GROUP, Smartwatts
from smartwatts.topology import CPUTopology
from tests.utils import MultipleReportSource

##############################
#
# Constants
#
##############################
INFLUX_URI = "localhost"
INFLUX_PORT = 8086
INFLUX_DBNAME = "db_test_influx"


##############################
#
# Fixtures
#
##############################

@pytest.fixture
def create_hwpc_reports_group_1() -> HWPCReportsGroup:
    """ Creates a HWPC Report """
    report_dict = {TIMESTAMP_CN: datetime. strptime("2022-03-31T10:03:16.196+00:00", DATE_FORMAT),
                   SENSOR_CN: "sensor",
                   TARGET_CN: "all",
                   GROUPS_CN: {
                       RAPL_GROUP: {
                           "0": {
                               "7": {
                                   "RAPL_ENERGY_PKG": 2151940096,
                                   "time_enabled": 503709618,
                                   "time_running": 503709618}}},
                       MSR_GROUP: {
                           "0": {
                               "0": {
                                   MPERF_EVENT: 27131018,
                                   APERF_EVENT: 14511032,
                                   "TSC": 1062403542,
                                   "time_enabled": 503596227,
                                   "time_running": 503596227},
                               "1": {MPERF_EVENT: 10724256,
                                     APERF_EVENT: 6219967,
                                     "TSC": 1062508538,
                                     "time_enabled": 503652347,
                                     "time_running": 503652347},
                               "2": {MPERF_EVENT: 34843946,
                                     APERF_EVENT: 20517490,
                                     "TSC": 1062516244,
                                     "time_enabled": 503657311,
                                     "time_running": 503657311},
                               "3": {MPERF_EVENT: 44880217,
                                     APERF_EVENT: 24521456,
                                     "TSC": 1061496242,
                                     "time_enabled": 503178189,
                                     "time_running": 503178189},
                               "4": {MPERF_EVENT: 33798356,
                                     APERF_EVENT: 15466927,
                                     "TSC": 1061649272,
                                     "time_enabled": 503258869,
                                     "time_running": 503258869},
                               "5": {MPERF_EVENT: 23821766,
                                     APERF_EVENT: 13564798,
                                     "TSC": 1061829320,
                                     "time_enabled": 503349457,
                                     "time_running": 503349457},
                               "6": {MPERF_EVENT: 16511276,
                                     APERF_EVENT: 8192311,
                                     "TSC": 1061959760,
                                     "time_enabled": 503411582,
                                     "time_running": 503411582},
                               "7": {MPERF_EVENT: 37457327,
                                     APERF_EVENT: 17288854,
                                     "TSC": 1062186326,
                                     "time_enabled": 503490955,
                                     "time_running": 503490955}}}}}

    return HWPCReportsGroup.create_reports_group_from_dicts([report_dict])


@pytest.fixture
def create_hwpc_reports_group_2() -> HWPCReportsGroup:
    """ Creates a HWPC Report """
    report_dict = {
        TIMESTAMP_CN: datetime. strptime("2022-03-31T10:03:17.196+00:00", DATE_FORMAT),
        SENSOR_CN: "sensor",
        TARGET_CN: "all",
        GROUPS_CN: {RAPL_GROUP:
                        {"0":
                             {"7":
                                  {"RAPL_ENERGY_PKG": 1448607744,
                                   "time_enabled": 2511811640,
                                   "time_running": 2511811640}}},
                    MSR_GROUP: {"0": {"0": {MPERF_EVENT: 19904712,
                                            APERF_EVENT: 8542957,
                                            "TSC": 1060745522,
                                            "time_enabled": 2511773057,
                                            "time_running": 2511773057},
                                      "1": {MPERF_EVENT: 4518072,
                                            APERF_EVENT: 2044618,
                                            "TSC": 1060699862,
                                            "time_enabled": 2511789422,
                                            "time_running": 2511789422},
                                      "2": {MPERF_EVENT: 44380305,
                                            APERF_EVENT: 19031866,
                                            "TSC": 1060637034,
                                            "time_enabled": 2511791885,
                                            "time_running": 2511791885},
                                      "3": {MPERF_EVENT: 25771800,
                                            APERF_EVENT: 11048323,
                                            "TSC": 1060783900,
                                            "time_enabled": 2511491166,
                                            "time_running": 2511491166},
                                      "4": {MPERF_EVENT: 52030149,
                                            APERF_EVENT: 22304587,
                                            "TSC": 1060827414,
                                            "time_enabled": 2511562374,
                                            "time_running": 2511562374},
                                      "5": {MPERF_EVENT: 15509844,
                                            APERF_EVENT: 6652760,
                                            "TSC": 1060775190,
                                            "time_enabled": 2511618366,
                                            "time_running": 2511618366},
                                      "6": {MPERF_EVENT: 7609809,
                                            APERF_EVENT: 3267467,
                                            "TSC": 1060727312,
                                            "time_enabled": 2511698088,
                                            "time_running": 2511698088},
                                      "7": {MPERF_EVENT: 13526448,
                                            APERF_EVENT: 5803844,
                                            "TSC": 1060736074,
                                            "time_enabled": 2511729308,
                                            "time_running": 2511729308}}}}}

    return HWPCReportsGroup.create_reports_group_from_dicts([report_dict])


@pytest.fixture
def create_hwpc_reports_group_3() -> HWPCReportsGroup:
    """ Creates a HWPC Report """
    report_dict = {
        TIMESTAMP_CN: datetime.strptime("2022-03-31T10:03:19.196+00:00",DATE_FORMAT),
        SENSOR_CN: "sensor",
        TARGET_CN: "modest_leavitt",
        GROUPS_CN: {CORE_GROUP:
                        {"0":
                             {"0":
                                  {"CPU_CLK_THREAD_UNHALTED:THREAD_P": 390665,
                                   "CPU_CLK_THREAD_UNHALTED:REF_P": 10452,
                                   "time_enabled": 2893886,
                                   "time_running": 2893886,
                                   "LLC_MISSES": 6871,
                                   "INSTRUCTIONS_RETIRED": 317866},
                              "1":
                                  {"CPU_CLK_THREAD_UNHALTED:THREAD_P": 912931,
                                   "CPU_CLK_THREAD_UNHALTED:REF_P": 17712,
                                   "time_enabled": 4659267,
                                   "time_running": 4659267,
                                   "LLC_MISSES": 4653,
                                   "INSTRUCTIONS_RETIRED": 332430},
                              "2": {"CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                                    "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                                    "time_enabled": 3316772,
                                    "time_running": 3316772,
                                    "LLC_MISSES": 0,
                                    "INSTRUCTIONS_RETIRED": 0},
                              "3": {"CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                                    "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                                    "time_enabled": 0,
                                    "time_running": 0,
                                    "LLC_MISSES": 0,
                                    "INSTRUCTIONS_RETIRED": 0},
                              "4": {"CPU_CLK_THREAD_UNHALTED:THREAD_P": 1549721,
                                    "CPU_CLK_THREAD_UNHALTED:REF_P": 41422,
                                    "time_enabled": 11167120,
                                    "time_running": 11167120,
                                    "LLC_MISSES": 31560,
                                    "INSTRUCTIONS_RETIRED": 1809124},
                              "5": {"CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                                    "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                                    "time_enabled": 0, "time_running": 0,
                                    "LLC_MISSES": 0,
                                    "INSTRUCTIONS_RETIRED": 0},
                              "6": {"CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                                    "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                                    "time_enabled": 0,
                                    "time_running": 0,
                                    "LLC_MISSES": 0,
                                    "INSTRUCTIONS_RETIRED": 0},
                              "7": {"CPU_CLK_THREAD_UNHALTED:THREAD_P": 1312173,
                                    "CPU_CLK_THREAD_UNHALTED:REF_P": 20977,
                                    "time_enabled": 3272674,
                                    "time_running": 3272674,
                                    "LLC_MISSES": 44165,
                                    "INSTRUCTIONS_RETIRED": 865509}}}}}

    return HWPCReportsGroup.create_reports_group_from_dicts([report_dict])


@pytest.fixture
def create_hwpc_reports_group_4() -> HWPCReportsGroup:
    """ Creates a HWPC Report """
    report_dict = {TIMESTAMP_CN: datetime.now(),
                   # We are 00 hours and 00 minutes ahead of UTC
                   SENSOR_CN: "sensor",
                   TARGET_CN: "all",
                   GROUPS_CN: {
                       RAPL_GROUP: {
                           "0": {
                               "7": {
                                   "RAPL_ENERGY_PKG": 2151940096,
                                   "time_enabled": 503709618,
                                   "time_running": 503709618}}},
                       MSR_GROUP: {
                           "0": {
                               "0": {
                                   MPERF_EVENT: 27131018,
                                   APERF_EVENT: 14511032,
                                   "TSC": 1062403542,
                                   "time_enabled": 503596227,
                                   "time_running": 503596227},
                               "1": {MPERF_EVENT: 10724256,
                                     APERF_EVENT: 6219967,
                                     "TSC": 1062508538,
                                     "time_enabled": 503652347,
                                     "time_running": 503652347},
                               "2": {MPERF_EVENT: 34843946,
                                     APERF_EVENT: 20517490,
                                     "TSC": 1062516244,
                                     "time_enabled": 503657311,
                                     "time_running": 503657311},
                               "3": {MPERF_EVENT: 44880217,
                                     APERF_EVENT: 24521456,
                                     "TSC": 1061496242,
                                     "time_enabled": 503178189,
                                     "time_running": 503178189},
                               "4": {MPERF_EVENT: 33798356,
                                     APERF_EVENT: 15466927,
                                     "TSC": 1061649272,
                                     "time_enabled": 503258869,
                                     "time_running": 503258869},
                               "5": {MPERF_EVENT: 23821766,
                                     APERF_EVENT: 13564798,
                                     "TSC": 1061829320,
                                     "time_enabled": 503349457,
                                     "time_running": 503349457},
                               "6": {MPERF_EVENT: 16511276,
                                     APERF_EVENT: 8192311,
                                     "TSC": 1061959760,
                                     "time_enabled": 503411582,
                                     "time_running": 503411582},
                               "7": {MPERF_EVENT: 37457327,
                                     APERF_EVENT: 17288854,
                                     "TSC": 1062186326,
                                     "time_enabled": 503490955,
                                     "time_running": 503490955}}}}}

    return  HWPCReportsGroup.create_reports_group_from_dicts([report_dict])


@pytest.fixture
def create_3_hwpc_reports_groups(create_hwpc_reports_group_1, create_hwpc_reports_group_2,
                                 create_hwpc_reports_group_3) -> list:
    return [create_hwpc_reports_group_1, create_hwpc_reports_group_2, create_hwpc_reports_group_3]


@pytest.fixture
def create_4_hwpc_reports_groups(create_hwpc_reports_group_1, create_hwpc_reports_group_2, create_hwpc_reports_group_3,
                                 create_hwpc_reports_group_4) -> list:
    return [create_hwpc_reports_group_4,create_hwpc_reports_group_3, create_hwpc_reports_group_1, create_hwpc_reports_group_2]


@pytest.fixture
def create_2_hwpc_reports_groups(create_hwpc_reports_group_3,
                                 create_hwpc_reports_group_1) -> list:
    return [create_hwpc_reports_group_3, create_hwpc_reports_group_1]


@pytest.fixture
def create_smartwatts_config() -> SmartWattsFormulaConfig:
    """ Creates a configuration """

    # CPU Topology
    cpu_topology = CPUTopology(tdp=125 * W, freq_bclk=100 * MHz, ratio_min=4 * MHz, ratio_max=42 * MHz,
                               ratio_base=19 * MHz)

    return SmartWattsFormulaConfig(rapl_event="RAPL_ENERGY_PKG", min_samples_required=2, history_window_size=3,
                                   cpu_topology=cpu_topology, real_time_mode=True, scope=SmartWattsFormulaScope.CPU,
                                   socket_domain_value="0")


##############################
#
# Tests
#
##############################
def test_smartwatts_calls_1_time_influxdb_with_realtime_mode_and_4_reports_groups(create_smartwatts_config,
                                                                                  create_4_hwpc_reports_groups):
    """ Test that smartwatts formula works well with influxdb """

    # Setup
    the_source = Source(MultipleReportSource(create_4_hwpc_reports_groups))
    influx_destination = InfluxDestination(uri=INFLUX_URI, port=INFLUX_PORT, db_name=INFLUX_DBNAME)
    smartwatts_formula = Smartwatts(create_smartwatts_config)

    influx_dicts_list = create_4_hwpc_reports_groups[0].to_influx_dict()

    # Exercise

    source(the_source).pipe(smartwatts_formula).subscribe(influx_destination)

    # Check

    assert len(smartwatts_formula.ticks) == 2  # There are only two ticks (process_report has been called twice)

    influx_destination.client.switch_database(INFLUX_DBNAME)
    result = influx_destination.client.query(
        query="SELECT * FROM power_consumption WHERE time={}".format(influx_dicts_list[0][TIME_CN]))
    result_list = list(result.get_points())

    assert len(result_list) == 0  # Not result is found because there is not 'all' target


def test_smartwatts_does_not_call__influxdb_with_realtime_mode_and_2_reports(create_smartwatts_config,
                                                                              create_2_hwpc_reports_groups):
     """ Test that smartwatts formula works well with influxdb """

     # Setup
     the_source = Source(MultipleReportSource(create_2_hwpc_reports_groups))
     influx_destination = InfluxDestination(uri=INFLUX_URI, port=INFLUX_PORT, db_name=INFLUX_DBNAME)
     smartwatts_formula = Smartwatts(create_smartwatts_config)

     influx_dict = create_2_hwpc_reports_groups[1].to_influx_dict()

     # Exercise

     source(the_source).pipe(smartwatts_formula).subscribe(influx_destination)

     # Check
     assert len(smartwatts_formula.ticks) == 2  # There are two ticks (process_report has not been called)

     influx_destination.client.switch_database(INFLUX_DBNAME)
     result = influx_destination.client.query(query="SELECT * FROM power_consumption WHERE time={}"
                                              .format(influx_dict[0][TIME_CN]))
     result_list = list(result.get_points())

     assert len(result_list) == 0  # No result is found
