from os import path
import dotenv
import click
import re

env = {
    "HOST": "127.0.0.1",
    "PORT": "8080",
    "SECRET": '',
    "ACCESS_TOKEN": '',
    "SUPERUSERS": [],
    "COMMAND_START": [""],
    "HARUKA_DIR": "./data/"
}


def create_env():
    if path.exists('./.env.prod'):
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
        dotenv.set_key('./.env.prod', key, str(value).replace('\'', '\"').replace(' ', ''), quote_mode='never')

if __name__ == "__main__":
    create_env()