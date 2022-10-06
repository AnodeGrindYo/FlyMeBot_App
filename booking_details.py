class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        start_date: str = None,
        end_date: str = None,
        budget: int = None

    ):
        self.destination = destination
        self.origin = origin
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
