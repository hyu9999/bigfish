import os
import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bigfish.settings.base")
channel_layer = channels.asgi.get_channel_layer()