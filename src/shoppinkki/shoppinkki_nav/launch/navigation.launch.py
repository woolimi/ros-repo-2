"""Navigation launch — map_server + AMCL + Nav2 bringup."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('shoppinkki_nav')
    map_yaml = os.path.join(pkg_nav, 'maps', 'shop.yaml')
    params_file = os.path.join(pkg_nav, 'config', 'nav2_params.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=map_yaml,
        description='Path to map YAML file',
    )

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        parameters=[{'yaml_filename': LaunchConfiguration('map')}],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        parameters=[params_file],
    )

    return LaunchDescription([map_arg, map_server, amcl])
