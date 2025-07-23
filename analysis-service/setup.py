from setuptools import setup, find_packages

setup(
    name="analysis-service",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "httpx",
        "python-dotenv",
        "mongomock",
        "google-generativeai",
        "cryptography",
        "pymongo",
        "mongoengine",
    ],
    python_requires=">=3.8",
) 