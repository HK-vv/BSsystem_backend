class SubmitWrongProblemError(RuntimeError):
    def __init__(self, *args):
        self.args = args


class ContestFinishedError(RuntimeError):
    def __init__(self, *args):
        self.args = args
