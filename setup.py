from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.libreorganizacion',
      version=version,
      description="A proposal archetype for Libre Organizacion system.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='propuesta proposal libre organizacion free organization democracia democracy',
      author='Manuel Gualda Caballero & Israel Saeta Perez',
      author_email='manuel@utopiaverde.org & dukebody@gmail.com',
      url='http://libreorganizacion.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Pillow',
          'Plone',
          'plone.app.dexterity',
          'plone.namedfile [blobs]',
          'plone.app.discussion',
          'plone.contentratings',
          'Products.PlonePopoll',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              ]
          },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
