from setuptools import setup, find_packages

setup(
    name="DataPoolViewer",
    version="1.0.0",
    author="Guillaume Train",
    author_email="g.train@live.fr",
    description="A library intended to provide data visualization tools for PyDataCore.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/DataPoolViewer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.21",
        "pandas>=1.3",
        'termcolor~=2.5.0',
        "scipy>=1.7",
        "pyqtgraph>=0.12",
        "PySide6>=6.2",
        'setuptools~=75.2.0',
        'pytz~=2024.2',
        'six~=1.16.0',
        'tzdata~=2024.2',
        'python-dateutil~=2.9.0.post0',
        'tabulate~=0.9.0'
    ],
)
