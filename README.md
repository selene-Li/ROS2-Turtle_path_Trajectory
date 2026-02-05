# ROS2-Turtlesim-Letter-Trajectory
ROS2 turtlesim-based implementation for drawing letter trajectories (R/O/S)

## Task_3 Questions:
***In a separate python script, design ‘R’, ‘O’, ‘S’ trajectories for different colors with different
colors.***
## 1. 创建 ROS2 工作空间
   在主目录创建ros2_ws工作空间
```
mkdir -p ~/ros2_ws/src
```
   进入新建的ros2_ws工作空间根目录
```
cd ~/ros2_ws
```

## 2. 创建 ROS2 Python 功能包
```
cd ~/ros2_ws/src
```
   创建名为turtle_spawner的Python功能包
```
ros2 pkg create --build-type ament_python --license Apache-2.0 turtle_spawner
```
## 3. 创建并填充 Python 节点文件
```
cd ~/ros2_ws/src/turtle_spawner/turtle_spawner
```
   创建空的Task_3.py文件
```
touch Task_3.py
```
   将代码复制到新建的Task_3.py 文件爱你
```
gedit Task_3.py
```
## 4. 配置setup文件
```
gedit ~/ros2_ws/src/turtle_spawner/setup.py

```
   在 setup.py 文件的**entry_points**部分的console_scripts下，添加这一行：
```
'Task_3 = turtle_spawner.Task_3:main',
```
## 5. 编译 ROS2 功能包
   回到工作空间根目录
```
cd ~/ros2_ws
```
   仅编译turtle_spawner功能包
```
colcon build --packages-select turtle_spawner
```
   加载工作空间的环境变量
```
source install/setup.bash
```
## 6. 运行 ROS2 节点
   新建终端 1（运行海龟仿真节点）; 加载系统级ROS2 Humble环境
```
source /opt/ros/humble/setup.bash
```
   启动turtlesim仿真节点（弹出海龟窗口）
```
ros2 run turtlesim turtlesim_node
```
   新建终端 2（运行你Task_3 节点）； 进入工作空间根目录
```
cd ~/ros2_ws
```
  加载工作空间环境变量
```
source install/setup.bash
```
  运行Task_3节点
```
ros2 run turtle_spawner Task_3
```
