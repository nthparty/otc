from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="otc",
    version="1.0.0",
    packages=["otc",],
    install_requires=[
        "pynacl~=1.4.0",
        "oblivious~=3.0.1"
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
