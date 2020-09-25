===
otc
===

Oblivious transfer (OT) communications protocol message/response functionality implementations based on Ed25519 primitives, including both pure-Python and libsodium-based variants.

|pypi| |travis| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/otc.svg
   :target: https://badge.fury.io/py/otc
   :alt: PyPI version and link.

.. |travis| image:: https://travis-ci.com/nthparty/otc.svg?branch=master
    :target: https://travis-ci.com/nthparty/otc

.. |coveralls| image:: https://coveralls.io/repos/github/nthparty/otc/badge.svg?branch=master
   :target: https://coveralls.io/github/nthparty/otc?branch=master

Purpose
-------
This library provides data structures and methods for a basic `oblivious transfer (OT) <https://en.wikipedia.org/wiki/Oblivious_transfer>`_ communications protocol defined in `work by Chou and Orlandi <https://eprint.iacr.org/2015/267.pdf>`_. Thanks to the underlying `oblivious <https://pypi.org/project/oblivious/>`_ library, users of this library have the option of relying either on pure Python implementations of cryptographic primitives or on wrappers for `libsodium <https://github.com/jedisct1/libsodium>`_.

Package Installation and Usage
------------------------------
The package is available on PyPI::

    python -m pip install otc

The library can be imported in the usual ways::

    import otc
    from otc import *

Testing and Conventions
-----------------------
All unit tests are executed and their coverage is measured when using `nose <https://nose.readthedocs.io/>`_ (see ``setup.cfg`` for configution details)::

    nosetests

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`_::

    python otc/otc.py -v

Style conventions are enforced using `Pylint <https://www.pylint.org/>`_::

    pylint otc

Contributions
-------------
In order to contribute to the source code, open an issue or submit a pull request on the GitHub page for this library.

Versioning
----------
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`_.
