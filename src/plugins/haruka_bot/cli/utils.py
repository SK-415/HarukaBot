from pathlib import Path

import click
import dotenv

env = {
    "HOST": "127.0.0.1",
    "PORT": "8080",
    "SECRET": '',
    "ACCESS_TOKEN": '',
    "SUPERUSERS": [],
    "COMMAND_START": [""],
    "HARUKA_DIR": "./data/",
    "LOG_LEVEL": "DEBUG"
}


def create_env():
    file_path = Path('./.env.prod').resolve()
    if file_path.exists():
        return

    while True:
        try:
            superusers = click.prompt('主人QQ号 (多个使用空格分开)', default='', show_default=False)
            superusers = [int(superuser) for superuser in superusers.split()]
            env['SUPERUSERS'] = superusers
            break
        except ValueError:
            print('输入格式有误，请重新输入')

    with open('.env.prod', 'w') as f:
        pass
    
    for key, value in env.items():
        dotenv.set_key(file_path, key, str(value).replace('\'', '\"').replace(' ', ''), quote_mode='never')

if __name__ == "__main__":
    create_env()
