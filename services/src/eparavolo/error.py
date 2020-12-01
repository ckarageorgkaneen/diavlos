from services.src.helper.error import ErrorCode
from services.src.helper.error import ErrorData


class eParavoloErrorCode(ErrorCode):
    NOT_FOUND = 1


eParavoloErrorData = ErrorData()
eParavoloErrorData.add(eParavoloErrorCode.NOT_FOUND,
                       'Δεν βρέθηκαν αποτελέσματα.',
                       200)
