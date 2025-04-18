from setuptools import setup, find_packages

# Read requirements.txt and clean up the requirements
with open('requirements.txt') as f:
    requirements = []
    for line in f:
        line = line.strip()
        # Skip empty lines or comments
        if line and not line.startswith('#'):
            # Remove any trailing comments and whitespace
            requirement = line.split('#')[0].strip()
            requirements.append(requirement)

setup(
    name="group_size",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
)