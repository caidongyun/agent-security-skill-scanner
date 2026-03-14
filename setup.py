from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-security-scanner",
    version="2.0.1-beta",
    author="Security Team",
    author_email="security@example.com",
    description="AI Agent Skill Security Scanner - Detect malicious skills, backdoor code, permission abuse (Beta Version)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caidongyun/agent-security-skill-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "agent-security-scanner=cli:main",
        ],
    },
    keywords="security agent scanner malware-detection ai-security beta",
    project_urls={
        "Bug Tracker": "https://github.com/caidongyun/agent-security-skill-scanner/issues",
        "Documentation": "https://github.com/caidongyun/agent-security-skill-scanner/blob/master/README.md",
        "Source": "https://github.com/caidongyun/agent-security-skill-scanner",
    },
)
