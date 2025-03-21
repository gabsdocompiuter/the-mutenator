import json

from dataclasses import dataclass
from windows_toasts import (
    WindowsToaster,
    Toast,
    ToastScenario
)
from pycaw.pycaw import (
    AudioSession,
    AudioUtilities,
    ISimpleAudioVolume,
    IAudioMeterInformation,
)


@dataclass
class TheMutenatorConfig:
    meeting_app: str
    volume_downcrase: int
    exceptions: list[str]


def read_config() -> TheMutenatorConfig:
    with open('the_mutenator.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    config = TheMutenatorConfig(
        volume_downcrase=data.get('volume_downcrase', 20),
        exceptions=data.get('exceptions', []),
        meeting_app=data.get('meeting_app', 'teams')
    )

    config.exceptions.append(config.meeting_app)

    return config


def formatar_list(app_list: list[str]) -> str:
    if not app_list:
        return ''
    elif len(app_list) == 1:
        return app_list[0]
    else:
        return ', '.join(app_list[:-1]) + ' e ' + app_list[-1]


def show_notification(notification_text: str, app_list: list[str]) -> None:
    toaster = WindowsToaster('The Mutenator')
    toast = Toast(scenario=ToastScenario.Important)
    toast.text_fields = [
        notification_text,
        formatar_list(app_list).replace('.exe', '')
    ]
    toaster.show_toast(toast)


def full_app_name(app: str) -> str:
    if app.endswith('.exe'):
        return app.lower()
    else:
        return f'{app.lower()}.exe'


def meeting_in_progress(config: TheMutenatorConfig) -> bool:
    sessions: list[AudioSession] = AudioUtilities.GetAllSessions()
    for session in sessions:
        session: AudioSession

        if session.Process and session.Process.name().lower() == full_app_name(config.meeting_app):
            audio_meter = session._ctl.QueryInterface(IAudioMeterInformation)
            audio_level = audio_meter.GetPeakValue()
            if audio_level > 0:
                return True
    return False


def change_apps_volume(config: TheMutenatorConfig, volume_change: int) -> None:
    exceptions: list[str] = [
        full_app_name(app)
        for app in config.exceptions
    ]

    apps_ajustados: list[str] = []

    sessions: list[AudioSession] = AudioUtilities.GetAllSessions()
    for session in sessions:
        session: AudioSession

        if not session.Process or session.Process.name().lower() in exceptions:
            continue

        app_volume = session._ctl.QueryInterface(ISimpleAudioVolume)

        volume_atual = app_volume.GetMasterVolume()
        novo_volume = volume_atual + volume_change / 100

        novo_volume = 0 if novo_volume < 0 else novo_volume
        novo_volume = 1 if novo_volume > 1 else novo_volume

        app_volume.SetMasterVolume(novo_volume, None)

        apps_ajustados.append(session.Process.name().lower())

    notification_text: str = f'Volume dos apps {f'reduzido em {config.volume_downcrase}%' if volume_change < 0 else 'aumentado novamente'}'
    show_notification(notification_text, apps_ajustados)


def mute_apps() -> None:
    config: TheMutenatorConfig = read_config()
    active_meeting: bool = False

    while True:
        if meeting_in_progress(config):
            if not active_meeting:
                change_apps_volume(config, config.volume_downcrase * -1)
                active_meeting = True
        elif active_meeting:
            change_apps_volume(config, config.volume_downcrase)
            active_meeting = False


if __name__ == '__main__':
    mute_apps()
