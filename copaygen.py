#!/usr/bin/env python
"""
An example script that generates public addresses from the kind of m-of-n HD
public addresses that Copay uses.

The gist of the code is the `bip32_hdm_addr` function from the pybitcointools
package, which is used like this:

    bip32_hdm_addr
        <list of extended pubkeys>,
        <number of required pubkeys (the m in m-of-n)>,
        <derivation path as list>
    )

Note that the first and third arguments must be given as lists (tuples or other
iterables won't do!)

So for an example, to generate the first public address that Copay would
generate for a 2-of-2 HDM wallet with the extended public keys stored in
variables pub1 and pub2, we would call the function as follows:

    >>> bip32_hdm_addr([pub1, pub2], 2, [0,0])
    '3GMCA3odvfcBG7sQRBNTeaPU4KTLwjaQxt'

Note that Copay seems to always derive the addresses from path 0/i, where i is
the current derivation iteration. As such, the following keys would be
generated like this:

    >>> bip32_hdm_addr([pub1, pub2], 2, [0,1])
    >>> bip32_hdm_addr([pub1, pub2], 2, [0,2])
    >>> bip32_hdm_addr([pub1, pub2], 2, [0,3])
    >>> bip32_hdm_addr([pub1, pub2], 2, [0,4])

And so on.

This file contains an example script that opens the localstorage file generated
by Copay and generates public addresses based on that. Example usage:

    # Open default copay profile and generate 100 public addresses
    # If there's more than one wallet, ask for the details interactively
    $ copaygen.py

    # Generate addresses from 100 to 150
    $ copaygen.py -s 100 -n 150

    # Open the wallet with id a00ec799-e905-4ffc- 9bd0-edecd19e181d<
    $ copaygen.py --walletid=a00ec799-e905-4ffc-9bd0-edecd19e181d

    # Specify the path to Copay's localstorage file
    $ copaygen.py --localstorage=~/copay/Local\ Storage/file__0.localstorage

Run `copaygen.py -h` for more info.

"""
from __future__ import unicode_literals, absolute_import, print_function
import argparse
import json
import os
import platform
import sys
import sqlite3
# the version of pybitcointools from github is installed as `bitcoin`, the
# version from pypi as `pybitcointools`
try:
    from bitcoin import bip32_hdm_addr
except ImportError:
    try:
        from pybitcointools import bip32_hdm_addr
    except ImportError:
        print("copaygen.py requires the pybitcointools package to run")
        sys.exit(1)


if sys.version_info[0] == 2:
    input = raw_input


def iter_copay_addresses(wallet, start, amount):
    pubkeys = [k["xPubKey"] for k in wallet["publicKeyRing"]]
    num_required = wallet["m"]
    for i in range(start, amount):
        yield bip32_hdm_addr(pubkeys, num_required, [0, i])


def get_default_copay_localstorage_path():
    system = platform.system()
    if system == 'Windows':
        base = os.path.join(os.getenv('LOCALAPPDATA'), 'copay')
    elif system == 'Darwin':
        base = os.path.expanduser("~/Library/Application Support/copay")
    elif system == 'Linux':
        base = os.path.expanduser("~/.config/copay")
    else:
        raise NotImplementedError('get_default_copay_localstorage_path not '
                                  'implemented for system "%s"' % system)
    return os.path.join(base, 'Local Storage', 'file__0.localstorage')


def get_copay_profile(localstorage_path):
    connection = sqlite3.connect(localstorage_path)
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT CAST(value as TEXT) from ItemTable where key = 'profile'")
        ret = cursor.fetchone()
        ret = ret[0]
    finally:
        connection.close()
    return json.loads(ret)


def get_copay_wallet(profile, walletid=None):
    wallets = profile["credentials"]

    def list_wallets(numbers=True):
        for i, wallet in enumerate(wallets):
            if numbers:
                print("[%s]" % i, end=" ")
            print("%s (%s-of-%s) (id: %s)" %
                (wallet["walletName"], wallet["m"], wallet["n"], wallet["walletId"]))

    if walletid:
        for wallet in wallets:
            if wallet["walletId"] == walletid:
                return wallet
        print("walletId '%s' not found! the following wallets were found:" %
               walletid)
        list_wallets(numbers=False)
        sys.exit(1)

    if len(wallets) == 0:
        print("No wallets found!")
        sys.exit(1)
    elif len(wallets) == 1:
        return wallets[0]

    print("Multiple wallets found - pick yours:")
    while True:
        list_wallets()
        choice = input("> ")
        try:
            return wallets[int(choice)]
        except (ValueError, IndexError):
            print("Pick a number between 0 and %s" % len(wallets))


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--localstorage", "-f", default=None,
                        help="Path to copay localstorage file")
    parser.add_argument("--walletid", "-w", default=None,
                        help="Wallet id")
    parser.add_argument("--start", "-s", default=0, type=int,
                        help="Start address generation from this address")
    parser.add_argument("--amount", "-n", default=100, type=int,
                        help="Create this many addresses")
    config = parser.parse_args(argv)

    localstorage_path = config.localstorage or \
                        get_default_copay_localstorage_path()
    if not os.path.exists(localstorage_path):
        print("copay localstorage path '%s' doesn't exist "
              "(try specifying with --localstorage?" % localstorage_path)
        sys.exit(1)
    profile = get_copay_profile(localstorage_path)
    wallet = get_copay_wallet(profile, config.walletid)
    address_iter = iter_copay_addresses(wallet, start=config.start, amount=config.amount)
    for address in address_iter:
        print(address)

if __name__ == "__main__":
    main()
