# -*- coding: utf-8 -*-

from configparser import ConfigParser

from simple_term_menu import TerminalMenu

from fish_ai.config import get_config_path


def switch_context():
    config = ConfigParser()
    config.read(get_config_path())
    sections = config.sections()
    if "fish-ai" in sections:
        sections.remove("fish-ai")
    options = [
        "{} (provided by {})".format(
            section, config.get(section=section, option="provider")
        )
        for section in sections
    ]
    terminal_menu = TerminalMenu(options, title="Select context")
    index = terminal_menu.show()
    if index is None or isinstance(index, tuple):
        return
    active_section = options[index].split(" ")[0]
    config.set(section="fish-ai", option="configuration", value=active_section)
    config.write(open(get_config_path(), "w"))
    print("💪 Now using '{}'.".format(active_section))
