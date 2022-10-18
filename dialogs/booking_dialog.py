"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult, Choice
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient, CardFactory
from botbuilder.schema import InputHints, HeroCard, CardImage
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog

from config import DefaultConfig
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

import random
from datetime import datetime
import sys


CONFIG = DefaultConfig()
INSTRUMENTATION_KEY = CONFIG.APPINSIGHTS_INSTRUMENTATION_KEY

class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client

        self.logger = logging.getLogger(__name__)
        
        self.logger.addHandler(
            AzureLogHandler(
                connection_string = INSTRUMENTATION_KEY
            )
        )

        text_prompt = TextPrompt(TextPrompt.__name__)

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.origin_step,
                self.destination_step,
                self.start_date_step,
                self.end_date_step,
                self.budget_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        
        self.initial_dialog_id = WaterfallDialog.__name__

        self.add_dialog(text_prompt)
        # self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            DateResolverDialog(DateResolverDialog.START_DATE_DIALOG_ID)
        )
        self.add_dialog(
            DateResolverDialog(DateResolverDialog.END_DATE_DIALOG_ID)
        )
        self.add_dialog(waterfall_dialog)

    # Ville d'origine : première étape du waterfall
    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        
        booking_details = step_context.options
        
        ls_msg = [
            "Which city do you want to escape from ?",
            "Which town are you trying to escape from?",
            "What town do you wish to escape from?",
            "What city do you want to get out of?",
            "What city do you want to leave?",
            "What city would you like to flee from?"
        ]
        
        ls_cities = [
            "Paris",
            "Berlin",
            "Madrid",
            "Toronto",
            "Tokyo",
            "Beijing",
            "Pyongyang",
            "London",
            "Tchernobyl"
        ]

        if booking_details.origin is None:
            # msg = (
            #         f"What is your departure city ?\n\n(example: Paris)"
            #     )
            msg = (
                    f"{ random.choice(ls_msg) }\n\n(example: { random.choice(ls_cities) })"
                )
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(msg)
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.origin)

    # Ville de destination
    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        
        """Prompt for destination."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.origin = step_context.result
        
        ls_msg = [
            "In which city do you want to go?",
            "Which city would you like to go to?",
            "What city are you going to?",
            "Which town are you going to?",
            "Where do you want to go?",
            "What town do you want to move to?",
            "What city do you want to come to?",
            "What city do you wish to go to?"
        ]
        
        ls_cities = [
            "Paris",
            "Berlin",
            "Madrid",
            "Toronto",
            "Tokyo",
            "Beijing",
            "Pyongyang",
            "London",
            "Kiev... Well, maybe not Kiev",
            "Tchernobyl"
        ]

        if booking_details.destination is None:
            # msg = (
            #         f"What is your destination city ?\n\n(example: Madrid)"
            #         )
            msg = (
                    f"{ random.choice(ls_msg) }\n\n(example: { random.choice(ls_cities) })"
                )
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(msg)
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.destination)

    # Date de départ
    async def start_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for start travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.destination = step_context.result
        ls_funny = [
            f"{ booking_details.destination } is a great place !",
            f"{ booking_details.destination }! From what I see, you don't deny yourself anything!",
            f"It seems that { booking_details.destination } is pretty, at this time of the year!",
            f"{ booking_details.destination } is a lovely destination!",
            f"{ booking_details.destination }... Well, why not..."
        ]
        msg_funny = random.choice(ls_funny)
        chance_to_send_funny_msg = 90/100
        if random.random() < chance_to_send_funny_msg:
            prompt_funny = MessageFactory.text(msg_funny, msg_funny, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_funny)

        if not booking_details.start_date or self.is_ambiguous(
            booking_details.start_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.START_DATE_DIALOG_ID, booking_details.start_date
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.start_date)

    # Date de fin
    async def end_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for end travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.start_date = step_context.result

        if not booking_details.end_date or self.is_ambiguous(
            booking_details.end_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.END_DATE_DIALOG_ID, booking_details.end_date
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.end_date)

    # Budget
    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for budget."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.end_date = step_context.result
        
        # Let's compare date. If the return date is prior to departure date, we'll need a TARDIS
        print("start date : "+booking_details.start_date, file=sys.stdout)
        print("end date : "+booking_details.end_date, file=sys.stdout)
        start_date = datetime.strptime(booking_details.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(booking_details.end_date, "%Y-%m-%d")
        if end_date < start_date:
            msg_tardis = f"Wait a second... Your return date ({ booking_details.end_date }) is prior to your departure date ({booking_details.start_date})!!!"
            prompt_tardis = MessageFactory.text(msg_tardis, msg_tardis, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_tardis)
            
            msg_tardis = f"It seems you'll need a TARDIS. I'll call the Doctor"
            prompt_tardis = MessageFactory.text(msg_tardis, msg_tardis, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_tardis)
            
            card = HeroCard(
                title="Did someone call the Doctor ?",
                images=[
                    CardImage(
                        url="https://media1.giphy.com/media/bBUQPfg7l5kAM/giphy.gif?cid=790b76112d6b4038fe5c7954ca3b662d06b29e742e5d1ec8&rid=giphy.gif&ct=g"
                    )
                ]
            )
            reply_tardis = MessageFactory.list([])
            reply_tardis.attachments.append(CardFactory.hero_card(card))
            await step_context.context.send_activity(reply_tardis)

        if booking_details.budget is None:
            ls_msg = [
                "Let's talk about money... What is your budget for travelling?",
                "Let's talk about money... what's your budget for traveling?",
                "Let's talk about money... what's your budget to travel?",
                "Speaking of money... what's your travel budget?",
                "Let's talk about money... how much is your travel budget?",
                "Let's talk about cash... what's your travel budget?",
                "Let's talk about money... how much money do you have to travel?",
                "Now, let's talk about money... what's your travel budget?",
                "Speaking of money... what's your budget for traveling?",
                "A flight is not free, you know... How much do you have?"
            ]
            msg = (
                    f"{random.choice(ls_msg)}\n\n(example: 3.14€)"
                )
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(msg)
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.budget = step_context.result

        msg = (
            f"Please confirm :\n\n"
            f"Departure : { booking_details.origin }\n\n" 
            f"Destination : { booking_details.destination }\n\n"
            f"Starting on: { booking_details.start_date }\n\n"
            f"Ending on: { booking_details.end_date}\n\n"
            f"Budget: { booking_details.budget }."
        )
        
        prompt_options = PromptOptions(
            choices = [Choice("Yep"), Choice("Nope")],
            prompt = MessageFactory.text(msg)
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            # For some reason, boolean returned values are inverted once deployed on Azure
            # So I've made a custom prompt
            # ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg)) 
            ChoicePrompt.__name__, prompt_options
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        booking_details = step_context.options
        import sys
        print(step_context.result.value, file=sys.stdout)

        # Customer is happy
        if step_context.result.value == "Yep":
            self.logger.setLevel(logging.INFO)
            self.logger.info('Flight booked with success : the customer is satisfied')
            return await step_context.end_dialog(booking_details)

        # Customer is not happy
        properties = {'custom_dimensions': booking_details.__dict__}
        self.logger.setLevel(logging.ERROR)
        self.logger.error("The customer is not satisfied with the Bot's proposition", extra=properties)
        
        ls_apology_msg = [
            "I'm sure you said that because you're angry.... Let's try again",
            "I'm sure you said that because you're mad... let's try again",
            "I'm sure you said that because you're angry... let's try some more",
            "I'm sure you said that because you're angry... let's give it a try",
            "I bet you said that because you're angry... let's try again",
            "I'm sure you said that because you're angry... let's keep trying",
            "I'm sure you said that because you're upset... let's give it another shot",
            "I'm sure you said that because you're mad... let's give it another try",
            "Okay, calm down! Let's start again from the beginning"
        ]
        apology_msg = random.choice(ls_apology_msg)
        prompt_apology = MessageFactory.text(apology_msg, apology_msg, InputHints.ignoring_input)
        await step_context.context.send_activity(prompt_apology)
        
        # Track when user is unhappy with the bot
        self.telemetry_client.track_trace("Unhappy user", properties, "ERROR")

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
