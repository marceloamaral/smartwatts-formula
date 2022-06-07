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
# Last modified : 13 April 2022

##############################
#
# Classes
#
##############################
from typing import Optional, Dict

import pymongo
from powerapi.rx import BaseSource, Destination
from powerapi.rx.hwpc_reports_group import HWPCReportsGroup
from rx.core import Observer
from rx.core.abc import Scheduler


class SimpleSource(BaseSource):
    """Simple source for testing purposes"""

    def __init__(self, reports_group: HWPCReportsGroup) -> None:
        """ Creates a simple source that sends one report to the formula

        Args:

        """
        super().__init__()
        self.reports_group = reports_group

    def subscribe(self, operator: Observer, scheduler: Optional[Scheduler] = None):
        """ Required method for retrieving data from a source by a Formula

            Args:
                operator: The operator (e.g. a formula or log)  that will process the data
                scheduler: Used for parallelism. Not used for the time being

        """
        operator.on_next(self.reports_group)

    def close(self):
        """ Closes the access to the data source"""
        pass


class MultipleReportSource(BaseSource):
    """ Source sending several reports  testing purposes """

    def __init__(self, reports_groups: list) -> None:
        """ Creates a fake source

        Args:

        """
        super().__init__()
        self.reports_groups = reports_groups

    def subscribe(self, operator: Observer, scheduler: Optional[Scheduler] = None):
        """ Required method for retrieving data from a source by a Formula

            Args:
                operator: The operator (e.g. a formula or log)  that will process the data
                scheduler: Used for parallelism. Not used for the time being

        """
        for reports_group in self.reports_groups:
            operator.on_next(reports_group)

    def close(self):
        """ Closes the access to the data source"""
        pass


class SimpleReportDestination(Destination):
    """Simple destination for testing purposes"""

    def __init__(self) -> None:
        """ Creates a fake source

        Args:

        """
        super().__init__()
        self.reports_group = None

    def store_report(self, reports_group):
        """ Required method for storing a report

            Args:
                report: The report that will be stored
        """
        self.reports_group = reports_group

    def on_completed(self) -> None:
        pass

    def on_error(self, error: Exception) -> None:
        pass


class MultipleReportDestination(Destination):
    """Simple destination for testing purposes"""

    def __init__(self) -> None:
        """ Creates a fake source

        Args:

        """
        super().__init__()
        self.reports_groups = []

    def store_report(self, reports_group):
        """ Required method for storing a report

            Args:
                report: The report that will be stored
        """
        self.reports_groups.append(reports_group)

    def on_completed(self) -> None:
        pass

    def on_error(self, error: Exception) -> None:
        raise error


##############################
#
# Functions
#
##############################

def gen_mongodb_database_test(uri: str, db_name: str, collection_name: str, content_list=[Dict]):
    """ Prepares the database for testing purposes

        Args:
            uri: The uri for accessing mongo
            db_name: name of the monngodb to be set up
            collection_name: name of the collection to be created
            content_list : dict with the content of the database. It is a List of dicts

    """
    mongo = pymongo.MongoClient(uri)

    # We get the DATABASE. If it does not exist, it will be created
    db = mongo[db_name]

    # delete collection if it already exist
    db[collection_name].drop()
    db.create_collection(collection_name)

    # Insert the content

    for current_content in content_list:
        db[collection_name].insert_one(current_content)

    # Close the connection
    mongo.close()

