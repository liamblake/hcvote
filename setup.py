from setuptools import setup

setup(
    name="hcvote",
    url="https://github.com/LiamBlake/hcvote",
    author="Liam Blake",
    author_email="",
    packages=["hcvote"],
    install_requires=[],
    extras_require={
        "dev": ["black==21.9b0", "isort==5.9.3", "flake8==4.0.1", "mypy==0.910"],
        "test": ["pytest==6.2.5", "pytest-cov==3.0.0"],
    },
    version="0.1",
    license="GNU",
    description="The Hare-Clark electoral counting system, implemented in Python.",
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
)
