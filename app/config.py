
import json

from dataclasses import dataclass
from windows_toasts import (
    WindowsToaster,
    Toast,
    ToastScenario
)


@dataclass
class TheMutenatorConfig:
    meeting_app: str
    volume_decrease_percent: int
    exceptions: list[str]


def read_config() -> TheMutenatorConfig:
    with open('the_mutenator.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    config = TheMutenatorConfig(
        volume_decrease_percent=data.get('volume_decrease_percent', 80),
        exceptions=data.get('exceptions', []),
        meeting_app=data.get('meeting_app', 'ms-teams')
    )

    config.exceptions.append(config.meeting_app)

    return config


def full_app_name(app: str) -> str:
    if app.endswith('.exe'):
        return app.lower()
    else:
        return f'{app.lower()}.exe'


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
