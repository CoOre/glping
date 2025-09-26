from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="glping",
    version="1.0.0",
    author="Vladimir Nosov",
    author_email="inosovvv@gmail.com",
    description="CLI-утилита для отслеживания событий в GitLab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/glping/glping",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "glping=glping.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "glping": ["*.txt", "*.md"],
    },
)