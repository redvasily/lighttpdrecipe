from setuptools import setup, find_packages

setup(
    name="lighttpdrecipe",
    version='0.1.2',
    description='Buildout recipe for generating lighttpd configuration files',
    author='vasily sulatskov',
    author_email='redvasily@gmail.com',
    url='http://github.com/redvasily/lighttpdrecipe/tree/master/',
    download_url='http://cloud.github.com/downloads/redvasily/lighttpdrecipe/',
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
    package_data={
        '': ['*.jinja'],
    },
    install_requires=['setuptools', 'zc.recipe.egg', 'Jinja2'],
    entry_points = {'zc.buildout': ['default = lighttpdrecipe.recipe:Lighttpd']},
    zip_safe=False,
)
