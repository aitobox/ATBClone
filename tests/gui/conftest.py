import pytest
import toga


@pytest.fixture(autouse=True)
def toga_app():
    if toga.App.app is None:
        app = toga.App(formal_name="TestApp", app_id="com.test.app")
    else:
        app = toga.App.app
    return app
