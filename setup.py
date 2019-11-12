"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import json
import os
import shutil
import sys
from abc import abstractmethod
from distutils.command.clean import clean
from pathlib import Path
from subprocess import CalledProcessError, call, check_call

from setuptools import Command, find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

if 'bdist_wheel' in sys.argv:
    raise RuntimeError("This setup.py does not support wheels")

# Paths setup with virtualenv detection
if 'VIRTUAL_ENV' in os.environ:
    BASE_ENV = Path(os.environ['VIRTUAL_ENV'])
else:
    BASE_ENV = Path('/')

# Kytos var folder
VAR_PATH = BASE_ENV / 'var' / 'lib' / 'kytos'
# Path for enabled NApps
ENABLED_PATH = VAR_PATH / 'napps'
# Path to install NApps
INSTALLED_PATH = VAR_PATH / 'napps' / '.installed'
CURRENT_DIR = Path('.').resolve()

# NApps enabled by default
# CORE_NAPPS = ['of_core']


class SimpleCommand(Command):
    """Make Command implementation simpler."""

    user_options = []

    def __init__(self, *args, **kwargs):
        """Store arguments so it's possible to call other commands later."""
        super().__init__(*args, **kwargs)
        self.__args = args
        self.__kwargs = kwargs

    @abstractmethod
    def run(self):
        """Run when command is invoked.

        Use *call* instead of *check_call* to ignore failures.
        """

    def run_command(self, command_class):
        """Run another command with same __init__ arguments."""
        command_class(*self.__args, **self.__kwargs).run()

    def initialize_options(self):
        """Set defa ult values for options."""

    def finalize_options(self):
        """Post-process options."""


class Cleaner(clean):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        super().run()
        call('rm -vrf ./build ./dist ./*.pyc ./*.egg-info', shell=True)
        call('find . -name __pycache__ -type d | xargs rm -rf', shell=True)


class TestCoverage(SimpleCommand):
    """Display test coverage."""

    description = 'run unit tests and display code coverage'

    def run(self):
        """Run unittest quietly and display coverage report."""
        cmd = 'coverage3 run setup.py test && coverage3 report'
        check_call(cmd, shell=True)


class CITest(SimpleCommand):
    """Run all CI tests."""

    description = 'run all CI tests: unit and doc tests, linter'

    def run(self):
        """Run unit tests with coverage, doc tests and linter."""
        for command in TestCoverage, Linter:
            self.run_command(command)


class Linter(SimpleCommand):
    """Lint Python source code."""

    description = 'lint Python source code'

    def run(self):
        """Run yala."""
        print('Yala is running. It may take several seconds...')
        try:
            check_call('yala *.py backends/*.py tests/*.py', shell=True)
            print('No linter error found.')
        except CalledProcessError:
            print('Linter check failed. Fix the error(s) above and try again.')
            exit(-1)


class InstallMode(install):
    """Create files in var/lib/kytos."""

    description = 'To install NApps, use kytos-utils. Devs, see "develop".'

    def run(self):
        """Create of_core as default napps enabled."""
        print(self.description)


class DevelopMode(develop):
    """Recommended setup for kytos-napps developers.

    Instead of copying the files to the expected directories, a symlink is
    created on the system aiming the current source code.
    """

    description = 'install NApps in development mode'

    def run(self):
        """Install the package in a developer mode."""
        super().run()
        if self.uninstall:
            shutil.rmtree(str(ENABLED_PATH), ignore_errors=True)
        else:
            self._create_folder_symlinks()
            # self._create_file_symlinks()
            # KytosInstall.enable_core_napps()

    @staticmethod
    def _create_folder_symlinks():
        """Symlink to all Kytos NApps folders.

        ./napps/kytos/napp_name will generate a link in
        var/lib/kytos/napps/.installed/kytos/napp_name.
        """
        links = INSTALLED_PATH / 'kytos'
        links.mkdir(parents=True, exist_ok=True)
        code = CURRENT_DIR
        src = links / 'kronos'
        symlink_if_different(src, code)

        (ENABLED_PATH / 'kytos').mkdir(parents=True, exist_ok=True)
        dst = ENABLED_PATH / Path('kytos', 'kronos')
        symlink_if_different(dst, src)

    # @staticmethod
    # def _create_file_symlinks():
    #     """Symlink to required files."""
    #     src = ENABLED_PATH / '__init__.py'
    #     dst = CURRENT_DIR / 'napps' / '__init__.py'
    #     symlink_if_different(src, dst)


def symlink_if_different(path, target):
    """Force symlink creation if it points anywhere else."""
    # print(f"symlinking {path} to target: {target}...", end=" ")
    if not path.exists():
        # print(f"path doesn't exist. linking...")
        path.symlink_to(target)
    elif not path.samefile(target):
        # print(f"path exists, but is different. removing and linking...")
        # Exists but points to a different file, so let's replace it
        path.unlink()
        path.symlink_to(target)


def read_version_from_json():
    """Read the NApp version from NApp kytos.json file."""
    file = Path('kytos.json')
    metadata = json.loads(file.read_text())
    return metadata['version']


setup(name='kytos_kronos',
      version=read_version_from_json(),
      description='NApp to store time series data developed by Kytos Team',
      url='http://github.com/kytos/kronos',
      author='Kytos Team',
      author_email='devel@lists.kytos.io',
      license='MIT',
      test_suite='tests',
      include_package_data=True,
      extras_require={
          'dev': [
              'coverage',
              'pip-tools',
              'yala',
              'tox',
          ],
      },
      packages=find_packages(exclude=['tests']),
      cmdclass={
          'ci': CITest,
          'clean': Cleaner,
          'coverage': TestCoverage,
          'develop': DevelopMode,
          'install': InstallMode,
          'lint': Linter
      },
      zip_safe=False,
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.6',
          'Topic :: System :: Networking',
          'Topic :: Software Development :: Libraries'
      ])
