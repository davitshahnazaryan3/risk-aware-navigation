from colorama import Fore


def initiate_msg(text):
    print(Fore.LIGHTBLUE_EX + text + Fore.WHITE)


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
