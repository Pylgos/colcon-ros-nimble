# Copyright 2018 Easymov Robotics
# Licensed under the Apache License, Version 2.0

import os

from colcon_core.event.test import TestFailure
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import get_command_environment
from colcon_core.task import run
from colcon_core.task import TaskExtensionPoint
from pathlib import Path
from colcon_core.event.output import StderrLine

logger = colcon_logger.getChild(__name__)


class NimbleTestTask(TaskExtensionPoint):
    """Test Nimble packages."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--nimble-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to nim compiler. ')

    async def test(self, *, additional_hooks=None):  # noqa: D102
        pkg = self.context.pkg
        args = self.context.args

        logger.info(
            "Testing Nimble package in '{args.path}'".format_map(locals()))

        assert os.path.exists(args.build_base), \
            "Has this package been built before?"

        try:
            env = await get_command_environment(
                'test', args.build_base, self.context.dependencies)
        except RuntimeError as e:
            logger.error(str(e))
            return 1

        cmd = [
            "nimble-ament-build",
            "test",
            "--install-base=" + str(Path(self.context.args.install_base).resolve()),
            "--build-base=" + str(Path(self.context.args.build_base).resolve()),
        ]

        res = await run(self.context, cmd, cwd=str(Path(self.context.pkg.path).resolve()), env=env, shell=False, capture_output=True)
        if res.returncode != 0:
            for line in res.stdout.split(b'\n'):
                self.context.put_event_into_queue(StderrLine(line + b'\n'))
            self.context.put_event_into_queue(TestFailure(pkg.name))
        
        # the return code should still be 0
        return 0
