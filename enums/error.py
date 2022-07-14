class ScannerErrorType:
    INVALID_INPUT = "Invalid input"
    INVALID_NUMBER = "Invalid number"
    UNCLOSED_COMMENT = "Unclosed comment"
    UNMATCHED_COMMENT = "Unmatched comment"

class SemanticErrorType:
    SCOPING = "SCOPING"
    BREAK_STMT = "BREAK_STMT"
    CONT_STMT = "CONT_STMT"
    MISMATCH_PARAM_FUNC = "MISMATCH_PARAM_FUNC"
    MAIN_FUNC_DEF = "MAIN_FUNC_DEF"
    TYPE_MISMATCH = "TYPE_MISMATCH"
