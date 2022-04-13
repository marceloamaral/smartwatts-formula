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
from powerapi.exception import PowerAPIExceptionWithMessage


##############################
#
# Classes
#
##############################

class SmartWattsException(PowerAPIExceptionWithMessage):
    """ SmartWattsException class with message to indicate problems related with SmartWatts """

    def __init__(self, msg):
        super().__init__(msg)


##############################
#
# Functions
#
##############################
def create_exception_message_missing_index(entity_name: str, group_name: str, entity_type: str) -> str:
    """ Creates a messaage for indicating a problem with an index

        Args:
            entity_name: The name of entity that produces a problem inside the index (e.g., rapl event, core)
            group_name: The group associated with the index (e.g., rapl, core)
            entity_type: The type of the entity (rapl event, socket,
        Return:
            A message indicating the index problem
    """
    return "There is a problem with the HWPCReport. An index for the {} {} in {} group cannot be found".format(
        entity_name, entity_type, group_name)
