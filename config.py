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
    
    # LUIS_APP_ID = "74f68d80-8b03-45b0-bc98-a256adb35ef5"
    # # LUIS_API_KEY = "d293cf63a16f4efdb783caa618ec1c8a"
    # LUIS_API_KEY = "59945099b3124e2ebd1c164b71a6507e"
    # LUIS_API_HOST_NAME = "westeurope.api.cognitive.microsoft.com"
    # APPINSIGHTS_INSTRUMENTATION_KEY = "InstrumentationKey=3aa1e02c-e977-4c9b-9b2a-7b20f00a9cb8;IngestionEndpoint=https://francecentral-1.in.applicationinsights.azure.com/;LiveEndpoint=https://francecentral.livediagnostics.monitor.azure.com/"
    # # APPINSIGHTS_INSTRUMENTATION_KEY = "3aa1e02c-e977-4c9b-9b2a-7b20f00a9cb8"
 