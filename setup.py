from setuptools import setup, find_packages

requires = [req for req in open('requirements.txt').read().splitlines()
            if not req.startswith('git')]

setup(name='admiral',
      version='0.0.1',
      description='SpotFleet Admiral',
      long_description=open('README.md').read(),
      url='https://github.com/deviavir/spotfleet-admiral',
      author='Chase Sillevis',
      author_email='chase@sillevis.net',
      license='MIT',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['test']),
      install_requires=requires,
      zip_safe=True)
