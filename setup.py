from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

setup(
    name="otc",
    version="2.0.0",
    packages=["otc",],
    install_requires=[
        "bcl~=2.0",
        "oblivious~=4.0"
    ],
    license="MIT",
    url="https://github.com/nthparty/otc",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Oblivious transfer (OT) communications protocol "+\
                "message/response functionality implementations "+\
                "based on Curve25519 primitives.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="nose.collector",
    tests_require=["nose"],
)
