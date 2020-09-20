from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="otp",
    version="0.1.0",
    packages=["otp",],
    install_requires=["pynacl", "oblivious",],
    license="MIT",
    url="https://github.com/nthparty/otp",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Oblivious transfer (OT) protocol message/response "+\
                "functionality implementations based on Ed25519 primitives.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="nose.collector",
    tests_require=["nose"],

