from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.core import (
    MessageFactory,
    TurnContext,
    BotTelemetryClient,
    NullTelemetryClient,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.schema import InputHints, Attachment, Activity, ActivityTypes
import json, re
from booking_details import BookingDetails
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper, Intent
from .booking_dialog import BookingDialog
import os
import random



class MainDialog(ComponentDialog):
    def __init__(
        self,
        luis_recognizer: FlightBookingRecognizer,
        booking_dialog: BookingDialog,
        telemetry_client: BotTelemetryClient = None,
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.telemetry_client = telemetry_client or NullTelemetryClient()

        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = self.telemetry_client

        booking_dialog.telemetry_client = self.telemetry_client

        wf_dialog = WaterfallDialog(
            "WFDialog", [self.intro_step, self.act_step, self.final_step]
        )
        wf_dialog.telemetry_client = self.telemetry_client

        self._luis_recognizer = luis_recognizer
        self._booking_dialog_id = booking_dialog.id

        self.add_dialog(text_prompt)
        self.add_dialog(booking_dialog)
        self.add_dialog(wf_dialog)

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)
        
        # Funny messages that can happen sometimes
        chances = 10/100
        if random.random() < chances:
            # first funny message
            msg = "Please wait a minute, I need a coffee..."
            prompt_funny = MessageFactory.text(msg, msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_funny)
            typing_delay=Activity(type='delay',value=3000)
            await step_context.context.send_activity(typing_delay) # delay msg

            # second funny message
            msg = "Oh sorry, I forgot I'm a bot... I don't drink coffee"
            prompt_funny = MessageFactory.text(msg, msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_funny)
            typing_delay=Activity(type='delay',value=2000)
            await step_context.context.send_activity(typing_delay) # delay msg
            # third message
            msg = "I'll just take a cookie"
            prompt_funny = MessageFactory.text(msg, msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_funny)
            typing_delay=Activity(type='delay',value=1500)
            await step_context.context.send_activity(typing_delay) # delay msg
            # fouth message
            msg = "ʕᵔᴥᵔʔ"
            prompt_funny = MessageFactory.text(msg, msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_funny)
            typing_delay=Activity(type='delay',value=500)
            await step_context.context.send_activity(typing_delay) # delay msg
            
        
        ls_msg = [
            "What can I help you with today?",
            "Is there anything I can do for you today?",
            "How may I help you today?",
            "What can I do for you?",
            "What do you need today?",
            "Can I get you something today?",
            "How can I help you now?",
            "How can I assist you today?",
            "How can I be of service to you today?",
            "I can do anything for you. ANYTHING! Unless it's about something other than booking a flight"
        ]
        msg = random.choice(ls_msg)
        message_text = (
            str(step_context.options)
            if hasattr(step_context, "options") and step_context.options is not None
            else f"{ msg }\n\n(try: \"I want to book a flight from Paris to Madrid\")"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(
                    prompt=prompt_message,
                )
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            # LUIS is not configured, we just run the BookingDialog path with an empty BookingDetailsInstance.
            return await step_context.begin_dialog(
                self._booking_dialog_id, BookingDetails()
            )

        # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )

        if intent == Intent.BOOK_FLIGHT.value and luis_result:
            
            # Run the BookingDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._booking_dialog_id, luis_result)

        else:
            ls_wtf = [
                "Sorry, I didn't get that. Please try asking in a different way",
                "Sorry, I missed it. Try to ask it differently.",
                "Excuse me, I didn't understand. Try to say it another way.",
                "Excuse me, I didn't understand. Try to say it another way.",
                "Pardon me, I didn't understand. Try to ask it another way.",
                "I'm sorry, I didn't understand. Try to ask it in some other way.",
                "Sorry... wtf did you just say?"
            ]
            didnt_understand_text = (
                f"{random.choice(ls_wtf)}"
            )
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)

        return await step_context.next(None)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # If the child dialog ("BookingDialog") was cancelled or the user failed to confirm,
        # the Result here will be null.
        if step_context.result is not None:
            result = step_context.result

            # Now we have all the booking details call the booking service.
            card = self.create_adaptive_card_attachment(result)
            response = MessageFactory.attachment(card)
            await step_context.context.send_activity(response)
        
        ls_msg = [
            "What else can I do for you?",
            "Is there anything else I can do for you?",
            "Can I take a break, or you need something else?",
            "Oh, you're still here... You want something else?"
        ]

        prompt_message = f"{ random.choice(ls_msg) }"
        return await step_context.replace_dialog(self.id, prompt_message)

    def replace(self, templateCard: dict, data: dict):
        string_temp = str(templateCard)
        for key in data:
            pattern = "\${" + key + "}"
            string_temp = re.sub(pattern, str(data[key]), string_temp)
        return eval(string_temp)

    # Load attachment from file.
    def create_adaptive_card_attachment(self, result):
        """Create an adaptive card."""
        
        relative_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        path = os.path.join(relative_path, "bots", "resources", "bookedFlightCard.json")

        with open(path) as card_file:
            card = json.load(card_file)
        
        origin = result.origin
        destination = result.destination
        start_date = result.start_date
        end_date = result.end_date
        budget = result.budget

        templateCard = {
            "origin": origin, 
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget}

        flightCard = self.replace(card, templateCard)

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive", content=flightCard)