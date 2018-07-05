from setuptools import setup  # type: ignore
import re


requirements = [
    'async_timeout>=3.0.0',
    'attrs>=18.1.0',
    'click>=6.7',
    'mypy_extensions>=0.3.0',
    'typing-extensions>=3.6.5'
]

dependency_links = [
    'git+https://github.com/Rapptz/discord.py@ec3435b22418d36a01c04d2098a70d71844a4c87#egg=discord.py'
]

extras_require = {
    'db': [
        'asyncpg>=0.15.0'
    ]
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
          'discord-stubs', 'uvloop-stubs'
      ],
      package_data={
          'botus_receptus': ['py.typed'],
          'aiohttp-stubs': ['*.pyi'],
          'asyncpg-stubs': ['*.pyi', 'exceptions/*.pyi', 'protocol/*.pyi', 'protocol/codecs/*.pyi'],
          'discord-stubs': ['*.pyi', 'ext/*.pyi', 'ext/commands/*.pyi'],
          'uvloop-stubs': ['*.pyi']
      },
      package_dir={
          'botus_receptus': 'botus_receptus',
          'aiohttp-stubs': 'stubs/aiohttp',
          'asyncpg-stubs': 'stubs/asyncpg',
          'discord-stubs': 'stubs/discord',
          'uvloop-stubs': 'stubs/uvloop'
      },
      license='BSD 3-Clause',
      extras_require=extras_require,
      install_requires=requirements,
      dependency_links=dependency_links)
