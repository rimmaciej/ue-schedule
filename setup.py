import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ue-schedule-tool",
    version="0.1.2",
    author="Maciej Rim",
    author_email="pypi@mrim.pl",
    description="Class schedule download library for UE Katowice",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rimmaciej/ue-schedule-tool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_required=["icalendar==4.0.3", "requests==2.22.0"],
)

