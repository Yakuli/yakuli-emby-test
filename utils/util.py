import json
import logging
import os

import requests

base_dir = os.path.dirname(os.path.abspath(__file__))

REQUEST_KWARGS = {
    'proxy_url': ''
}


# 获取config.json的json 字典
def get_config():
    """Get Base config"""
    with open(f'{base_dir}/config.json', 'r', encoding='utf-8') as fr:
        configs = json.load(fr)
    # logging.info(f'配置文件:{configs}')
    return configs


config = get_config()
logging.basicConfig(
    filename=f"{base_dir}/../{config['LOG_FILE']}",
    level=logging.INFO,
    filemode='a+',
    format='%(levelname)s:%(asctime)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


def get_help():
    msg = '请根据以下命令列表进行操作\n------------\n'
    for k in config['COMMAND']:
        msg += f"{k}\t\t{config['COMMAND'][k]}\n"
    return msg


def load_userid_json():
    with open(f'{base_dir}/userid.json', 'r') as fr:
        return json.load(fr)


def get_ids():
    return list(load_userid_json().keys())


def save_id(user_id, user_type='user'):
    ids = load_userid_json()
    if user_type == 'user':
        # 初始化用户
        ids[str(user_id)] = {
            'type': 'user'
        }
    elif user_type == 'admin':
        # 更新type
        ids[str(user_id)]['type'] = 'admin'
    # ids[str(user_id)] = {'type': 'user'} if user_type == 'user' else {'type': 'admin'}
    with open(f'{base_dir}/userid.json', 'w') as fw:
        json.dump(ids, fw, indent=2)


def is_admin(user_id):
    if load_userid_json()[str(user_id)]['type'] == 'admin':
        return True
    return False


def update_id(tg_id, emby_name, emby_id):
    ids = load_userid_json()
    ids[str(tg_id)]['emby_name'] = emby_name
    ids[str(tg_id)]['emby_id'] = emby_id
    with open(f'{base_dir}/userid.json', 'w') as fw:
        json.dump(ids, fw, indent=2)


# -------- EMBY OPERATE --------
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/100.0.4896.60 Safari/537.36 ',
    'accept': 'application/json'
}
proxy = config['PROXY'] if config['PROXY'] else False


def url_get(path):
    url = f"{config['EMBY_URL']}/emby{path}?api_key={config['API_TOKEN']}"
    if proxy:
        return requests.get(url, headers=header, proxies={'http': proxy, 'https': proxy})
    else:
        return requests.get(url, headers=header)


def url_post_body(path, body):
    url = f"{config['EMBY_URL']}/emby{path}?api_key={config['API_TOKEN']}"
    if proxy:
        return requests.post(url, headers=header, json=body,
                             proxies={'http': proxy, 'https': proxy})
    else:
        return requests.post(url, json=body, headers=header)


def url_delete(path):
    url = url = f"{config['EMBY_URL']}/emby{path}?api_key={config['API_TOKEN']}"
    if proxy:
        return requests.delete(url, headers=header, proxies={'http': proxy, 'https': proxy})
    else:
        return requests.delete(url, headers=header)


def get_emby_users():
    """Get emby users
    return:
        users: dict{'name1':'id1','name2':'id2'}
    """
    path = '/Users/Query'
    r = url_get(path)
    users = {}
    for u in r.json()['Items']:
        users[u['Name']] = u['Id']
    return users


def is_bind(tg_id):
    """判断用户是否已绑定或已创建(库里有)
    
    args:
        tg_id: TGID
    """
    if len(load_userid_json()[str(tg_id)]) > 1:
        return True
    return False


def create_emby_user(tg_id, username):
    """Create emby user

    args:
        username: 自定义username (可选)
    return:
        [message]: 返回TG的消息
    """
    if is_bind(tg_id):
        return f"您已有账号:{load_userid_json()[str(tg_id)]['emby_name']}, 不可再注册"
    path = '/Users/New'
    body = {
        'Name': username
    }
    r = url_post_body(path, body)
    if r.status_code == 200:
        update_id(tg_id, username, r.json()['Id'])
        return f"创建成功!\n用户名: {username}\n请登录官网修改密码 (第一次登录需空密码)"
    else:
        return f"创建失败, 请联系管理员"


def delete_emby_user(userid=''):
    """delete User

    args:
        userid: userid
    return
        [message]: 返回TG的消息
    """
    path = f'/Users/{userid}'
    r = url_delete(path)
    print(r)
    if r.status_code == 204:
        return f"用户id{userid}\n删除成功"
    elif r.status_code == 404:
        return f"无此用户id{userid}\n删除失败"


def bind_emby_user(tg_id, emby_name):
    """绑定emby用户"""
    ids = load_userid_json()
    # 判断用户是否已被绑定
    for u in ids:
        if len(ids[u]) > 1:
            if ids[u]['emby_name'] == emby_name:
                return f"用户名: {emby_name} 已被绑定, 请检查!"
    update_id(tg_id, emby_name, get_emby_users()[emby_name])
    return f"绑定/换绑成功"


def reset_user_password(username):
    """reset Password"""
    path = ''


def main_test():
    pass
    # print(delete_emby_user('3fe466c0b82c47e899cc717b50a1a987'))
    print(json.dumps(get_emby_users(), indent=2))


if __name__ == '__main__':
    main_test()
