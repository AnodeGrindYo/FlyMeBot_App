"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog

from config import DefaultConfig
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

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
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
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

        if booking_details.origin is None:
            msg = (
                    # f"{type(step_context)}\n\n"
                    # f"{step_context.values}\n\n"
                    f"What is your departure city ?\n\n"
                    # f"DEBUG:"
                    # f"Departure city : { booking_details.origin }\n\n" 
                    # f"Destination : { booking_details.destination }\n\n"
                    # f"Starting on: { booking_details.start_date }, ending on: { booking_details.end_date}\n\n"
                    # f"Budget: { booking_details.budget }."
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

        if booking_details.destination is None:
            msg = (
                    f"What is your destination city ?\n\n"
                    # f"DEBUG:"
                    # f"Departure city : { booking_details.origin }\n\n" 
                    # f"Destination : { booking_details.destination }\n\n"
                    # f"Starting on: { booking_details.start_date }, ending on: { booking_details.end_date}\n\n"
                    # f"Budget: { booking_details.budget }."
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

        if booking_details.budget is None:
            msg = (
                    f"Let's talk about money... What is your budget for travelling?\n\n"
                    # f"DEBUG:"
                    # f"Departure city : { booking_details.origin }\n\n" 
                    # f"Destination : { booking_details.destination }\n\n"
                    # f"Starting on: { booking_details.start_date }, ending on: { booking_details.end_date}\n\n"
                    # f"Budget: { booking_details.budget }."
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
            # f"Departure city : { booking_details.origin }\n\n" 
            # f"Destination : { booking_details.destination }\n\n"
            # f"Starting on: { booking_details.start_date }, ending on: { booking_details.end_date}\n\n"
            # f"Budget: { booking_details.budget }."
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        booking_details = step_context.options
        
        if step_context.result:
            self.logger.setLevel(logging.INFO)
            self.logger.info('Flight booked, customer satisfied')
            return await step_context.end_dialog(booking_details)

        properties = {'custom_dimensions': booking_details.__dict__}
        
        self.logger.setLevel(logging.ERROR)
        self.logger.error('Customer is not satisfied with the Bot\'s proposition', extra=properties)

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
