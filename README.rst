===
otc
===

Oblivious transfer (OT) communications protocol message/response functionality implementations based on `Curve25519 <https://cr.yp.to/ecdh.html>`__ and the `Ristretto <https://ristretto.group>`__ group.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/otc.svg
   :target: https://badge.fury.io/py/otc
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/otc/badge/?version=latest
   :target: https://otc.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/nthparty/otc/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/nthparty/otc/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/nthparty/otc/badge.svg?branch=main
   :target: https://coveralls.io/github/nthparty/otc?branch=main
   :alt: Coveralls test coverage summary.

Purpose
-------
This library provides data structures and methods for a basic `oblivious transfer (OT) <https://en.wikipedia.org/wiki/Oblivious_transfer>`__ communications protocol defined in `work by Chou and Orlandi <https://eprint.iacr.org/2015/267>`__. Thanks to the underlying `oblivious <https://pypi.org/project/oblivious>`__ library, method implementations rely on cryptographic primitives found within the `libsodium <https://github.com/jedisct1/libsodium>`__ library.

For more information and background about the underlying mathematical structures and primitives, consult materials about `Curve25519 <https://cr.yp.to/ecdh.html>`__, the `Ristretto <https://ristretto.group>`__ group, and the related `Ed25519 <https://ed25519.cr.yp.to>`__ system.

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/otc>`__::

    python -m pip install otc

The library can be imported in the usual manner::

    import otc
    from otc import *

Example
^^^^^^^
Suppose that a sender wants to send exactly one of two payloads to a receiver (such as one of two decryption keys). Furthermore, the receiver does not want to reveal to the sender which of the two payloads they chose to receive. To begin, the sender creates a sender object `s` with a public key `s.public` that should be sent to the receiver::

    >>> import otc
    >>> s = otc.send()

The receiver can then create a receiver object and use `s.public` to make an encrypted selection that the sender cannot decrypt::

    >>> r = otc.receive()
    >>> selection = r.query(s.public, 1)

The sender can then send two encrypted replies based on the receiver's selection; the receiver will *only be able to decrypt the pre-selected payload*, and the sender *does not know* which of the two payloads can be decrypted by the receiver::

    >>> replies = s.reply(selection, bytes([0] * 16), bytes([255] * 16))

Finally, the receiver can decrypt their chosen payload::

    >>> r.elect(s.public, 1, *replies) == bytes([255] * 16) # Second message.
    True

See the article `Privacy-Preserving Information Exchange Using Python <https://medium.com/nthparty/privacy-preserving-information-exchange-using-python-1a4a11bed3d5>`__ for a more detailed presentation of the this example.

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__::

    python -m pip install .[docs,lint]

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__::

    python -m pip install .[docs]
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details)::

    python -m pip install .[test]
    python -m pytest

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`__::

    python otc/otc.py -v

Style conventions are enforced using `Pylint <https://pylint.pycqa.org>`__::

    python -m pip install .[lint]
    python -m pylint otc

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/nthparty/otc>`__ for this library.

Versioning
^^^^^^^^^^
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/otc>`__ by a package maintainer. First, install the dependencies required for packaging and publishing::

    python -m pip install .[publish]

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions. Create and push a tag for this version (replacing ``?.?.?`` with the version number)::

    git tag ?.?.?
    git push origin ?.?.?

Remove any old build/distribution files. Then, package the source into a distribution archive::

    rm -rf build dist *.egg-info
    python -m build --sdist --wheel .

Finally, upload the package distribution archive to `PyPI <https://pypi.org>`__::

    python -m twine upload dist/*
