# -*- coding: utf-8 -*-

import re
import base64


def redact(messages):
    for message in messages:
        message['content'] = redact_content(message['content'])
    return messages


def redact_content(content):
    r = content
    r = redact_cli_parameter('api-key', r)
    r = redact_cli_parameter('key', r)
    r = redact_cli_parameter('password', r)
    r = redact_cli_parameter('passphrase', r)
    r = redact_cli_parameter('secret', r)
    r = redact_pem_encoded_private_key(r)
    r = redact_pem_encoded_private_key_block(r)
    r = redact_base64_data(r)
    return r


def redact_cli_parameter(param, content):
    pattern = r'--{param}([= ])(["\']?)\S+\2'.format(
        param=param)
    replace_with = r'--{param}\1\2<REDACTED>\2'.format(
        param=param)
    return re.sub(
        pattern,
        replace_with,
        content)


def redact_pem_encoded_private_key(content):
    pattern = (r'-----BEGIN ([A-Z0-9]+) PRIVATE KEY-----\n'
               r'[\s\S]+\n'
               r'-----END \1 PRIVATE KEY-----')
    replace_with = (r'-----BEGIN \1 PRIVATE KEY-----\n'
                    r'<REDACTED>\n'
                    r'-----END \1 PRIVATE KEY-----')
    return re.sub(
        pattern,
        replace_with,
        content,
        flags=re.DOTALL)


def redact_pem_encoded_private_key_block(content):
    pattern = (r'-----BEGIN ([A-Z0-9]+) PRIVATE KEY BLOCK-----\n'
               r'[\s\S]+\n'
               r'-----END \1 PRIVATE KEY BLOCK-----')
    replace_with = (r'-----BEGIN \1 PRIVATE KEY BLOCK-----\n'
                    r'<REDACTED>\n'
                    r'-----END \1 PRIVATE KEY BLOCK-----')
    return re.sub(
        pattern,
        replace_with,
        content,
        flags=re.DOTALL)


def redact_base64_data(content):
    pattern = r'["\']([A-Za-z0-9+\\/=]+={0,2})["\']'

    def redact_match(match):
        encoded_string = match.group(1)
        try:
            base64.b64decode(encoded_string)
            return r'"<REDACTED>"'
        except base64.binascii.Error:
            return match.group(0)

    return re.sub(pattern, redact_match, content)
