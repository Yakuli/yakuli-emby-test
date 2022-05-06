# yakuli-emby-test

## 声明
**这是一个测试的bot, 写了玩, 有很多bug, 仅供交流学习用, 所产生的任何后果与本人无关**

## 使用

### 1. 配置 /utils/config.json
  - `BOT_TOKEN` 那就是@BotFather创建的机器人的Token了
  - `EMBY_URL` Emby的主服务器
  - `API_TOKEN` Emby的API密钥
  - `PROXY` 设置全局代理, *留空*则不设置代理 (如果你在不能访问TG的地区, 这很有用)
  - `LINES` /line 命令性展示给用户的线路
  - `LOG_FILE` 日志文件 (我也不知道为啥要写这个, 虽然没啥用)
  - `WELCOME` 用户首次使用机器人时的欢迎语
  - `COMMAND` 用户/help 时的功能列表
## 运行

### 1. 本地运行
> 环境要求: >= Python3.9 
``` shell
pip install -r requirements.txt
python bot.py
```
### 2. Docker运行(建议的)
编译镜像, 运行
``` shell
docker build -t emby_bot_image .
docker run -dt --name=emby_bot -v $PWD:/root/emby --restart=always emby_bot_image
```
重启
``` shell
docker restart emby_bot
```
## 功能
- [x] start - 登记
- [x] create - 注册账号
- [x] reset - 重置密码
- [x] bind - emby账号与tg绑定
- [x] my - 查询用户信息
- [x] line - 查看emby线路
- [x] help - 查看机器人帮助
- [ ] status - 查看EMBY服务器运行状态
- [ ] total - 查看统计信息
- [ ] search - 管理员


