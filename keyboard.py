from kivy.core.window import Window
from kivy.uix.widget import Widget


class MyKeyboardListener(Widget):

    def __init__(self, app, **kwargs):
        self.app = app
        super(MyKeyboardListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        #print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print('The key', keycode, 'have been pressed')
        #print(' - text is %r' % text)
        #print(' - modifiers are %r' % modifiers)

        if keycode[1] == 'enter':
            self.app.handle_message(self.app.textinput.text, self.app.myip)
            self.app.mainlabel.text += "\n"
            self.app.textinput.text = ''
        else:
            self.app.textinput.text += text
            self.app.mainlabel.text += text

        #if keycode[1] == 'r':
            #self.app.mainlabel.text += 'reprint\n'
        #if keycode[1] == 'u':
            #self.app.mainlabel.text += 'user\n'



        # If we hit escape, release the keyboard
        #if keycode[1] == 'q':
        #    keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return text
