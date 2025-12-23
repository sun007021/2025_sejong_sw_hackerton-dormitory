class StudentNotFoundException(Exception):
    """Exception raised when student is not found."""

    def __init__(self, student_id: str):
        self.student_id = student_id
        self.message = f"Student with ID '{student_id}' not found"
        super().__init__(self.message)


class StudentAlreadyExistsException(Exception):
    """Exception raised when student already exists."""

    def __init__(self, student_id: str):
        self.student_id = student_id
        self.message = f"Student with ID '{student_id}' already exists"
        super().__init__(self.message)


class InvalidStudentDataException(Exception):
    """Exception raised when student data is invalid."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)