# Copyright 2018 Easymov Robotics
# Licensed under the Apache License, Version 2.0

from colcon_core.logging import colcon_logger
from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_core.package_descriptor import PackageDescriptor
from colcon_core.plugin_system import satisfies_version
from colcon_ros.package_identification.ros import _get_package
from colcon_ros.package_identification.ros import RosPackageIdentification
import copy

logger = colcon_logger.getChild(__name__)


class AmentNimblePackageIdentification(PackageIdentificationExtensionPoint):
    """Nimble packages with `.nimble` files"""
    
    PRIORITY = 1000

    def __init__(self):
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, desc: PackageDescriptor):
        if desc.type is not None and desc.type != 'ament_nimble':
            return

        ros_desc = copy.deepcopy(desc)

        ros_extension = RosPackageIdentification()
        ros_extension.identify(ros_desc)

        if ros_desc.type != 'ament_nimble':
            return

        if not (ros_desc.path / f"{ros_desc.name}.nimble").is_file():
            return

        desc.type = ros_desc.type
        desc.name = ros_desc.name
        desc.dependencies = ros_desc.dependencies
        desc.hooks = ros_desc.hooks
        desc.metadata = ros_desc.metadata