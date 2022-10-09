from pprint import pprint
import random
import vk_api
import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

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

    file_handler = logging.FileHandler(filename='bot.log', encoding='UTF-8', mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(message)s', datefmt='%d-%m-%Y %H:%M'))  # TODO
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)


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

    def run(self):
        """ Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
                log.info('мне написал: from_id:, %s, peer_id: %s', event.object.from_id, event.object.peer_id)
            except Exception:
                log.exception('Вот, что пошло не так: ')

    def on_event(self, event):
        """
        Обрабатывает события
        :param event: VkBotMessageEvent object
        :return:
        """
        log.debug(event.type)
        if event.type == VkBotEventType.MESSAGE_NEW:
            log.debug(event.object.message['text'])
            self.api.messages.send(peer_id=event.object.message['peer_id'], message='Это ты, Особо?"',
                                   random_id=random.randint(0, 2 ** 20))
        elif event.type == VkBotEventType.MESSAGE_REPLY:
            log.debug('Это я ответил, БОТ')
        else:
            log.info('Хз что с этим делать', event.type)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id=settings.GROUP_ID, token=settings.TOKEN)
    bot.run()
