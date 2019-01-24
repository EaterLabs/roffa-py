from setuptools import setup, find_packages

print(open(__file__[:-8] + "requirements.txt", 'r').readlines())

setup(
    name='roffa',
    version='1.0.0',
    py_modules=find_packages(),
    install_requires=map(lambda r: r.strip(), open(__file__[:-8] + "requirements.txt", 'r').readlines()),
    entry_points='''
        [console_scripts]
        roffa=bin.roffa:cli
    ''',
)
