from usecasesmarker.spreadsheet_controller_for_checker import ISpreadsheetControllerForChecker

class SpreadSheetFactoryForChecker:

    ##@brief Creates and returns an object of a class that implements the methods specified within
    # ISpreadsheetControllerForChecker (this emulates an interface for encapsulating your particular implementation of
    # a controller, and that includes only the methods required for marking your project features). This method
    # must create the framework of objects that allow that, once finalized its execution,
    # everything is ready for invoking the methods of the object implementing the methods specified within
    # ISpreadsheetControllerForChecker and starting setting contents in the spreadsheet cells and start checking results
    # and marking your code
    # @return an object of a class that implements the methods specified within ISpreadsheetControllerForChecker.

    def create_spreadsheet_controller() -> ISpreadsheetControllerForChecker:
        return ISpreadsheetControllerForChecker()