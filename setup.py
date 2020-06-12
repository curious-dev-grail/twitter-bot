from setuptools import setup, find_packages
import os

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt"), "r"
) as f:
    dependencies = f.read().split("\n")

setup(
    name="twitter-bot",
    author="Gaurav",
    description="A Tool to Scrape Tweets",
    version="0.2",
    packages=find_packages(),
    py_modules=["twitterbot.cli", "twitterbot.twitterbot", "twitterbot.exceptions"],
    install_requires=dependencies,
    entry_points={"console_scripts": ["twitter-bot=twitterbot.cli:main"]},
)
