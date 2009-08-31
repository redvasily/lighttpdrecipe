from setuptools import setup, find_packages

setup(
    name="lighttpdrecipe",
    version='0.1',
    description='Buildout recipe for generating lighttpd configuration files',
    author='vasily sulatskov',
    author_email='redvasily@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        "Framework :: Buildout",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    install_requires=['setuptools', 'zc.recipe.egg', 'Jinja2'],
    entry_points = {'zc.buildout': ['default = lighttpdrecipe.recipe:Lighttpd']},
    zip_safe=False,
)
