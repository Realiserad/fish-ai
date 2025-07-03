# -*- coding: utf-8 -*-

from os import path
import sys
from configparser import ConfigParser
import os


def get_config_path():
    if 'XDG_CONFIG_HOME' in os.environ:
        return path.expandvars('$XDG_CONFIG_HOME/fish-ai.ini')
    else:
        return path.expanduser('~/.config/fish-ai.ini')


def lookup_setting():
    print(get_config(sys.argv[1] or ''))


def get_config(key):
    if not config.has_section('fish-ai'):
        # There is no configuration file or the user made a mistake.
        # Just return 'None' here to simplify testing.
        return None

    active_section = config.get(section='fish-ai', option='configuration')

    if config.has_option(section=active_section, option=key):
        return path.expandvars(config.get(section=active_section, option=key))

    if config.has_option(section='fish-ai', option=key):
        return path.expandvars(config.get(section='fish-ai', option=key))

    if key == 'api_key' or key == 'password':
        # If not specified in the configuration, try to load from keyring
        import keyring
        return keyring.get_password('fish-ai', active_section)

    return None


config = ConfigParser()
config.read(get_config_path())
