import reflex as rx

from webui import styles
from webui.state import State


def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.breadcrumb(
                    rx.breadcrumb_item(
                        rx.heading("Venture Chatitalist", size="sm"),
                    )
                ),
            ),
            justify="space-between",
        ),
        bg=styles.bg_dark_color,
        backdrop_filter="auto",
        backdrop_blur="lg",
        p="4",
        border_bottom=f"1px solid {styles.border_color}",
        position="sticky",
        top="0",
        z_index="100",
    )
