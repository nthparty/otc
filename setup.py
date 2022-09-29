from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

name = "otc"
version = "4.0.0"

setup(
    name=name,
    version=version,
    packages=["otc",],
    install_requires=[
        "bcl~=2.3",
        "oblivious~=6.0"
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
)
