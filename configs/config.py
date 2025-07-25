# -*- coding: utf-8 -*-

# Max-Planck-Gesellschaft zur Förderung der Wissenschaften e.V. (MPG) is
# holder of all proprietary rights on this computer program.
# You can only use this computer program if you have closed
# a license agreement with MPG or you get the right to use the computer
# program from someone who is authorized to grant you that right.
# Any use of the computer program without a valid license is prohibited and
# liable to prosecution.
#
# Copyright©2023 Max-Planck-Gesellschaft zur Förderung
# der Wissenschaften e.V. (MPG). acting on behalf of its Max Planck Institute
# for Intelligent Systems. All rights reserved.
#
# Contact: mica@tue.mpg.de

import yaml
import argparse
from pathlib import Path
from yacs.config import CfgNode as CN

cfg = CN()

cfg.flame_geom_path = "data/FLAME2020/generic_model.pkl"
cfg.flame_template_path = "data/uv_template.obj"
cfg.flame_lmk_path = "data/landmark_embedding.npy"
cfg.tex_space_path = "data/FLAME2020/FLAME_texture.npz"

cfg.num_shape_params = 300
cfg.num_exp_params = 100
cfg.tex_params = 140
cfg.actor = ""
cfg.config_name = ""
cfg.kernel_size = 7
cfg.sigma = 9.0
cfg.keyframes = [0]
cfg.bbox_scale = 2.5
cfg.fps = 25
cfg.begin_frames = 0
cfg.end_frames = 0
cfg.image_size = [512, 512]  # height, width
cfg.rotation_lr = 0.2
cfg.translation_lr = 0.003
cfg.raster_update = 8
cfg.pyr_levels = [
    [1.0, 160],
    [0.25, 40],
    [0.5, 40],
    [1.0, 70],
]  # Gaussian pyramid levels (scaling, iters per level) first level is only the sparse term!
cfg.optimize_shape = False
cfg.optimize_jaw = False
cfg.crop_image = True
cfg.save_folder = "./output/"

# Weights
cfg.w_pho = 350
cfg.w_lmks = 7000
cfg.w_lmks_68 = 1000
cfg.w_lmks_lid = 1000
cfg.w_lmks_mouth = 15000
cfg.w_lmks_iris = 1000
cfg.w_lmks_oval = 2000

cfg.w_exp = 0.02
cfg.w_shape = 0.3
cfg.w_tex = 0.04
cfg.w_jaw = 0.05

# Additional configuration keys added to allow a base configuration
cfg.is_base_config = None
cfg.test_run = None


def get_cfg_defaults():
    return cfg.clone()


def update_cfg(cfg, cfg_file):
    cfg.merge_from_file(cfg_file)
    return cfg.clone()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, help="Configuration file", required=True)

    args = parser.parse_args()
    print(args, end="\n\n")


def load_yaml_file(file_path: str) -> dict:
    """Load a YAML file and return its contents as a dictionary.

    Args:
        file_path (str): The path to the YAML file to be loaded.

    Returns:
        dict: A dictionary containing the contents of the YAML file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        raise
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        raise


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, help="Configuration file", required=True)

    args = parser.parse_args()
    print(args, end="\n\n")

    cfg = get_cfg_defaults()
    if args.cfg is not None:
        cfg_file = args.cfg
        cfg = update_cfg(cfg, args.cfg)
        cfg.cfg_file = cfg_file
    cfg.config_name = Path(args.cfg).stem
    return cfg


def parse_cfg(cfg_file):
    cfg = get_cfg_defaults()
    cfg = update_cfg(cfg, cfg_file)
    cfg.cfg_file = cfg_file

    cfg.config_name = Path(cfg_file).stem

    return cfg


def generate_configs_from_base(base_cfg: dict) -> list[dict]:
    """Generate tracker configurations for each video inside the base actor folder.

    The `base_cfg` could look like this:

    ```
    actor: './bulk/data/processed/face_recordings/'
    save_folder: './bulk/data/interim/face_recordings/Metrical-Tracker/'
    ...
    ```
    And this file will be used to create the tracker config for each video of the dataset. E.g.,
    one video is in: `/bulk/data/processed/face_recordings/2/bite_lower_lip/video.mp4`, but the
    original config file has to have the following path in actor key:
    `actor: './bulk/data/processed/face_recordings/2/bite_lower_lip/'`
    But there are many subfolders inside `face_recordings/2` and also in `face_recordings/3`, etc.

    Args:
        base_cfg (dict): The base configuration dictionary containing the actor path.

    Returns:
        list[dict]: A list of configuration dictionaries for each video found in the actor path.
    """
    base_actor_path = Path(base_cfg.actor)
    if not base_actor_path.exists():
        raise ValueError(f"Base actor path does not exist: {base_actor_path}")

    configs = []

    # Scan subdirectories for videos
    for subdir in base_actor_path.glob("*/*"):  # Assuming structure actor/class/video/
        if subdir.is_dir() and (subdir / "video.mp4").exists():
            print(f"Found video in: {subdir}")

            new_cfg = base_cfg.clone()
            new_cfg.actor = str(subdir)  # Update actor path
            # Save folder based on subdir parent and subdir stem
            # e.g., if subdir is `../2/bite_lower_lip`, then save folder will be
            # `../Metrical-Tracker/2/`, because the missing folder `bite_lower_lip` is handled
            # by tracker.py
            new_cfg.save_folder = str(Path(base_cfg.save_folder) / subdir.parent.stem) + "/"
            new_cfg.config_name = subdir.stem  # Name based on the last folder

            configs.append(new_cfg)

    print(f"\n>>> In total, {len(configs)} configs were generated.\n")
    return configs
