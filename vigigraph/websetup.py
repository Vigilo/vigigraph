# -*- coding: utf-8 -*-
"""Setup the vigigraph application"""

import logging

import transaction
from tg import config

from vigigraph.config.environment import load_environment
from vigilo.turbogears import populate_db 

__all__ = ['setup_app']

log = logging.getLogger(__name__)


def setup_app(command, conf, variables):
    """Place any commands to setup vigigraph here"""
    load_environment(conf.global_conf, conf.local_conf)
    populate_db()

