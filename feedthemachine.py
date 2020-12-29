from pynput import keyboard
import os

cnt = 0

voice = [
 'say "Yum!"',
 'say "Thanks."',
 'say "Merry Christmas."',
 'say "Thanks!"',
 'say "Yum!"',
 'say "Thanks!"',
 'say "Yum!"',
 'say "Just a couple more."',
 'say "Yum!"',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',
 'say "That is enough. Another lock number is three."',

]

def on_press(key):
    global cnt
    global voice
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
        # send to default printer
        if key.char == '5' or key.char == '6' or key.char == 23:
            os.system(voice[cnt])
            cnt = cnt + 1

            if cnt == 10 or cnt == 20:
              print("sending to printer")
              os.system("lp -o landscape odetojoy.pdf")

        if key.char == 'r':
            # reset cnt  (for test purposes)
            cnt = 0

    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()
