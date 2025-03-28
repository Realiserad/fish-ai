# -*- coding: utf-8 -*-

from fish_ai.redact import redact_content
import textwrap


def test_redact_api_key():
    input_str = '--api-key=sk-1234'
    expected_output = '--api-key=<REDACTED>'
    assert redact_content(input_str) == expected_output

    input_str = '--api-key sk-1234'
    expected_output = '--api-key <REDACTED>'
    assert redact_content(input_str) == expected_output

    input_str = "--api-key 'sk-1234'"
    expected_output = "--api-key '<REDACTED>'"
    assert redact_content(input_str) == expected_output

    input_str = '--api-key "sk-1234"'
    expected_output = '--api-key "<REDACTED>"'
    assert redact_content(input_str) == expected_output


def test_redact_password():
    input_str = 'login --username foo --password=samba123'
    expected_output = 'login --username foo --password=<REDACTED>'
    assert redact_content(input_str) == expected_output

    input_str = 'login --username foo --password samba123'
    expected_output = 'login --username foo --password <REDACTED>'
    assert redact_content(input_str) == expected_output

    input_str = "login --username foo --password 'samba123'"
    expected_output = "login --username foo --password '<REDACTED>'"
    assert redact_content(input_str) == expected_output

    input_str = 'login --username foo --password "samba123!"'
    expected_output = 'login --username foo --password "<REDACTED>"'
    assert redact_content(input_str) == expected_output


def test_redact_multiple_cli_parameters():
    input_str = textwrap.dedent("""\
        Here are some login commands for cucumber, tomato and pepper:

        login --username cucumber --password cucumber
        login --username tomato --api-key tomato""")
    expected_output = textwrap.dedent("""\
        Here are some login commands for cucumber, tomato and pepper:

        login --username cucumber --password <REDACTED>
        login --username tomato --api-key <REDACTED>""")
    assert redact_content(input_str) == expected_output


def test_redact_pem_encoded_private_key():
    input_str = textwrap.dedent("""\
        -----BEGIN RSA PRIVATE KEY-----
        Proc-Type: 4,ENCRYPTED
        DEK-Info: DES-EDE3-CBC,B1F1B3F5F1B4F1B3
        6+jVglcOq6vNfwt/Q+X9m
        -----END RSA PRIVATE KEY-----""")
    expected_output = textwrap.dedent("""\
        -----BEGIN RSA PRIVATE KEY-----
        <REDACTED>
        -----END RSA PRIVATE KEY-----""")
    assert redact_content(input_str) == expected_output


def test_redact_content():
    input_str = textwrap.dedent("""\
        Autocomplete the following command:

        key import --file key.pem --password samba123

        You may use the following command line history to personalize the
        response:

        key import --file key.pem --password samba123 --server server1.com
        key import --file key.pem --password samba123 --server server2.com

        The content of key.pem is:

        -----BEGIN PGP PRIVATE KEY BLOCK-----
        123456789123456789012345678901234567890123456789012345678901234
        123456789123456789012345678901234567890123456789012345678901234
        123456789123456789012345678901234567890123456789012345678901234
        -----END PGP PRIVATE KEY BLOCK-----""")
    expected_output = textwrap.dedent("""\
        Autocomplete the following command:

        key import --file key.pem --password <REDACTED>

        You may use the following command line history to personalize the
        response:

        key import --file key.pem --password <REDACTED> --server server1.com
        key import --file key.pem --password <REDACTED> --server server2.com

        The content of key.pem is:

        -----BEGIN PGP PRIVATE KEY BLOCK-----
        <REDACTED>
        -----END PGP PRIVATE KEY BLOCK-----""")
    assert redact_content(input_str) == expected_output


def test_nothing_to_redact():
    input_str = 'Nothing to redact here...'
    assert redact_content(input_str) == input_str


def test_do_not_redact():
    input_str = 'import-key --keyring /etc/apk/keys/foo.gpg'
    assert redact_content(input_str) == input_str
