# Licensed under the Apache License, Version 2.0

import os
from collections import OrderedDict
from pathlib import Path
from argparse import ArgumentParser

from colcon_core.environment import create_environment_scripts
from colcon_core.logging import colcon_logger
from colcon_core.package_descriptor import PackageDescriptor
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import create_environment_hook, get_command_environment
from colcon_core.task import TaskExtensionPoint, run
from colcon_core.verb.build import BuildPackageArguments
from colcon_core.event.output import StderrLine


logger = colcon_logger.getChild(__name__)


class AmentNimbleBuildTask(TaskExtensionPoint):
    """Build ROS packages with the build type 'ament_nimble'"""

    def __init__(self):
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, "^1.0")

    def add_arguments(self, *, parser: ArgumentParser):
        parser.add_argument(
            '--nimble-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to nim compiler. ')

    async def build(
        self, *, additional_hooks=[], skip_hook_creation=False
    ):
        additional_hooks += create_environment_hook(
            "ament_prefix_path",
            Path(self.context.args.install_base),
            self.context.pkg.name,
            "AMENT_PREFIX_PATH",
            "",
            mode="prepend")

        pkg: PackageDescriptor = self.context.pkg
        args: BuildPackageArguments = self.context.args

        logger.info(
            f"Building Nimble package in '{args.path}'")

        try:
            env = await get_command_environment(
                "build", args.build_base, self.context.dependencies)
        except RuntimeError as e:
            logger.error(str(e))
            return 1

        rc = await self._build(args, env)
        if rc != 0:
            return rc

        additional_hooks += create_environment_hook(
            f"nim_{pkg.name}_path",
            Path(args.install_base),
            pkg.name,
            "PATH",
            os.path.join("lib", self.context.pkg.name),
            mode="prepend")

        if not skip_hook_creation:
            create_environment_scripts(
                pkg, args, additional_hooks=additional_hooks)

    async def _build(self, args: BuildPackageArguments, env: OrderedDict):
        self.progress("build")
        cmd = [
            "nimble-ament-build",
            "build",
            "--install-base=" + str(Path(self.context.args.install_base).resolve()),
            "--build-base=" + str(Path(self.context.args.build_base).resolve())
        ]
        if self.context.args.symlink_install:
            cmd.append("--symlink-install")
        res = await run(self.context, cmd, cwd=str(Path(self.context.pkg.path).resolve()), env=env, shell=False, capture_output=True)
        if res.returncode != 0:
            for line in res.stdout.split(b'\n'):
                self.context.put_event_into_queue(StderrLine(line + b'\n'))

        return res.returncode
