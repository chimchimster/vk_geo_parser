import re
import time
import pyperclip
import webbrowser
import pyautogui as py


class CoordinatesCollector:

    firefox_path = 'snap/bin/firefox'

    def __init__(self, location):
        self.location = location
        self.browser = webbrowser

        # Initialize firefox browser
        self.browser.register('firefox', None, webbrowser.BackgroundBrowser(self.firefox_path))

    def collect_coordinates(self):
        self.browser.open('https://google.com/maps')
        time.sleep(3)

        py.click(x=202, y=194)
        time.sleep(3)

        self.__type(self.location, interval=0.25)
        time.sleep(3)

        py.press('enter')
        time.sleep(3)

        # Select data from get request
        py.click(x=518, y=119)
        time.sleep(3)

        pyperclip.copy('')
        time.sleep(3)
        py.hotkey('ctrl', 'c')
        time.sleep(3)

        link_with_get_data = pyperclip.paste()

        # Retrieve coordinates
        suitable = re.findall(r'\d+\.\d+\,\d+\.\d+', link_with_get_data)

        print(py.position())
        py.click(x=547, y=82)

        return suitable

    def __paste(self, text: str):
        pyperclip.copy(text)
        py.hotkey('ctrl', 'v')

    def __type(self, text: str, interval: float = 0.0):
        buffer = pyperclip.paste()
        if not interval:
            self.__paste(text)
        else:
            for char in text:
                self.__paste(char)
                time.sleep(interval)

        pyperclip.copy(buffer)
