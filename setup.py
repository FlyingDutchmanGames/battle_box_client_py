import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="battle_box_client",
    version="0.0.1",
    author="Grant Powell",
    description="Battle Box Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FlyingDutchmanGames/battle_box_client_py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
