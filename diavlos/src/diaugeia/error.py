from diavlos.src.helper.error import ErrorCode
from diavlos.src.helper.error import ErrorData


class DiaugeiaErrorCode(ErrorCode):
    NOT_FOUND = 1


DiaugeiaErrorData = ErrorData()
DiaugeiaErrorData.add(DiaugeiaErrorCode.NOT_FOUND,
                      'Δεν βρέθηκε ο αριθμός διαδικτυακής ανάρτησης',
                      200)
