import asyncio

from flet import (
    Page,
    app,
    MainAxisAlignment,
    Container,
    colors,
    Tabs,
    Tab,
)

from plugins.register import plugins_all
import constants


def add_plugins(page: Page) -> None:
    logs_view_plugins = [plugin(page) for plugin in plugins_all]

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
    page.title = "Flet counter example"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.window.width, page.window.max_width, page.window.min_width = [constants.PAGE_WIDTH] * 3
    page.window.height, page.window.max_height, page.window.min_height = [constants.PAGE_HEIGHT] * 3

    add_plugins(page)


if __name__ == '__main__':
    app(main)
