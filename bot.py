import re
import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, InlineQueryHandler
from utils.util import config, get_help, get_ids, save_id, is_admin, load_userid_json
from utils.util import create_emby_user, get_emby_users, bind_emby_user, is_bind


base_dir = os.path.dirname(os.path.abspath(__file__))


def start(update: Update, context: CallbackContext):
    """欢迎"""
    if str(update.effective_user.id) not in get_ids():
        save_id(update.effective_user.id)
        msg = config['WELCOME'] + '\n' + get_help() + "更多功能请关注频道"
        update.message.reply_markdown(msg)
    else:
        update.message.reply_markdown(get_help())


def help(update: Update, context: CallbackContext):
    """机器人帮助"""
    update.message.reply_markdown(get_help())


def create(update: Update, context: CallbackContext):
    """注册账号主函数"""
    if update.effective_chat.type != 'private':
        update.message.reply_text('不支持群内创建账号, 请私聊bot!')
    else:
        new_user = ''.join(context.args)
        if new_user:
            # 判断用户名是否合法
            if len(new_user) > 20 or len(new_user) < 8:
                update.message.reply_text('用户名长度不合法')
            elif re.match("^[a-zA-Z][0-9a-zA-z]*", new_user):   # 查找确认以字母开头不分大小写, 只包含数字和字母
                update.message.reply_text(create_emby_user(update.effective_user.id, new_user))
            else:
                update.message.reply_text('命名不合法')
        else:
            update.message.reply_markdown('参数错误\n正确用法: `/create [name]`\nname: 以字母开头,8-20位的字母或数字')


def reset(update: Update, context: CallbackContext):
    """重置账户密码"""
    if update.effective_chat.type != 'private':
        update.message.reply_text('不支持群内重置密码, 请私聊bot!')
    else:
        update.message.reply_text('暂未开放此功能, 请联系管理员')


def bind(update: Update, context: CallbackContext):
    """已有emby账号与TG绑定"""
    if update.effective_chat.type != 'private':
        update.message.reply_text('不支持群内绑定账号, 请私聊bot!')
    else:
        # bing后的args获取用法
        emby_name = ''.join(context.args)
        if emby_name == '':
            update.message.reply_markdown('绑定用法: `/bind [name]`\n---\n例如: `/bind anoxia`')
        else:
            if emby_name in get_emby_users().keys():
                update.message.reply_markdown(bind_emby_user(update.effective_user.id, emby_name))
            else:
                update.message.reply_markdown(f"emby用户名: {emby_name} 不存在")


def my(update: Update, context: CallbackContext):
    """返回用户userID"""
    msg = f"ID: {update.effective_user.id}\n"
    # 判断用户是否已绑定
    if is_bind(update.effective_user.id):
        msg += f"您已绑定EMBY, 账号: {load_userid_json()[str(update.effective_user.id)]['emby_name']}"
    else:
        msg += "您尚未绑定EMBY\n已有账号绑定 /bind\n无账号去创建 /create"
    update.message.reply_markdown(msg)


def line(update: Update, context: CallbackContext):
    """查看emby线路(网址)"""
    lines = ''
    for l in config['LINES']:
        lines += f"{l}\n"
    update.message.reply_markdown(f"*当前可用线路有:*\n----\n{lines}", disable_web_page_preview=True)


def status(update: Update, context: CallbackContext):
    """查看服务器运行状态"""


def total(update: Update, context: CallbackContext):
    """查看统计信息"""
    if update.effective_chat.type == 'private' and is_admin(update.effective_user.id):
        bind_number = 0
        for u in load_userid_json():
            if is_bind(u):
                bind_number += 1
        update.message.reply_text(f"用户数: {len(load_userid_json())}\n已注册/绑定用户: {bind_number}")
        if ''.join(context.args) == 'all':
            with open(f'{base_dir}/utils/userid.json', 'r') as fr:
                update.message.reply_document(fr)
            # update.message.reply_text(json.dumps(load_userid_json(), indent=2))
    else:
        update.message.reply_text('对不起，我不理解这个命令 /help')


def search(update: Update, context: CallbackContext):
    """管理员搜索"""


def unknown(update: Update, context: CallbackContext):
    """判断私聊或者群内@时，不理解的命令，进行回复"""
    # print(f"{context.bot.name}\t{update.effective_message.text}\t{update.effective_chat.type}")
    if context.bot.name in update.effective_message.text or update.effective_chat.type == 'private':
        update.message.reply_text('对不起，我不理解这个命令 /help')


def echo_msg(update: Update, context: CallbackContext):
    if update.message.text == 'chatid':
        update.message.reply_markdown(f"chatID: `{update.effective_chat.id}`")


def add_admin(update: Update, context: CallbackContext):
    """添加已存在的用户ID为管理员"""
    if is_admin(update.effective_user.id):
        new_admin_id = ''.join(context.args)
        if new_admin_id in get_ids():
            if is_admin(new_admin_id):
                update.message.reply_text(f'{new_admin_id} 用户已经是管理员了！')
            else:
                save_id(new_admin_id, 'admin')
                update.message.reply_text(f'{new_admin_id} 管理员添加成功')
        else:
            update.message.reply_text(f'{new_admin_id} 用户不存在')
        # update.message.reply_text('欢迎您管理员')
    else:
        update.message.reply_text('非管理员不要乱动')


def main():
    """ MAIN """
    if config['PROXY']:
        update = Updater(config['BOT_TOKEN'], request_kwargs={'proxy_url': config['PROXY']})
    else:
        update = Updater(config['BOT_TOKEN'])
    dispatch = update.dispatcher
    dispatch.add_handler(CommandHandler('start', start))
    dispatch.add_handler(CommandHandler('help', help))
    dispatch.add_handler(CommandHandler('my', my))
    dispatch.add_handler(CommandHandler('create', create))
    dispatch.add_handler(CommandHandler('reset', reset))
    dispatch.add_handler(CommandHandler('bind', bind))
    dispatch.add_handler(CommandHandler('line', line))
    dispatch.add_handler(CommandHandler('status', status))
    dispatch.add_handler(CommandHandler('total', total))
    dispatch.add_handler(CommandHandler('search', search))
    dispatch.add_handler(CommandHandler('add_admin', add_admin))
    dispatch.add_handler(MessageHandler(Filters.command, unknown))
    # -- test
    dispatch.add_handler(MessageHandler(Filters.text & (~Filters.command), echo_msg))

    update.start_polling()
    print(f"程序已开始运行，请查看{config['LOG_FILE']}文件")
    update.idle()


if __name__ == '__main__':
    main()
