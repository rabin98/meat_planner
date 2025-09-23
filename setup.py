# Setup script per il progetto Meat Planner

from setuptools import find_packages, setup

setup(
    name="meat-planner",
    version="1.0.0",
    description="Applicazione Streamlit per la pianificazione dei pasti settimanali",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "meat-planner=meat_planner:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)