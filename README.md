Generating Bitcoin addresses from an extended public key (Copay etc)
====================================================================

This document describes creating public Bitcoin addresses from the following
Copay config:

![](https://github.com/koirikivi/address-generation-poc/blob/master/img/copay-config.png)

The extended public key is saved in the file `extended_public_key`:

```bash
$ cat extended_public_key
xpub6DCMq6dp8Bms7L1ninNztsMJDRU997GBdNa4LjdQCS6Gd61uxZC7zsGw7pcZr3SpsjEBcUyGp3URrJRv1EkSS448BPPmHRbWDhWkFWFFXLp
```

Requirements
------------

This document uses the Python-based [pycoin](https://github.com/richardkiss/pycoin) library,
which provides an both a command line interface and an API for creating the
addresses. The library will be installed directly from github, since the CLI
was broken in the newest release on PIP.

```bash
$ pip install git://github.com/richardkiss/pycoin.git@2c7e3df80379ff937ce02c1d8779a5dd7e277e15#egg=pycoin
```

API
---

The Pycoin API can be used like this:

```python
>>> from pycoin.key import Key
>>> extended_public_key = open("extended_public_key").read().strip()
>>> key = Key.from_text(extended_public_key)
>>> key
<xpub6DCMq6dp8Bms7L1ninNztsMJDRU997GBdNa4LjdQCS6Gd61uxZC7zsGw7pcZr3SpsjEBcUyGp3URrJRv1EkSS448BPPmHRbWDhWkFWFFXLp>
>>> key.subkey(0).subkey(0)
<xpub6FhY7Gh1vqJHQ9DKUgKcxfBQ1KUfnRNoxALzGTYyhzfSeoNDGWyRk8Ha7MHypYGFhnc6tkCtsAr6QsJTtgejB28jotPpG1DzhdT96gXfFka>
>>> key.subkey(0).subkey(0).address()
u'1F79CzvNFezc4dVw7JNwhX1KL6DquDzuz9'
>>> key.subkey_for_path("0/0")  # alias for key.subkey(0).subkey(0)
<xpub6FhY7Gh1vqJHQ9DKUgKcxfBQ1KUfnRNoxALzGTYyhzfSeoNDGWyRk8Ha7MHypYGFhnc6tkCtsAr6QsJTtgejB28jotPpG1DzhdT96gXfFka>
>>> key.subkey_for_path("0/0").address()
u'1F79CzvNFezc4dVw7JNwhX1KL6DquDzuz9'
>>> key.subkey_for_path("0/1").address()
u'1CUP4FnYqYj2BeaMCSQ3939xKM2k5GAJxL'
```

CLI
---

pycoin installs a script called `genwallet`, that can be used the following
way:

```bash
genwallet -f <public key path> -s '0/<iteration>' -a
```

For an example:

```bash
$ genwallet -f extended_public_key -s '0/0' -a
1F79CzvNFezc4dVw7JNwhX1KL6DquDzuz9
$ genwallet -f extended_public_key -s '0/1' -a
1CUP4FnYqYj2BeaMCSQ3939xKM2k5GAJxL
$ genwallet -f extended_public_key -s '0/10' -a
1KAuMVWFSkY9cd3wij6xk2UbFsg2H1YDi
```

[More information about using the script can be found here.](http://blog.richardkiss.com/?p=313)
