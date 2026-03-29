## 맵만들기

시뮬레이션의 경우

```bash
ros2 launch pinky_gz_sim launch_sim_shop.launch.xml
ros2 launch pinky_navigation gz_map_building.launch.xml
# teleop keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# rviz
ros2 launch pinky_navigation gz_map_view.launch.xml
```

실물 로봇의 경우

```bash
# [Pinky]
## 로봇 설명(URDF), 라이다, 베이스 컨트롤러, 오도메트리 등 실제 로봇에 필요한 노드들을 띄웁니다
ros2 launch pinky_bringup bringup_robot.launch.xml
## slam_toolbox를 켜서 /scan과 TF로 맵을 만들고 /map을 퍼블리시합니다.
ros2 launch pinky_navigation map_building.launch.xml

# [PC]
## RViz를 실행해 SLAM으로 생성되는 /map 토픽을 실시간으로 확인합니다.
ros2 launch pinky_navigation map_view.launch.xml
# 키보드로 로봇을 수동 조종해 지도에 미탐색 구역을 채웁니다.
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# 현재 /map 토픽을 파일로 저장합니다. (예: my_map -> my_map.yaml, my_map.pgm)
ros2 run nav2_map_server map_saver_cli -f "<저장할 맵이름>"
```

[맵을 수정해주는 웹앱](https://gyropalm.github.io/ROS-SLAM-Map-Editor/editor.html)

```bash
## 생성한 월드로 시뮬 실행
ros2 launch pinky_gz_sim launch_second_map_sim.launch.xml
```

## 네비게이션

시뮬레이션의 경우
```bash
# 아래 둘 중 하나만 실행 (동시에 둘 다 실행하면 Gazebo/브리지/TF가 충돌할 수 있음)
# 기본 공장 월드
# ros2 launch pinky_gz_sim launch_sim.launch.xml

# custom_map 월드
ros2 launch pinky_gz_sim launch_custom_map_sim.launch.xml

# custom_map 월드를 쓴다면 map도 custom_map.yaml로 맞춰서 전달
ros2 launch pinky_navigation gz_bringup_launch.xml map:=maps/custom_map.yaml
ros2 launch pinky_navigation gz_nav2_view.launch.xml
```

실물 로봇의 경우

```bash
# [Pinky]
## 로봇 설명(URDF), 라이다, 베이스 컨트롤러, 오도메트리 등 실제 로봇에 필요한 노드들을 띄웁니다
ros2 launch pinky_bringup bringup_robot.launch.xml

# 저장한 정적 맵(yaml)을 로드해 localization + navigation(Nav2) 스택을 실행합니다.
ros2 launch pinky_navigation bringup_launch.xml map:=<저장한 맵이름.yaml>

# [PC]
# RViz를 실행해 로봇 위치, 코스트맵, 계획 경로를 시각화하고 목표를 줄 수 있습니다.
ros2 launch pinky_navigation nav2_view.launch.xml

# 2D Pose Estimate 버튼을 눌러 라이다와 맵 일치 시켜주기
# Nav2 Goal을 클릭하고 이동
```

## 맵상의 좌표 얻기

###  클릭한 부분의 좌표를 얻는법

```bash
# clicked_point 토픽을 구독
ros2 topic echo /clicked_point
# 이후 rviz의 publish point 이용, rviz 상 좌표 클릭
```

### 로봇의 현제 좌표를 얻는 법

```bash 
ros2 topic echo /amcl_pose
```

## Waypoint

1. waypoint 클릭
2. nav2 goal 을 이용해서 waypoint 추가
3. start waypoint following