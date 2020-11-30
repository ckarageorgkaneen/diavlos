from services.src.helper.error import ErrorCode
from services.src.helper.error import Error


class eParavoloErrorCode(ErrorCode):
    NOT_FOUND = 1


eParavoloError = Error()
eParavoloError.add(eParavoloErrorCode.NOT_FOUND,
                   'Δεν βρέθηκαν αποτελέσματα.',
                   200)
