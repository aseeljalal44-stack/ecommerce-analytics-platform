"""
تثبيت حزمة تحليل المتاجر الإلكترونية
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="ecommerce-analytics",
    version="1.0.0",
    author="Ecommerce Analytics Team",
    author_email="info@ecom-analytics.com",
    description="نظام تحليل المتاجر الإلكترونية المتنوعة",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ecommerce-analytics",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ecom-analytics=app.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ecommerce-analytics/issues",
        "Source": "https://github.com/yourusername/ecommerce-analytics",
        "Documentation": "https://github.com/yourusername/ecommerce-analytics/wiki"
    },
)