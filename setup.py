from typing import List
from setuptools import setup  # type: ignore
from setuptools.command.install import install  # type: ignore
from pathlib import Path
import re


class CustomInstallCommand(install):  # type: ignore
    def run(self) -> None:
        install.run(self)

        # mark yarl as being typed
        import yarl
        (Path(yarl.__file__).parent / 'py.typed').touch()


requirements: List[str] = []
dependency_links: List[str] = []
db_requirements: List[str]

with open('requirements/base.txt') as f:
    lines: List[str] = f.read().splitlines()

    for line in lines:
        if line.startswith('git+https'):
            dependency_links.append(line)
            req = line.split('#egg=')[1].split('-')
            requirement = f'{req[0]}>={req[1]}'
            requirements.append(requirement)
        else:
            requirements.append(line)

with open('requirements/db.txt') as f:
    db_requirements = [line for line in f.read().splitlines() if not line.startswith('-r ')]

extras_require = {
    'db': db_requirements
}

version = ''
with open('botus_receptus/__init__.py') as f:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)

    if match is not None:
        version = match.group(1)


if not version:
    raise RuntimeError('version is not set')

if version.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass

setup(name='botus_receptus',
      author='Bryan Forbes',
      url='https://github.com/BryanForbes/botus_receptus',
      version=version,
      packages=[
          'botus_receptus', 'botus_receptus.db', 'aiohttp-stubs', 'asyncpg-stubs',
          'discord-stubs'
      ],
      package_data={
          'botus_receptus': ['py.typed'],
          'aiohttp-stubs': ['*.pyi'],
          'asyncpg-stubs': ['*.pyi', 'exceptions/*.pyi', 'protocol/*.pyi', 'protocol/codecs/*.pyi'],
          'discord-stubs': ['*.pyi', 'ext/*.pyi', 'ext/commands/*.pyi']
      },
      package_dir={
          'botus_receptus': 'botus_receptus',
          'aiohttp-stubs': 'stubs/aiohttp',
          'asyncpg-stubs': 'stubs/asyncpg',
          'discord-stubs': 'stubs/discord'
      },
      license='BSD 3-Clause',
      extras_require=extras_require,
      install_requires=requirements,
      dependency_links=dependency_links,
      cmdclass={'install': CustomInstallCommand})
