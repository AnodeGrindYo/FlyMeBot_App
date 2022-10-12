from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails


class Intent(Enum):
    BOOK_FLIGHT = "BookFlight"
    CANCEL = "Cancel"
    NONE_INTENT = "None"

MAP_KEY_ATTR = {
    'or_city': 'origin', 
    'dst_city':'destination', 
    'str_date': 'start_date', 
    'end_date': 'end_date', 
    'budget': 'budget'
}
MAP_KEY_TYPE = {
    'or_city': 'geographyV2_city', 
    'dst_city':'geographyV2_city', 
    'str_date': 'datetime', 
    'end_date': 'datetime', 
    'budget': 'number'
}

def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)
            intent = recognizer_result.get_top_scoring_intent().intent

            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()

                for (key, type) in MAP_KEY_TYPE.items():
                    entity = LuisHelper._get_entity(recognizer_result, key, type)

                    if entity is not None:
                        setattr(result, MAP_KEY_ATTR[key], entity)
                
                    

        except Exception as exception:
            print(exception)

        return intent, result

    # Return the right entity in the Json
    def _get_entity(recognizer_result, key, type):

        if (recognizer_result.entities.get("$instance") is None
            or recognizer_result.entities.get(key) is None
            or len(recognizer_result.entities.get(key)) == 0) :
            return None

        score = 0
        index = None

        for i, entity in enumerate(recognizer_result.entities.get("$instance").get(key)):
            if entity['score'] > score:
                score = entity['score']
                index = i

        selected_entity = recognizer_result.entities.get("$instance").get(key)[index]

        score = 100
        index = None

        for i, entity in enumerate(recognizer_result.entities.get("$instance").get(type)):
            s = abs(entity['startIndex'] - selected_entity['startIndex']) + abs(entity['endIndex'] - selected_entity['endIndex'])
            if s < score:
                score = s
                index = i


        if (index is None
            or recognizer_result.entities.get(type) is None
            or len(recognizer_result.entities.get(type)) <= index):
            return None
        
        return (
            recognizer_result.entities.get(type)[index].capitalize()
            if type == 'geographyV2_city'
            else recognizer_result.entities.get(type)[index]["timex"][0]
            if type == 'datetime'
            else recognizer_result.entities.get(type)[index]
            if type == 'number'
            else None
        )