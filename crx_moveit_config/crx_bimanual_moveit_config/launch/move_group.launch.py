from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("crx_bimanual", package_name="crx_bimanual_moveit_config").to_moveit_configs()
    #print(moveit_config.config_dir_path)

    return generate_move_group_launch(moveit_config)
