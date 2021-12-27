from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CallbackContext

from data.utils import delete_last_message, get_config, save_config


@delete_last_message
def show_data(_, context: CallbackContext):
    cfg = get_config()
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=key, callback_data=key)] for key in cfg.keys()] +
        [[InlineKeyboardButton(text='Вернуться назад', callback_data='menu')]])
    return (context.bot.send_message(context.user_data['user'].id, 'Выберите переменную', reply_markup=markup),
            'data_requesting')


@delete_last_message
def request_changing_data(_, context: CallbackContext):
    context.user_data['key_to_change'] = context.match.string
    current_value = get_config()[context.match.string]
    if isinstance(current_value, list):
        current_value = ';'.join(map(str, current_value))
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Вернуться назад', callback_data='data')]])
    return context.bot.send_message(
        context.user_data['user'].id,
        f'На что вы хотите заменить <b>{context.match.string}</b>?\n'
        f'\n<b>Текущее значение:</b> {current_value}\n'
        'Если это список, то введите элементы через ;', reply_markup=markup,
        disable_web_page_preview=True, parse_mode=ParseMode.HTML), 'data'


def change_data(update, context):
    if context.user_data.get('message'):
        context.user_data.pop('message').delete()
    cfg = get_config()
    key = context.user_data['key_to_change']
    if key == 'admins' and str(update.message.from_user.id) not in update.message.text.split(';'):
        update.message.reply_text('Вы не можете удалить сами себя из admins')
        return show_data(update, context)
    if isinstance(cfg[key], list):
        cfg[key] = [val.strip() for val in update.message.text.split(';')]
    else:
        cfg[key] = update.message.text.strip()
    save_config(cfg)
    update.message.reply_text(f'Переменная <b>{context.user_data["key_to_change"]}</b> была обновлена',
                              parse_mode=ParseMode.HTML)
    return show_data(update, context)


@delete_last_message
def ask_resetting_data(_, context):
    markup = ReplyKeyboardMarkup([[KeyboardButton('Да')],
                                  [KeyboardButton('Нет')]],
                                 one_time_keyboard=True, resize_keyboard=True)
    return context.bot.send_message(context.user_data['user'].id,
                                    'Вы уверены, что хотите сбросить настройки до серверных?',
                                    reply_markup=markup), 'data_resetting'
