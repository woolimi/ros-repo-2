"""Navigation launch — map_server + AMCL + Nav2 bringup + Keepout Filter."""

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
    keepout_mask_yaml = os.path.join(pkg_nav, 'config', 'keepout_mask.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=map_yaml,
        description='Path to map YAML file',
    )

    # ── 주행 맵 서버 ─────────────────────────────────────────────────────────
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': LaunchConfiguration('map')}],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params_file],
    )

    # ── Keepout Filter 노드 (RETURNING 전용) ─────────────────────────────────
    # BTReturning이 lifecycle_manager_filter 를 통해 활성화/비활성화합니다.
    # autostart=false → 평상시 비활성. RETURNING 진입 시 BTReturning이 STARTUP.

    filter_mask_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='filter_mask_server',
        output='screen',
        parameters=[{
            'yaml_filename': keepout_mask_yaml,
            'topic_name': 'keepout_filter_mask',
            'frame_id': 'map',
        }],
    )

    costmap_filter_info_server = Node(
        package='nav2_map_server',
        executable='costmap_filter_info_server',
        name='costmap_filter_info_server',
        output='screen',
        parameters=[{
            'type': 0,                            # 0 = KeepoutFilter
            'filter_info_topic': '/costmap_filter_info',
            'mask_topic': '/keepout_filter_mask',
            'base': 0.0,
            'multiplier': 1.0,
        }],
    )

    # 메인 Nav2 lifecycle 관리자 (map_server, amcl 포함)
    lifecycle_manager_nav = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
        }],
    )

    # Keepout Filter 전용 lifecycle 관리자
    # autostart=false: 기본 비활성 상태 유지.
    # BTReturning이 /lifecycle_manager_filter/manage_nodes 서비스로
    # STARTUP(활성화) / PAUSE(비활성화) 명령을 전송합니다.
    lifecycle_manager_filter = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_filter',
        output='screen',
        parameters=[{
            'autostart': False,
            'node_names': ['filter_mask_server', 'costmap_filter_info_server'],
            'bond_timeout': 0.0,
        }],
    )

    return LaunchDescription([
        map_arg,
        map_server,
        amcl,
        filter_mask_server,
        costmap_filter_info_server,
        lifecycle_manager_nav,
        lifecycle_manager_filter,
    ])
