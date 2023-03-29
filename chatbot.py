#!/usr/bin/python

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot import languages

# Set the language of the bot and fixes chatterbot.exceptions.LanguageNotSupportedError: The language 'en' is not supported
languages.ENG.ISO_639_1 = "en_core_web_sm"


class ChatBotApp:
    def __init__(self):
        self.chatbot = ChatBot('ChatterBot')
        trainer = ChatterBotCorpusTrainer(self.chatbot)
        
        trainer.train("chatterbot.corpus.english")
        trainer.train("chatterbot.corpus.english.greetings",
                    "./resources/corpus/cybersecurity.yml",
                    "./resources/corpus/data_encryption.yml",
                    "./resources/corpus/malware.yml",
                    "./resources/corpus/network_security.yml",
                    "./resources/corpus/safety_browsing.yml",
                    "./resources/corpus/safety_email.yml",
                    "./resources/corpus/safety_internet.yml",)


    def get_response(self, message):
        response = self.chatbot.get_response(message)
        return str(response)
