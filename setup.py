import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shiftleft-scan-reports",
    version="1.0.3",
    author="Team ShiftLeft",
    author_email="hello@shiftleft.io",
    description="Library for producing html reports from ShiftLeft Scan or AppThreat scan results",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShiftLeftSecurity/scan-reports",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["Jinja2"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Utilities",
        "Topic :: Security",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
