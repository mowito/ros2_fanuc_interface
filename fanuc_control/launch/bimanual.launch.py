from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, OpaqueFunction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node, SetParameter
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import PushRosNamespace

from ament_index_python import get_package_share_directory
import os
import yaml

def load_yaml(package_name, file_path):
    pkg_path = get_package_share_directory(package_name)
    abs_path = os.path.join(pkg_path, file_path)
    with open(abs_path, "r") as f:
        return yaml.safe_load(f)

def generate_launch_description():
    declared = []

    declared += [
        DeclareLaunchArgument("left_robot_type",  default_value="crx10ia_l"),
        DeclareLaunchArgument("right_robot_type", default_value="crx10ia_l"),

        DeclareLaunchArgument("left_robot_ip",  default_value="192.168.1.100"),
        DeclareLaunchArgument("right_robot_ip", default_value="192.168.1.110"),

        DeclareLaunchArgument("use_mock_hardware", default_value="false", choices=["true", "false"]),
        DeclareLaunchArgument("read_only", default_value="false"),
        DeclareLaunchArgument("use_rmi", default_value="false"),

        DeclareLaunchArgument("gz", default_value="false"),
        DeclareLaunchArgument("gz_headless", default_value="true"),

        # TF between bases (right base relative to left base)
        DeclareLaunchArgument("right_base_xyz", default_value="0.8 0.0 0.0"),
        DeclareLaunchArgument("right_base_rpy", default_value="0.0 0.0 0.0"),

        # Controllers
        DeclareLaunchArgument("left_controllers_file",  default_value="controllers_left.yaml"),
        DeclareLaunchArgument("right_controllers_file", default_value="controllers_right.yaml"),

        # Bimanual MoveIt config package you will create
        DeclareLaunchArgument("bimanual_moveit_config_pkg", default_value="crx_bimanual_moveit_config"),
    ]

    return LaunchDescription(declared + [OpaqueFunction(function=launch_setup)])

def launch_setup(context, *args, **kwargs):
    description_package = "crx_description"

    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    read_only = LaunchConfiguration("read_only")
    use_rmi = LaunchConfiguration("use_rmi")
    gz = LaunchConfiguration("gz")
    gz_headless = LaunchConfiguration("gz_headless")

    left_robot_type  = LaunchConfiguration("left_robot_type")
    right_robot_type = LaunchConfiguration("right_robot_type")
    left_robot_ip    = LaunchConfiguration("left_robot_ip")
    right_robot_ip   = LaunchConfiguration("right_robot_ip")

    right_base_xyz = LaunchConfiguration("right_base_xyz")
    right_base_rpy = LaunchConfiguration("right_base_rpy")

    left_controllers_file  = LaunchConfiguration("left_controllers_file")
    right_controllers_file = LaunchConfiguration("right_controllers_file")

    bimanual_pkg = LaunchConfiguration("bimanual_moveit_config_pkg")

    set_use_sim_time = SetParameter(name="use_sim_time", value=gz)

    # -------- Left arm description (prefixed) --------
    left_robot_type_str = left_robot_type.perform(context)
    left_description = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([FindPackageShare(description_package), "urdf", left_robot_type_str, left_robot_type_str + ".xacro"]),
        " ", "robot_type:=", left_robot_type,
        " ", "use_mock_hardware:=", use_mock_hardware,
        " ", "robot_ip:=", left_robot_ip,
        " ", "read_only:=", read_only,
        " ", "use_rmi:=", use_rmi,
        " ", "gz:=", gz,
        " ", "prefix:=", TextSubstitution(text="left_"),
    ])
    left_robot_description = {"robot_description": left_description}

    # -------- Right arm description (prefixed) --------
    right_robot_type_str = right_robot_type.perform(context)
    right_description = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([FindPackageShare(description_package), "urdf", right_robot_type_str, right_robot_type_str + ".xacro"]),
        " ", "robot_type:=", right_robot_type,
        " ", "use_mock_hardware:=", use_mock_hardware,
        " ", "robot_ip:=", right_robot_ip,
        " ", "read_only:=", read_only,
        " ", "use_rmi:=", use_rmi,
        " ", "gz:=", gz,
        " ", "prefix:=", TextSubstitution(text="right_"),
    ])
    right_robot_description = {"robot_description": right_description}

    # Controllers paths
    left_robot_controllers = PathJoinSubstitution([FindPackageShare("fanuc_control"), "config", left_controllers_file])
    right_robot_controllers = PathJoinSubstitution([FindPackageShare("fanuc_control"), "config", right_controllers_file])

    # Namespaced stacks
    left_stack = GroupAction([
        PushRosNamespace("left"),

        Node(package="robot_state_publisher", executable="robot_state_publisher",
             output="both", parameters=[left_robot_description]),

        Node(package="controller_manager", executable="ros2_control_node",
             output="both",
             parameters=[left_robot_description, left_robot_controllers],
             remappings=[("/forward_position_controller/commands", "/position_commands")]),

        Node(package="controller_manager", executable="spawner",
             arguments=["joint_state_broadcaster", "--controller-manager", "/left/controller_manager"]),

        Node(package="controller_manager", executable="spawner",
             arguments=["manipulator_controller", "-c", "/left/controller_manager"]),
    ])

    right_stack = GroupAction([
        PushRosNamespace("right"),

        Node(package="robot_state_publisher", executable="robot_state_publisher",
             output="both", parameters=[right_robot_description]),

        Node(package="controller_manager", executable="ros2_control_node",
             output="both",
             parameters=[right_robot_description, right_robot_controllers],
             remappings=[("/forward_position_controller/commands", "/position_commands")]),

        Node(package="controller_manager", executable="spawner",
             arguments=["joint_state_broadcaster", "--controller-manager", "/right/controller_manager"]),

        Node(package="controller_manager", executable="spawner",
             arguments=["manipulator_controller", "-c", "/right/controller_manager"]),
    ])

    # Static TF: right_base relative to left_base
    # (Make sure these frame names match your base link naming after prefixing)
    static_tf_right = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            # xyz
            *right_base_xyz.perform(context).split(),
            # rpy
            *right_base_rpy.perform(context).split(),
            # parent, child
            "left_base_link",
            "right_base_link",
        ],
        output="screen"
    )

    # MoveIt: a NEW bimanual MoveIt config package (see section 2)
    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([FindPackageShare(bimanual_pkg), "launch", "move_group.launch.py"])]
        )
    )
    moveit_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([FindPackageShare(bimanual_pkg), "launch", "moveit_rviz.launch.py"])]
        )
    )

    # Optional Gazebo (you’ll likely need a dedicated bimanual gazebo.launch.py)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(get_package_share_directory("crx_description"), "launch", "gazebo.launch.py")]),
        launch_arguments={"headless": gz_headless}.items(),
        condition=IfCondition(gz),
    )

    return [
        set_use_sim_time,
        left_stack,
        right_stack,
        static_tf_right,
        move_group,
        moveit_rviz,
        gazebo_launch,
    ]
