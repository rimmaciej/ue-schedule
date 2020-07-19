import setuptools

from ue_schedule import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ue-schedule",
    version=VERSION,
    author="Maciej Rim",
    author_email="pypi@mrim.pl",
    description="UE Katowice class schedule utility library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rimmaciej/ue-schedule",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["icalendar==4.0.6", "requests==2.24.0"],
)
