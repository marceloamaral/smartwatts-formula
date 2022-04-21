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
# Last modified : 1 April 2022

##############################
#
# Imports
#
##############################
from collections import deque, OrderedDict, defaultdict
from datetime import datetime
from hashlib import sha1
from math import fabs, ldexp
from pickle import dumps
from typing import Dict

from pandas import MultiIndex
from powerapi import quantity
from powerapi.quantity import PowerAPIQuantity, ms, W
from powerapi.report import HWPCReport
from powerapi.rx import Report
from powerapi.rx.formula import Formula
from powerapi.rx.power_report import POWER_CN, PowerReport
from sklearn.exceptions import NotFittedError

from sklearn.linear_model import ElasticNet as Regression

##############################
#
# Constants
#
##############################
RAPL_GROUP = 'rapl'
GLOBAL_GROUP = 'global'
MSR_GROUP = 'msr'
CORE_GROUP = 'core'

APERF_EVENT = 'APERF'
MPERF_EVENT = 'MPERF'

TIME_EVENT_PREFIX = 'time_'

##############################
#
# Classes
#
##############################
from smartwatts.context import SmartWattsFormulaConfig
from smartwatts.exception import SmartWattsException, create_exception_message_missing_index


class History:
    """ This class stores the reports history to use when learning a new power model """

    def __init__(self, max_length):
        """ Initialize a new reports history container.

            Args:
                max_length: Maximum amount of samples to keep before overriding the oldest sample at insertion
        """
        self.max_length = max_length
        self.X = deque(maxlen=max_length)
        self.y = deque(maxlen=max_length)

    def __len__(self):
        """ Compute the length of the history

            Return:
            Length of the history
        """
        return len(self.X)

    def store_report(self, power_reference: PowerAPIQuantity, events_value: []):
        """ Append a report to the reports history

            Args:

                events_value: List of raw events value
                power_reference: Power reference corresponding to the events value
        """
        self.X.append(events_value)
        self.y.append(power_reference.magnitude)


class PowerModel:
    """ This Power model compute the power estimations and handle the learning of a new model when needed """

    def __init__(self, frequency: int, history_window_size: int):
        """ Initialize a new power model

            Args:
                frequency: Frequency of the power model
                history_window_size: Size of the history window used to keep samples to learn from
        """
        self.frequency = frequency
        self.model = Regression()
        self.hash = 'uninitialized'
        self.history = History(history_window_size)
        self.id = 0

    def learn_power_model(self, min_samples: int, min_intercept: int, max_intercept: int):
        """ Learn a new power model using the stored reports and update the formula id/hash

        Args:
            min_samples: Minimum amount of samples required to learn the power model
            min_intercept: Minimum value allowed for the intercept of the model
            max_intercept: Maximum value allowed for the intercept of the model
        """
        if len(self.history) < min_samples:
            return

        fit_intercept = len(self.history) == self.history.max_length
        model = Regression(fit_intercept=fit_intercept, positive=True).fit(self.history.X, self.history.y)

        # Discard the new model when the intercept is not in specified range
        if not min_intercept <= model.intercept_ < max_intercept:
            return

        self.model = model
        self.hash = sha1(dumps(self.model)).hexdigest()
        self.id += 1

    @staticmethod
    def _extract_events_value(events: Dict):
        """ Creates and return a list of events value from the events group

            Args:
                events: Events group

            Return:
                List containing the events value sorted by event name
                TODO TO USE DATAFRAMES INSTEAD OF DICTIONARIES ??
        """
        return [value for _, value in sorted(events.items())]

    def store_report_in_history(self, power_reference: PowerAPIQuantity, events: Dict):
        """ Store the events group into the System reports list and learn a new power model

        Args:
            power_reference: Power reference. It is stored in Watt
            events: Events value
        """
        self.history.store_report(power_reference, self._extract_events_value(events))

    def compute_power_estimation(self, events: Dict):
        """Compute a power estimation from the events value using the power model

            Args:
                events: Events value
                NotFittedError when the model haven't been fitted

            Return:
                Power estimation for the given events value without units
        """
        return self.model.predict([self._extract_events_value(events)])[0]

    def cap_power_estimation(self, raw_target_power: PowerAPIQuantity, raw_global_power: PowerAPIQuantity):
        """ Cap target's power estimation to the global power estimation

            Args:
                raw_target_power: Target power estimation from the power model
                raw_global_power: Global power estimation from the power model

            Return:
                Capped power estimation (in same unit as raw_target_power) with its ratio over global power consumption
        """
        target_power = raw_target_power - (self.model.intercept_ * raw_target_power.units)
        global_power = raw_global_power - (self.model.intercept_ * raw_global_power.units)

        ratio = target_power / global_power if global_power > 0.0 * raw_global_power.units \
                                               and target_power > 0.0 * target_power.units \
            else (0.0 * raw_global_power.units)
        power = target_power if target_power > 0.0 * target_power.units else (0.0 * target_power.units)
        return power, ratio.magnitude

    def apply_intercept_share(self, target_power: PowerAPIQuantity, target_ratio: float):
        """ Apply the target's share of intercept from its ratio from the global power consumption

            Args:
                target_power: Target power estimation (in Watt)
                target_ratio: Target ratio over the global power consumption
            Return:
                Target power estimation including intercept (in same unit as target_power) and ratio over global power
                consumption
        """
        intercept = target_ratio * self.model.intercept_
        return target_power + (intercept * target_power.units)


