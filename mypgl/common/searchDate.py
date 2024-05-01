class SearchDate:
    """
    検索日付のパーツ
    """

    def __init__(
        self,
        fromYearVar,
        fromYearMenu,
        fromMonthVar,
        fromMonthMenu,
        fromDateVar,
        fromDateMenu,
        toYearVar,
        toYearMenu,
        toMonthVar,
        toMonthMenu,
        toDateVar,
        toDateMenu,
    ):
        """
        Constructor
        """
        self.fromYearVar = fromYearVar
        self.fromYearMenu = fromYearMenu
        self.fromMonthVar = fromMonthVar
        self.fromMonthMenu = fromMonthMenu
        self.fromDateVar = fromDateVar
        self.fromDateMenu = fromDateMenu
        self.toYearVar = toYearVar
        self.toYearMenu = toYearMenu
        self.toMonthVar = toMonthVar
        self.toMonthMenu = toMonthMenu
        self.toDateVar = toDateVar
        self.toDateMenu = toDateMenu
