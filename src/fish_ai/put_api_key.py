# -*- coding: utf-8 -*-

import sys
from configparser import ConfigParser

import keyring
from simple_term_menu import TerminalMenu

from fish_ai.config import get_config_path


def select_section(config, sections):
    if len(sections) == 1:
        return sections[0]
    else:
        options = [
            "{} (provided by {})".format(
                section, config.get(section=section, option="provider")
            )
            for section in sections
        ]
        terminal_menu = TerminalMenu(options, title="Select context")
        index = terminal_menu.show()
        if index is None or not isinstance(index, int):
            return
        return options[index].split(" ")[0]


def put_api_key():
    configuration_file = ConfigParser()
    configuration_file.read(get_config_path())
    sections = configuration_file.sections()
    if "fish-ai" in sections:
        sections.remove("fish-ai")
    selected_section = select_section(configuration_file, sections)

    if not selected_section:
        return

    if configuration_file.has_option(
        section=selected_section, option="api_key"
    ):
        # Move API key from the configuration to the keyring
        api_key = configuration_file.get(
            section=selected_section, option="api_key"
        )
        keyring.set_password("fish-ai", selected_section, api_key)
        configuration_file.remove_option(selected_section, "api_key")
        configuration_file.write(open(get_config_path(), "w"))
    else:
        # Ask for the API key and put it on the keyring
        p = f"Provide an API key for \033[92m{selected_section}\033[0m.\n🔑 "
        print(p, end="")
        sys.stdout.flush()
        api_key = sys.stdin.readline().strip()
        keyring.set_password("fish-ai", selected_section, api_key)

    print(
        (
            f"🔒 The API key for \033[92m{selected_section}\033[0m is now on "
            "your keyring."
        )
    )
