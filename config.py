import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.environ.get("LUIS_APP_ID", "")
    LUIS_API_KEY = os.environ.get("LUIS_API_KEY", "")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LUIS_API_HOST_NAME", "")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get("APPINSIGHTS_INSTRUMENTATION_KEY", "")
    LUIS_API_ENDPOINT = os.environ.get("LUIS_API_ENDPOINT", "")
    