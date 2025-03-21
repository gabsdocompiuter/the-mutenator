import sys
import pystray
import threading

from PIL import Image, ImageFile
from typing import Any

from app.the_mutenator import TheMutenator


STOP_EVENT: threading.Event = threading.Event()
volume_on_ico: ImageFile = Image.open('icons/volume-on.ico')


def close_app(icon, item) -> None:
    icon.stop()
    STOP_EVENT.set()
    sys.exit()


icon = pystray.Icon(
    name='the_mutenator',
    icon=volume_on_ico,
    title='The Mutenator',
    menu=pystray.Menu(
        pystray.MenuItem('Fechar', close_app)
    )
)

the_mutenator = TheMutenator(icon)


if __name__ == '__main__':
    the_mutenator.start_monitoring(STOP_EVENT)
    icon.run()
