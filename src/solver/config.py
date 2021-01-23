import os
from dotenv import load_dotenv


def load_envs(root: str):
    default_env = os.path.join(root, '.env.base')
    custom_env = os.path.join(root, '.env')

    path = default_env
    if os.path.exists(custom_env):
        path = custom_env

    load_dotenv(dotenv_path=path)
