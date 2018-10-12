from setuptools import setup  # type: ignore
import re


requirements = [
    'async_timeout>=3.0.0',
    'attrs>=18.1.0',
    'click>=6.7',
    'mypy_extensions>=0.4.1',
    'typing-extensions>=3.6.5'
]

version = ''
with open('src/botus_receptus/__init__.py') as f:
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

dependency_links = [
    'git+https://github.com/bryanforbes/discord.py@8c18bf868e47740e8ae1c2fb2741b3482412efab#egg=discord.py[typings]'
]

extras_require = {
    'db': ['asyncpg>=0.17.0']
}

setup(name='botus_receptus',
      author='Bryan Forbes',
      url='https://github.com/BryanForbes/botus_receptus',
      version=version,
      packages=[
          'botus_receptus', 'botus_receptus.db', 'asyncpg-stubs', 'uvloop-stubs'
      ],
      package_data={
          'botus_receptus': ['py.typed'],
          'asyncpg-stubs': ['*.pyi', 'exceptions/*.pyi', 'protocol/*.pyi', 'protocol/codecs/*.pyi'],
          'uvloop-stubs': ['*.pyi']
      },
      package_dir={'': 'src'},
      license='BSD 3-Clause',
      install_requires=requirements,
      extras_require=extras_require,
      python_requires=">=3.7",
      dependency_links=dependency_links)