class Smartwatts(Formula):
    """ This formula computes per-target power estimations using hardware performance counters """

    def __init__(self, config: SmartWattsFormulaConfig) -> None:
        """ Creates a smartwatts formula

            Args:

        """
        super().__init__()
        self.config = config
        self.ticks = OrderedDict()  # Dictionary with timestamp as key and Dict as values
        #  values Dict have target as key and Report as value
        self.sensor = None
        self.models = self._gen_models_dict()

    def process_report(self, report: Report):
        """ Required method for processing data as an observer of a source

            Args:
                report: The operator (e.g. a destination) that will process the output of the formula
        """

        self.ticks.setdefault(report.get_timestamp(), {}).update({report.get_target(): report})
        self.sensor = report.get_sensor()

        # start to process the oldest tick only after receiving at least 5 ticks.
        # we wait before processing the ticks in order to mitigate the possible delay of the sensor/database.
        if self.config.real_time_mode:
            if len(self.ticks) > 2:
                power_reports, formula_reports = self._process_oldest_tick()

                # We submit the observers of the formula
                self.submit_reports(power_reports)
        else:
            if len(self.ticks) > 5:
                power_reports, formula_reports = self._process_oldest_tick()

                # We submit the observers of the formula
                self.submit_reports(power_reports)

    def _gen_models_dict(self) -> OrderedDict:
        """ Generate and returns a layered container to store per-frequency power models

            Args:

            Return:
                Initialized Ordered dict containing a power model for each frequency layer
        """
        return OrderedDict((freq, PowerModel(freq, self.config.history_window_size)) for freq in
                           self.config.cpu_topology.get_supported_frequencies())

    def _get_frequency_layer(self, frequency: PowerAPIQuantity) -> PowerAPIQuantity:
        """ Find and returns the nearest frequency layer for the given frequency

            Args:
                frequency: CPU frequency
            Return:
                Nearest frequency layer for the given frequency in MHz
        """
        last_layer_freq = 0
        for current_layer_freq in self.models.keys():
            if frequency.magnitude < current_layer_freq:
                return last_layer_freq * quantity.DEFAULT_FREQUENCY_UNIT
            last_layer_freq = current_layer_freq

        return last_layer_freq * quantity.DEFAULT_FREQUENCY_UNIT

    def compute_pkg_frequency(self, system_msr: Dict) -> PowerAPIQuantity:
        """ Compute the average package frequency

            Args:
                system_msr: MSR events group of System target

            Return:
                Average frequency of the Package
        """
        return (self.config.cpu_topology.get_base_frequency() * system_msr[APERF_EVENT]) / system_msr[MPERF_EVENT]

    def get_power_model(self, system_core: Dict):
        """ Fetch the suitable power model for the current frequency

            Args:
                system_core: Core events group of System target
            Return:
                Power model to use for the current frequency
        """
        return self.models[self._get_frequency_layer(self.compute_pkg_frequency(system_core)).magnitude]

    def submit_reports(self, reports: list):
        """ Send the report to the formula observers

            Args:
                reports: List of reports to be submitted
        """

        for observer in self.observers:
            for current_report in reports:
                observer.on_next(current_report)

    def _process_oldest_tick(self):
        """ Process the oldest tick stored in the stack and generate power reports for the running target(s)

            Return :
                Power reports of the running target(s)
        """
        timestamp, hwpc_reports = self.ticks.popitem(last=False)

        # reports of the current tick
        power_reports = []
        formula_reports = []

        # prepare required events group of Global target
        try:
            global_report = hwpc_reports.pop('all')
        except KeyError:
            # cannot process this tick without the reference measurements
            return power_reports, formula_reports

        rapl = self._gen_rapl_events_group(global_report)
        avg_msr = self._gen_msr_events_group(global_report)
        global_core = self._gen_agg_core_report_from_running_targets(hwpc_reports)

        # compute RAPL power report TODO How to compute the error here
        rapl_power = rapl[self.config.rapl_event]
        current_used_power_unit = rapl_power.units
        power_reports.append(self._gen_power_report(timestamp=timestamp, target=RAPL_GROUP, error=0,
                                                    formula=self.config.rapl_event, raw_power=0.0, power=rapl_power,
                                                    ratio=1.0, metadata={}))

        if not global_core:
            return power_reports, formula_reports

        # fetch power model to use
        pkg_frequency = self.compute_pkg_frequency(avg_msr)
        model = self.get_power_model(avg_msr)

        # compute Global target power report
        try:
            # TODO using rapl_power.units is ok here ?
            raw_global_power = model.compute_power_estimation(global_core) * current_used_power_unit

            # compute power model error from reference TODO this error is ok for global ?
            model_error = fabs(rapl_power.magnitude - raw_global_power.magnitude) * current_used_power_unit

            power_reports.append(self._gen_power_report(timestamp=timestamp, target=GLOBAL_GROUP, formula=model.hash,
                                                        raw_power=raw_global_power, power=raw_global_power, ratio=1.0,
                                                        metadata={}, error=model_error))
        except NotFittedError:
            model.store_report_in_history(rapl_power, global_core)
            model.learn_power_model(self.config.min_samples_required, 0.0, self.config.cpu_topology.tdp.to(W).magnitude)
            return power_reports, formula_reports

        # compute per-target power report
        for target_name, target_report in hwpc_reports.items():
            target_core = self._gen_core_events_group(target_report)
            raw_target_power = model.compute_power_estimation(target_core) * current_used_power_unit
            target_power, target_ratio = model.cap_power_estimation(raw_target_power, raw_global_power)
            target_power = model.apply_intercept_share(target_power, target_ratio)
            power_reports.append(
                self._gen_power_report(
                    timestamp=timestamp,
                    target=target_name,
                    formula=model.hash,
                    raw_power=raw_target_power,
                    power=target_power,
                    ratio=target_ratio,
                    metadata=target_report.get_metadata(),
                    error=fabs((target_power - raw_global_power).magnitude) * current_used_power_unit
                ))

        # store global report
        model.store_report_in_history(rapl_power, global_core)

        # learn new power model if error exceeds the error threshold
        if model_error > self.config.error_threshold:
            model.learn_power_model(self.config.min_samples_required, 0.0, self.config.cpu_topology.tdp.to(W).magnitude)

        # store information about the power model used for this tick
        formula_reports.append(self._gen_formula_report(timestamp, pkg_frequency, model, model_error))
        return power_reports, formula_reports

    def _gen_formula_report(self, timestamp: datetime, pkg_frequency: PowerAPIQuantity, model: PowerModel, error: int):
        """ Generate a formula report using the given parameters

            Args:
                timestamp: Timestamp of the measurements
                pkg_frequency: Package average frequency
                Power model used for the estimation
                Error rate of the model
            Formula report filled with the given parameters
        """
        metadata = {
            'scope': self.config.scope.value,
            'socket': self.config.socket_domain_value,
            'layer_frequency': model.frequency,
            'pkg_frequency': pkg_frequency,
            'samples': len(model.history),
            'id': model.id,
            'error': error,
            'intercept': model.model.intercept_,
            'coef': str(model.model.coef_)
        }
        return Report.create_report_from_values(timestamp=timestamp, sensor=self.sensor, target=model.hash,
                                                metadata=metadata)

    def _gen_power_report(self, timestamp: datetime, target: str, formula: str, raw_power: PowerAPIQuantity,
                          error: PowerAPIQuantity,
                          power: PowerAPIQuantity,
                          ratio: float, metadata: Dict):

        """ Generate a power report using the given parameters

            Args:
                timestamp: Timestamp of the measurements
                target: Target name
                formula: Formula identifier
                power: Power estimation
            Return:
                Power report filled with the given parameters
        """
        metadata.update({
            'scope': self.config.scope.value,
            'socket': self.config.socket_domain_value,
            'formula': formula,
            'ratio': ratio,
            'predict': raw_power,
            'error': error,
        })
        return PowerReport.create_report_from_values(timestamp=timestamp, sensor=self.sensor, target=target,
                                                     power=power,
                                                     metadata=metadata)

    def _gen_rapl_events_group(self, system_report: HWPCReport):
        """ Generate an events group with the RAPL reference event converted in Watts for the current socket

            Args:
                system_report: The HWPC report of the System target
            Return:
                A dictionary containing the RAPL reference event with its value converted in Watts
        """

        # Get the dictionary of events for rapl>self.socket
        # the index is a tuple with format (timestamp, sensor, target,groups,socket,core)

        # Look for the values related to RAPL

        try:
            # if not system_report.index.is_monotonic_increasing:
            #    system_report = system_report.sort_index()
            rapl_report = system_report.loc[system_report.get_timestamp(), system_report.get_sensor(),
                                            system_report.get_target(), RAPL_GROUP, self.config.socket_domain_value]
        except KeyError:
            raise SmartWattsException(msg=create_exception_message_missing_index(entity_name=
                                                                                 self.config.socket_domain_value,
                                                                                 group_name=RAPL_GROUP,
                                                                                 entity_type="socket"))

        # event_value = system_report.loc[(system_report.get_timestamp(), system_report.get_sensor(),
        #                                 system_report.get_target()), 'rapl', self.socket].at[self.config.rapl_event]
        try:
            event_value = rapl_report[self.config.rapl_event][
                rapl_report.index[0]]  # The column name is the rapl_event name

            energy = ldexp(event_value, -32) / (self.config.reports_frequency.to(ms).magnitude / 1000)
        except KeyError:
            raise SmartWattsException(msg=create_exception_message_missing_index(entity_name=
                                                                                 self.config.rapl_event,
                                                                                 group_name=RAPL_GROUP,
                                                                                 entity_type="rapl event"))

        return {self.config.rapl_event: energy * W}

    def _gen_msr_events_group(self, system_report: HWPCReport):
        """ Generate an events group with the average of the MSR counters for the current socket

            Args:
                system_report: The HWPC report of the System target
            Return:
                A dictionary containing the average of the MSR counters
        """
        mrs_average_values_dict = defaultdict(int)

        # We get the mrs values
        try:
            mrs_report = system_report.loc[system_report.get_timestamp(), system_report.get_sensor(),
                                           system_report.get_target(), MSR_GROUP, self.config.socket_domain_value]
        except KeyError:
            raise SmartWattsException(msg=create_exception_message_missing_index(entity_name=
                                                                                 self.config.socket_domain_value,
                                                                                 group_name=MSR_GROUP,
                                                                                 entity_type="socket"))

        for event_name in mrs_report.columns:  # We compute the average
            mrs_average_values_dict[event_name] = mrs_report[event_name].mean()

        return mrs_average_values_dict

    def _gen_core_events_group(self, report: HWPCReport):
        """ Generate an events group with Core events for the current socket

            The events value are the sum of the value for each CPU.

            Args:
                report: The HWPC report of any target

            Return:
                A dictionary containing the Core events of the current socket
        """
        # We get the core values
        try:

            core_event_report = report.loc[report.get_timestamp(), report.get_sensor(),
                                           report.get_target(), CORE_GROUP, self.config.socket_domain_value]
        except KeyError:
            raise SmartWattsException(msg=create_exception_message_missing_index(entity_name=
                                                                                 self.config.socket_domain_value,
                                                                                 group_name=CORE_GROUP,
                                                                                 entity_type="socket"))

        core_events_group_dict = defaultdict(int)

        for event_name in core_event_report.columns:  # We add all the events_values uf they are to related to time
            if not event_name.startswith(TIME_EVENT_PREFIX):
                core_events_group_dict[event_name] = core_event_report[event_name].sum()

        return core_events_group_dict

    def _gen_agg_core_report_from_running_targets(self, targets_report):
        """ Generate an aggregate Core events group of the running targets for the current socket

            Args:
                targets_report: List of Core events group of the running targets

            Return:
                A dictionary containing an aggregate of the Core events for the running targets of the current socket
        """
        agg_core_events_group_dict = defaultdict(int)
        for _, target_report in targets_report.items():
            for event_name, event_value in self._gen_core_events_group(target_report).items():
                agg_core_events_group_dict[event_name] += event_value

        return agg_core_events_group_dict
