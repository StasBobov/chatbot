from copy import deepcopy
from pprint import pprint
from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEvent

import settings
from bot import Bot


class Test1(TestCase):
    RAW_EVENT = ({'group_id': 93989305, 'type': 'message_new', 'event_id': '9a6484bad8ff5362256f480100dd92d45e2480b9',
                'v': '5.131',
                'object': {'message': {'date': 1666022407, 'from_id': 5958128, 'id': 331, 'out': 0, 'attachments': [],
                    'conversation_message_id': 331, 'fwd_messages': [], 'important': False, 'is_hidden': False,
                    'peer_id': 5958128, 'random_id': 0, 'text': 'где'},
                'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback',
                'intent_subscribe', 'intent_unsubscribe'], 'keyboard': True, 'inline_keyboard': True, 'carousel': True,
            'lang_id': 0}
                        }})

    def test_run(self):
        count = 5
        obj = Mock()
        obj.obj.from_id,  obj.obj.peer_id= 0, 0 # заглушки для получаемых event - ов
        events = [obj] * count # [obj, obj, ...]
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = Mock(return_value=events)
        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == count

    INPUTS =[
        'Привет',
        'А когда?',
        'Где будет конференция?',
        'Зарегистрируй меня',
        'Вениамин',
        'мой адрес email@mail',
        'email@mail.ru'
    ]
    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name='Вениамин', email='email@mail.ru')
    ]
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send: Mock = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT) # возвращает полную копию целого объекта self.RAW_EVENT
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.run()

        # валидируем, что функция запускалась столько же раз, сколько было input-ов
        assert send_mock.call_count == len(self.INPUTS)
        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS




























    # def test_event(self):
    #     event = VkBotMessageEvent(raw=self.RAW_EVENT)
    #     with patch('bot.vk_api.VkApi'):
    #         with patch('bot.VkBotLongPoll'):
    #             bot = Bot('', '')
    #             # bot.api = Mock()
    #             bot.api.messages.send = Mock()
    #             bot.on_event(event)
    #
    #             # проверяем, что bot.api.messages.send вызвался 1 раз с такими параметрами:
    #             bot.api.messages.send.assert_called_once_with(peer_id=event.object.message['peer_id'],
    #                                               message='Это ты, Особо?"',
    #                                               random_id=ANY)
    #
