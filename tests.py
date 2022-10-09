from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent

from bot import Bot


class Test1(TestCase):
    RAW_EVENT = {'group_id': 93989305, 'type': 'message_new', 'event_id': '35f247f5994c15348f40b1b65a6bca0688096985',
                 'v': '5.131', 'object': {'message': {'date': 1665334193, 'from_id': 5958128, 'id': 74, 'out': 0,
                'attachments': [], 'conversation_message_id': 74, 'fwd_messages': [], 'important': False,
                'is_hidden': False, 'peer_id': 5958128, 'random_id': 0, 'text': 'iii'}, 'client_info':
                 {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe',
                 'intent_unsubscribe'], 'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}}}

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

    def test_event(self):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)
        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll'):
                bot = Bot('', '')
                # bot.api = Mock()
                bot.api.messages.send = Mock()
                bot.on_event(event)

                # проверяем, что bot.api.messages.send вызвался 1 раз с такими параметрами:
                bot.api.messages.send.assert_called_once_with(peer_id=event.object.message['peer_id'],
                                                  message='Это ты, Особо?"',
                                                  random_id=ANY)

