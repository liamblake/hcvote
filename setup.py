from setuptools import setup

setup(
    name="Hare-Clark Vote Counter",
    url="https://github.com/LiamBlake/Hare-Clark-VoteCounter",
    author="Liam Blake",
    author_email="",
    packages=["hcvote"],
    install_requires=["pandas==1.2.4"],
    extras_require={"dev": ["black", "isort", "flake8", "pytest", "pytest-cov"]},
    version="0.1",
    license="GNU",
    description="Implementation of Hare-Clark voting system.",
    long_description=open("README.md").read(),
)
