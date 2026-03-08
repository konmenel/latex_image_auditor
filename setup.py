from setuptools import setup, find_packages

setup(
    name="latex-image-auditor",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'latex-image-auditor=latex_image_auditor.checker:main',
            'latexauditor=latex_image_auditor.checker:main',
        ],
    },
)