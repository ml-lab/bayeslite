# -*- coding: utf-8 -*-

#   Copyright (c) 2010-2016, MIT Probabilistic Computing Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import division

import contextlib
import itertools
import math
import numpy as np
import pytest

from cgpm.cgpm import CGpm
from cgpm.dummy.fourway import FourWay
from cgpm.dummy.piecewise import PieceWise
from cgpm.utils import general as gu

from bayeslite import bayesdb_open
from bayeslite import bayesdb_register_metamodel
from bayeslite.exception import BQLError
from bayeslite.metamodels.cgpm_metamodel import CGPM_Metamodel
from bayeslite.util import cursor_value


@contextlib.contextmanager
def smoke_bdb():
    with bayesdb_open(':memory:') as bdb:
        bdb.sql_execute('CREATE TABLE t (a, b, c, d, e)')

        for a, b, c, d, e in itertools.product(*([range(2)]*5)):
            # XXX Insert synthetic data generator here.
            bdb.sql_execute('''
                INSERT INTO t (a, b, c, d, e) VALUES (?, ?, ?, ?, ?)
            ''', (a, b, c, d, e))

        bdb.execute('''
            CREATE POPULATION p FOR t WITH SCHEMA (
                MODEL a, b, c, d, e AS NUMERICAL
            )
        ''')

        bdb.execute('CREATE METAMODEL m1 FOR p;')
        bdb.execute('INITIALIZE 10 MODELS FOR m1;')

        bdb.execute('CREATE METAMODEL m2 FOR p;')
        bdb.execute('INITIALIZE 10 MODELS FOR m2;')
        yield bdb

def test_estimate_cmi__ci_slow():
    with smoke_bdb() as bdb:
        bql = '''
            ESTIMATE MUTUAL INFORMATION OF a WITH b USING 10 SAMPLES
            BY p
        '''
        result = bdb.execute(bql).fetchall()
        assert len(result) == 1

        bql = '''
            ESTIMATE MUTUAL INFORMATION OF a WITH b
            BY p
            MODELED BY m1
        '''
        result = bdb.execute(bql).fetchall()
        assert len(result) == 1

        bql = '''
            ESTIMATE
                MUTUAL INFORMATION OF a WITH b
                    GIVEN (d, c = 1) USING 10 SAMPLES
            BY p;
        '''
        result = bdb.execute(bql).fetchall()
        assert len(result) == 1

        bql = '''
            ESTIMATE
                MUTUAL INFORMATION OF a WITH b GIVEN (c = 1) USING 10 SAMPLES
            BY p;
        '''
        result = bdb.execute(bql).fetchall()
        assert len(result) == 1

        bql = '''
            ESTIMATE
                MUTUAL INFORMATION OF a WITH b GIVEN (d) USING 10 SAMPLES
            BY p;
        '''
        result = bdb.execute(bql).fetchall()
        assert len(result) == 1
