import threading
import pythoncom
import pystray

from PIL import Image

from pycaw.pycaw import (
    AudioSession,
    AudioUtilities,
    ISimpleAudioVolume,
    IAudioMeterInformation,
)

from app.config import TheMutenatorConfig, read_config, full_app_name, show_notification

class TheMutenator:
    config: TheMutenatorConfig = read_config()
    has_meeting_in_progress: bool = False
    icon: pystray.Icon


    def __init__(self, icon: pystray.Icon) -> None:
        self.icon = icon


    def meeting_in_progress(self) -> bool:
        sessions: list[AudioSession] = AudioUtilities.GetAllSessions()
        for session in sessions:
            session: AudioSession

            try:
                if session.Process and session.Process.name().lower() == full_app_name(self.config.meeting_app):
                    audio_meter = session._ctl.QueryInterface(IAudioMeterInformation)
                    audio_level = audio_meter.GetPeakValue()
                    if audio_level > 0:
                        return True
            except:
                continue
        return False


    def _change_apps_volume(self, volume_change: int) -> None:
        exceptions: list[str] = [
            full_app_name(app)
            for app in self.config.exceptions
        ]

        apps_ajustados: list[str] = []

        sessions: list[AudioSession] = AudioUtilities.GetAllSessions()
        for session in sessions:
            session: AudioSession

            try:
                if not session.Process or session.Process.name().lower() in exceptions:
                    continue

                app_volume = session._ctl.QueryInterface(ISimpleAudioVolume)

                volume_atual = app_volume.GetMasterVolume()
                novo_volume = volume_atual + volume_change / 100

                novo_volume = 0 if novo_volume < 0 else novo_volume
                novo_volume = 1 if novo_volume > 1 else novo_volume

                app_volume.SetMasterVolume(novo_volume, None)

                apps_ajustados.append(session.Process.name().lower())
            except:
                continue

        notification_text: str = f'Volume dos apps {f'reduzido em {self.config.volume_decrease_percent}%' if volume_change < 0 else 'aumentado novamente'}'
        show_notification(notification_text, apps_ajustados)


    def mute_apps(self, stop_event: threading.Event) -> None:
        pythoncom.CoInitialize()
        try:
            while not stop_event.is_set():
                if self.meeting_in_progress():
                    if not self.has_meeting_in_progress:
                        self._change_apps_volume(self.config.volume_decrease_percent * -1)
                        self.has_meeting_in_progress = True
                        self.change_icon(True)
                elif self.has_meeting_in_progress:
                    self._change_apps_volume(self.config.volume_decrease_percent)
                    self.has_meeting_in_progress = False
                    self.change_icon(False)
        finally:
            pythoncom.CoUninitialize()


    def change_icon(self, in_meeting: bool) -> None:
        icon_path = f'icons/volume-{'off' if in_meeting else 'on'}.ico'
        self.icon.icon = Image.open(icon_path)
        self.icon.title = 'Em reunião' if in_meeting else 'Disponível'
        self.icon._update_icon()


    def start_monitoring(self, stop_event: threading.Event) -> threading.Thread:
        thread = threading.Thread(
            target=self.mute_apps,
            args=(stop_event,),
            daemon=True,
        )
        thread.start()
        return thread
