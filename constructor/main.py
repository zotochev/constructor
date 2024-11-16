from flet import (
    Page,
    app,
    MainAxisAlignment,
    Container,
    colors,
    Tabs,
    Tab,
    SnackBar,
    Text,
)

from event_system import EventSystem
from plugins.register import plugins_all
import constants
from events import Events


def add_plugins(page: Page, event_system: EventSystem) -> None:
    logs_view_plugins = [plugin(page, event_system) for plugin in plugins_all]

    tabs = Tabs(
        tabs=[
            Tab(plugin.name, plugin.container, adaptive=True)
            for plugin in logs_view_plugins
        ],
    )
    tabs_container = Container(content=tabs,
                               bgcolor=colors.TRANSPARENT,
                               height=constants.PAGE_HEIGHT - 60,
                               width=constants.PAGE_WIDTH,
                               padding=0)

    page.add(tabs_container)


async def main(page: Page):
    page.title = "Constructor"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.window.width, page.window.max_width, page.window.min_width = [constants.PAGE_WIDTH] * 3
    page.window.height, page.window.max_height, page.window.min_height = [constants.PAGE_HEIGHT] * 3
    event_system = EventSystem()

    def handle_error_message(message: str) -> None:
        snack_bar = SnackBar(Text(f"{message}"), open=True, duration=1000)
        page.overlay.append(snack_bar)
        page.update()

    event_system.subscribe(Events.Main.error, handle_error_message)

    add_plugins(page, event_system)


if __name__ == '__main__':
    app(main)
