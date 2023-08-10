from colorama import Fore
import timeit
import os
import subprocess


def get_init_time():
    """
    Records initial time
    :return: float                      Initial time
    """
    start_time = timeit.default_timer()
    return start_time


def truncate(n, decimals=0):
    """
    Truncates time with given decimal points
    :param n: float                     Time
    :param decimals: int                Decimal points
    :return: float                      Truncated time
    """
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def get_time(start_time):
    """
    Prints running time in seconds and minutes
    :param start_time: float            Initial time
    :return: None
    """
    elapsed = timeit.default_timer() - start_time
    print('Running time: ', truncate(elapsed, 1), ' seconds')
    print('Running time: ', truncate(elapsed / float(60), 2), ' minutes')


def initiate_msg(text):
    print(Fore.LIGHTBLUE_EX + text + Fore.WHITE)


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)


def create_folder(directory):
    """
    creates directory
    :param directory: str                   Directory to be created
    :return: None
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Creating directory. " + directory)


def export_figure(figure, **kwargs):
    """
    Saves figure as .emf
    :param figure: fig handle
    :param kwargs: filepath: str                File name, e.g. '*\filename'
    :return: None
    """
    inkscape_path = kwargs.get('inkscape', "C://Program Files//Inkscape//bin//inkscape.exe")
    filepath = kwargs.get('filename', None)
    filetype = kwargs.get('filetype', None)
    if filepath is not None:
        path, filename = os.path.split(filepath)
        filename, extension = os.path.splitext(filename)
        svg_filepath = os.path.join(path, filename + '.svg')
        target_filepath = os.path.join(path, filename + f'.{filetype}')
        figure.savefig(svg_filepath, bbox_inches='tight', format='svg')
        subprocess.call([inkscape_path, svg_filepath, f'--export-{filetype}', target_filepath])
        # os.remove(svg_filepath)
