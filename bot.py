import json
from pprint import pprint
import random
import vk_api
import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import handlers

log = logging.getLogger('bot')

try:
    import settings
except ImportError:
    exit("DO cp settings.py.default settings.py")


def configure_logging():
    log.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(name)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename='bot.log', encoding='UTF-8', mode='w')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(message)s', datefmt='%d-%m-%Y %H:%M'))  # TODO
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)


class UserState:
    def __init__(self, scenario_name, step_name, context=None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}



class Bot:
    """ Бот-синебот для vk.com с поддержкой IP "Товарищ майор - удалённый доступ" """

    def __init__(self, group_id, token):
        """

        :param group_id: групп ID из группы vk
        :param token: секретный токен
        """
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()
        self.user_states = dict() # user ID : user state

    def run(self):
        """ Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Вот, что пошло не так: ')

    def on_event(self, event):
        """
        Обрабатывает события
        :param event: VkBotMessageEvent object
        :return:
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            return
        user_id = event.message['from_id']
        text = event.message['text']
        if user_id in self.user_states:
            # продолжаем сценарий
            text_to_send = self.continue_scenario(user_id=user_id, text=text)
        else:
            # ищем новый интент
            go = True
            for intent in settings.INTENTS:
                if go:
                    for token in intent['tokens'].split():
                        if text.find(token) != -1:
                            if intent['answer']:
                                text_to_send = intent['answer']
                                log.debug('Пользователь с ID: %d интересовался нашим мероприятием', user_id)
                            else:
                                text_to_send = self.start_scenario(user_id, intent['scenario'])
                            go = False
                            break
                        else:
                            text_to_send = settings.DEFAULT_ANSWER

        self.api.messages.send(peer_id=user_id,
                               message=text_to_send,
                                random_id=random.randint(0, 2 ** 20))

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send


    def continue_scenario(self, user_id, text):
        state = self.user_states[user_id]  # если в сценарии
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler']) # находит функцию handle_name или handle_event
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context) # отформатировали текст при помощи значений state.context
            if next_step['next_step']:
                state.step_name = step['next_step']
                log.debug('Пользователь с ID: %d, внёс информацию: %s', user_id,
                          state.context)
            else:
                log.debug('Зарегистрировался пользователь с ID: %d, name: %s, с email: %s', user_id,
                          state.context['name'], state.context['email'])
                self.user_states.pop(user_id)
        else:
            text_to_send = step['failure_text'].format(**state.context)
        return text_to_send


if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id=settings.GROUP_ID, token=settings.TOKEN)
    bot.run()
