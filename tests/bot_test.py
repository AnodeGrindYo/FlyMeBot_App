import sys
import os
import json
import aiounittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from booking_details import BookingDetails
from config import DefaultConfig
from dialogs import BookingDialog, MainDialog
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper, Intent

from botbuilder.dialogs.prompts import TextPrompt

from botbuilder.core import (
    TurnContext, 
    ConversationState, 
    MemoryStorage
)

from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.core.adapters import TestAdapter

class LuisTest(aiounittest.AsyncTestCase):

    # Test la requête vers Luis et la réponse obtenue
    async def test_luis_query(self):

        CONFIG = DefaultConfig()
        RECOGNIZER = FlightBookingRecognizer(CONFIG)

        async def exec_test(turn_context: TurnContext):

            intent, result = await LuisHelper.execute_luis_query(RECOGNIZER, turn_context)

            await turn_context.send_activity(
                json.dumps(
                    {
                        "intent": intent,
                        "booking_details": None if not hasattr(result, "__dict__") else result.__dict__,
                    }
                )
            )

        adapter = TestAdapter(exec_test)

        await adapter.test(
            "Hello",
            json.dumps(
                {
                    "intent": Intent.NONE_INTENT.value,
                    "booking_details": None,
                }
            ),
        )

        await adapter.test(
            "Hello, I want to go to Paris",
            json.dumps(
                {
                    "intent": Intent.BOOK_FLIGHT.value,
                    "booking_details": BookingDetails(
                        destination="Paris"
                    ).__dict__,
                }
            ),
        )

        await adapter.test(
            "I want to book a flight from Berlin. My budget is 300$. I will leave the 20 december 2022 and coming back the 2 january 2023.",
            json.dumps(
                {
                    "intent": Intent.BOOK_FLIGHT.value,
                    "booking_details": BookingDetails(
                        origin = "Berlin",
                        start_date = "2022-12-20",
                        end_date = "2023-01-02",
                        budget = 300
                    ).__dict__,
                }
            ),
        )


class BotTest(aiounittest.AsyncTestCase):

    # Test une réservation étape par étape
    async def test_booking_step_by_step(self):
        async def exec_test(turn_context: TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()

            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)


        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)

        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("WFDialog")
        dialogs.add(wf_dialog)

        adapter = TestAdapter(exec_test)

        await adapter.test("Hello", "What can I help you with today?")
        await adapter.test("I want to go to Paris", "From what city will you be travelling?")
        await adapter.test("from New York", "On what date would you like to travel?")
        await adapter.test("the 21 september 2022", "On what date would you like to return?")
        await adapter.test("the 5 october 2022", "What is your budget for traveling?")
        await adapter.test(
            "my bydget is 600$",
            "Please confirm, I have you traveling from: from New York to: Paris departure: 2022-09-21 return: 2022-10-05 price: my bydget is 600$. (1) Yes or (2) No"
            )

    # Test une annulation de réservation
    async def test_booking_cancel(self):
        async def exec_test(turn_context: TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()

            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)


        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)

        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("WFDialog")
        dialogs.add(wf_dialog)

        adapter = TestAdapter(exec_test)

        await adapter.test("Hello", "What can I help you with today?")
        await adapter.test("I want to leave from Paris", "To what city would you like to travel?")
        await adapter.test("Cancel", "Cancelling")

    # Test une réservation en fournissant toutes les informations en une seule fois
    async def test_booking_one_shot(self):
        async def exec_test(turn_context: TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()

            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)


        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)

        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("WFDialog")
        dialogs.add(wf_dialog)

        adapter = TestAdapter(exec_test)

        await adapter.test("Hello", "How can I help you?")
        await adapter.test(
            "I want to book a flight from Toulouse to Madrid. My budget is 300$. I will leave the 24 december 2022 and coming back the 18 january 2023.",
            "Please confirm, I have you traveling from: Toulouse to: Madrid departure: 2022-12-24 return: 2023-01-18 price: 300. (1) Yes or (2) No"
            )
            