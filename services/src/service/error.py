from services.src.helper.error import ErrorCode
from services.src.helper.error import Error


class ServiceErrorCode(ErrorCode):
    UNAUTHORIZED_ACTION = 1
    FETCH_ALL = 2
    NOT_FOUND = 3
    ALREADY_EXISTS = 4
    REQUIRED_UPDATE_KEYS = 5
    NO_FIELD_UPDATED = 6
    FIELDS_NOT_PROPER = 7
    SITE_API_ERROR = 8


_ERROR_ARGS = [
    (ServiceErrorCode.UNAUTHORIZED_ACTION,
     'Ο χρήστης δεν έχει επαρκή δικαίωματα.',
     403),
    (ServiceErrorCode.FETCH_ALL,
     'Πρόβλημα κατά τη φόρτωση των διαδικασιών.',
     404),
    (ServiceErrorCode.NOT_FOUND,
     'Η διαδικασία δε βρέθηκε.',
     200),
    (ServiceErrorCode.ALREADY_EXISTS,
     'Η διαδικασία υπάρχει ήδη.',
     409),
    (ServiceErrorCode.REQUIRED_UPDATE_KEYS,
     'Υποχρεωτικά κλειδιά: name, fields.',
     404),
    (ServiceErrorCode.NO_FIELD_UPDATED,
     'Δεν ενημερώθηκε κανένα πεδίο.',
     404),
    (ServiceErrorCode.FIELDS_NOT_PROPER,
     'To κλειδί fields πρέπει να περιέχει dictionary.',
     404),
    (ServiceErrorCode.SITE_API_ERROR,
     'Παρουσιάστηκε σφάλμα διεπαφής με τη σελίδα.',
     500
     )
]

ServiceError = Error()
ServiceError.add_many(_ERROR_ARGS)
