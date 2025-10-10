"""Setup script for photo_organizer package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

setup(
    name="photo-organizer",
    version="1.0.0",
    author="Austin Serb",
    author_email="contact@serbyte.com",
    description="AI-powered construction photo organization pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/austinserb/photo-organizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.0.0",
        "pillow-heif>=0.13.0",
        "imagehash>=4.3.0",
        "tqdm>=4.65.0",
        "python-slugify>=8.0.0",
        "exifread>=3.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "ai_classification": ["openai>=1.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "pylint>=2.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "photo-organizer=photo_organizer.cli:main",
        ],
    },
)
