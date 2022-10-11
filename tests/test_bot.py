from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from config import DefaultConfig

CONFIG = DefaultConfig()



def test_luis_intent():
    """Vérifie la top intent
    """
    # Instantiate prediction client
    clientRuntime = LUISRuntimeClient(
        CONFIG.LUIS_API_ENDPOINT,
        CognitiveServicesCredentials(CONFIG.LUIS_API_KEY))
    # Create request
    request ='book a flight from cok to cdg from 01/01/2021 to 02/02/2021 for a budget of 3500 euros'

    # Get response
    response = clientRuntime.prediction.resolve(CONFIG.LUIS_APP_ID, query=request)

    check_top_intent = 'BookFlight'
    is_top_intent = response.top_scoring_intent.intent
    assert check_top_intent == is_top_intent


def test_luis_origin():
    """Vérifie la  détection de la ville d'origine
    """
    # Instantiate prediction client
    clientRuntime = LUISRuntimeClient(
        CONFIG.LUIS_API_ENDPOINT,
        CognitiveServicesCredentials(CONFIG.LUIS_API_KEY))
    
    # Create request
    request ='I want to book a flight from Toulouse to Mexico from 18/01/2022 to 01/02/2023. I have a budget of 1000€'

    # Get response
    response = clientRuntime.prediction.resolve(CONFIG.LUIS_APP_ID, query=request)
    
    check_origin = 'toulouse'
    all_entities = response.entities
    
    for i in range(0, len(all_entities)):
        if all_entities[i].type == 'or_city':
            is_origin = all_entities[i].entity
    
    assert check_origin == is_origin


def test_luis_destination():
    """vérifie la détection de la ville de destination
    """
    # Instantiate prediction client
    clientRuntime = LUISRuntimeClient(
        CONFIG.LUIS_API_ENDPOINT,
        CognitiveServicesCredentials(CONFIG.LUIS_API_KEY))
    
    # Create request
    request ='I want to book a flight from Toulouse to Mexico from 18/01/2022 to 01/02/2023. I have a budget of 1000€'

    # Get response
    response = clientRuntime.prediction.resolve(CONFIG.LUIS_APP_ID, query=request)
    
    check_destination = 'mexico'
    all_entities = response.entities
    
    for i in range(0, len(all_entities)):
        if all_entities[i].type == 'dst_city':
            is_destination = all_entities[i].entity
    
    assert check_destination == is_destination


def test_luis_budget():
    """Vérifie la détection du budget
    """
    # Instantiate prediction client
    clientRuntime = LUISRuntimeClient(
        CONFIG.LUIS_API_ENDPOINT,
        CognitiveServicesCredentials(CONFIG.LUIS_API_KEY))
    
    # Create request
    request ='I want to book a flight from Toulouse to Mexico from 18/01/2022 to 01/02/2023. I have a budget of 1000€'

    # Get response
    response = clientRuntime.prediction.resolve(CONFIG.LUIS_APP_ID, query=request)
    
    check_budget = '1000 €'
    all_entities = response.entities
    
    for i in range(0, len(all_entities)):
        if all_entities[i].type == 'budget':
            is_budget = all_entities[i].entity
    
    assert check_budget == is_budget