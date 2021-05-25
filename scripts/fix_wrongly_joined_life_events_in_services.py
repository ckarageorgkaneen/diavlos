#!/usr/bin/env python3
from diavlos.src.site import Site
from diavlos.src.service import Service

WRONG_LIFE_EVENTS_MAP = {
    'Επαγγελματίες υγείαςΕλεύθεροι επαγγελματίες': 'Επαγγελματίες υγείας,Ελεύθεροι επαγγελματίες',
    'Κοινωνική αρωγήΔιαχείριση ακίνητης περιουσίας': 'Κοινωνική αρωγή,Διαχείριση ακίνητης περιουσίας',
    'ΑνεργίαΑποζημιώσεις και παροχές': 'Ανεργία,Αποζημιώσεις και παροχές',
    'Γεωργική επιχειρηματικότηταΓεωργία': 'Γεωργική επιχειρηματικότητα,Γεωργία',
    'ΚτηματογράφησηΕλεύθεροι επαγγελματίες': 'Κτηματογράφηση,Ελεύθεροι επαγγελματίες',
    'Φορολογία πολιτώνΦορολογία επιχειρήσεων': 'Φορολογία πολιτών,Φορολογία επιχειρήσεων',
    'Αδειοδοτήσεις και συμμόρφωσηΑδειοδοτήσεις και συμμόρφωση': 'Αδειοδοτήσεις και συμμόρφωση,Αδειοδοτήσεις και συμμόρφωση',
    'Αδειοδοτήσεις και συμμόρφωσηΓεωργία': 'Αδειοδοτήσεις και συμμόρφωση,Γεωργία',
    'ΑνεργίαΚατασκηνώσεις': 'Ανεργία,Κατασκηνώσεις',
    'ΑπώλειαΔικαστήρια': 'Απώλεια,Δικαστήρια',
    'ΓεωργίαΓεωργική επιχειρηματικότητα': 'Γεωργία,Γεωργική επιχειρηματικότητα',
    'Επαγγελματίες υγείαςΑναγνώριση επαγγελματικών προσόντων': 'Επαγγελματίες υγείας,Αναγνώριση επαγγελματικών προσόντων',
    'ΕπιδοτήσειςΗλεκτρονικός φάκελος επιχείρησης': 'Επιδοτήσεις,Ηλεκτρονικός φάκελος επιχείρησης',
    'Ιατροφαρμακευτική περίθαλψηΕπαγγελματίες υγείας': 'Ιατροφαρμακευτική περίθαλψη,Επαγγελματίες υγείας',
    'ΤηλεπικοινωνίεςΑδειοδοτήσεις και συμμόρφωση': 'Τηλεπικοινωνίες,Αδειοδοτήσεις και συμμόρφωση',
    'Άτομα με αναπηρίες και χρόνιες παθήσειςΑσφάλιση': 'Άτομα με αναπηρίες και χρόνιες παθήσεις,Ασφάλιση',
    'Αδειοδοτήσεις και συμμόρφωσηΕλεύθεροι επαγγελματίες': 'Αδειοδοτήσεις και συμμόρφωση,Ελεύθεροι επαγγελματίες',
    'Αδειοδοτήσεις και συμμόρφωσηΤηλεπικοινωνίες': 'Αδειοδοτήσεις και συμμόρφωση,Τηλεπικοινωνίες',
    'ΑνεργίαΕπιδόματα': 'Ανεργία,Επιδόματα',
    'ΑνεργίαΤουρισμός': 'Ανεργία,Τουρισμός',
    'Γεωργική επιχειρηματικότηταΤρόφιμα': 'Γεωργική επιχειρηματικότητα,Τρόφιμα',
    'Διαχείριση ακίνητης περιουσίαςΑκίνητη περιουσία επιχειρήσεων': 'Διαχείριση ακίνητης περιουσίας,Ακίνητη περιουσία επιχειρήσεων',
    'Ελεύθεροι επαγγελματίεςΑδειοδοτήσεις και συμμόρφωση': 'Ελεύθεροι επαγγελματίες,Αδειοδοτήσεις και συμμόρφωση',
    'ΕπιδόματαΦορολογία πολιτών': 'Επιδόματα,Φορολογία πολιτών',
    'Κατάρτιση και εκπαιδευτικό περιεχόμενοΕπαγγελματίες εκπαίδευσης': 'Κατάρτιση και εκπαιδευτικό περιεχόμενο,Επαγγελματίες εκπαίδευσης',
    'ΚτηνοτροφίαΑδειοδοτήσεις και συμμόρφωση': 'Κτηνοτροφία,Αδειοδοτήσεις και συμμόρφωση',
    'ΚτηνοτροφίαΓεωργία': 'Κτηνοτροφία,Γεωργία',
    'Νομοθεσία και αποφάσειςΝομοθεσία': 'Νομοθεσία και αποφάσεις,Νομοθεσία',
    'ΟχήματαΦορολογία επιχειρήσεων': 'Οχήματα,Φορολογία επιχειρήσεων',
    'Πανεπιστήμια και φοίτησηΕπιδόματα': 'Πανεπιστήμια και φοίτηση,Επιδόματα',
    'Φάκελος υγείαςΙατροφαρμακευτική περίθαλψη': 'Φάκελος υγείας,Ιατροφαρμακευτική περίθαλψη',
    'Φορολογία πολιτώνΈλεγχος εγκυρότητας φορολογικών στοιχείων': 'Φορολογία πολιτών,Έλεγχος εγκυρότητας φορολογικών στοιχείων',
    'Έλεγχος εγκυρότητας φορολογικών στοιχείωνΑκίνητη περιουσία επιχειρήσεων': 'Έλεγχος εγκυρότητας φορολογικών στοιχείων,Ακίνητη περιουσία επιχειρήσεων',
    'Έλεγχος εγκυρότητας φορολογικών στοιχείωνΦορολογία πολιτών': 'Έλεγχος εγκυρότητας φορολογικών στοιχείων,Φορολογία πολιτών',
    'Αδειοδοτήσεις και συμμόρφωσηΓεωργική επιχειρηματικότητα': 'Αδειοδοτήσεις και συμμόρφωση,Γεωργική επιχειρηματικότητα',
    'Αδειοδοτήσεις και συμμόρφωσηΚαταγγελίες': 'Αδειοδοτήσεις και συμμόρφωση,Καταγγελίες',
    'Αδειοδοτήσεις και συμμόρφωσηΚατασκηνώσεις': 'Αδειοδοτήσεις και συμμόρφωση,Κατασκηνώσεις',
    'Ακίνητη περιουσία επιχειρήσεωνΦορολογία επιχειρήσεων': 'Ακίνητη περιουσία επιχειρήσεων,Φορολογία επιχειρήσεων',
    'ΑνεργίαΆτομα με αναπηρίες και χρόνιες παθήσεις': 'Ανεργία,Άτομα με αναπηρίες και χρόνιες παθήσεις',
    'ΑνεργίαΚατάρτιση και εκπαιδευτικό περιεχόμενο': 'Ανεργία,Κατάρτιση και εκπαιδευτικό περιεχόμενο',
    'Απασχόληση προσωπικούΈναρξη και λύση επιχείρησης': 'Απασχόληση προσωπικού,Έναρξη και λύση επιχείρησης',
    'Απασχόληση στο δημόσιο τομέαΑνεργία': 'Απασχόληση στο δημόσιο τομέα,Ανεργία',
    'Απασχόληση στο δημόσιο τομέαΦορολογία πολιτών': 'Απασχόληση στο δημόσιο τομέα,Φορολογία πολιτών',
    'ΑπώλειαΣυνταξιοδότηση': 'Απώλεια,Συνταξιοδότηση',
    'Αρχαιολογικοί χώροι και πολιτιστική κληρονομιάΤουρισμός': 'Αρχαιολογικοί χώροι και πολιτιστική κληρονομιά,Τουρισμός',
    'ΑσφάλισηΙατροφαρμακευτική περίθαλψη': 'Ασφάλιση,Ιατροφαρμακευτική περίθαλψη',
    'ΓεωργίαΑδειοδοτήσεις και συμμόρφωση': 'Γεωργία,Αδειοδοτήσεις και συμμόρφωση',
    'ΓεωργίαΑλιεία': 'Γεωργία,Αλιεία',
    'ΓεωργίαΚτηνοτροφία': 'Γεωργία,Κτηνοτροφία',
    'Γεωργική επιχειρηματικότηταΣυνεταιρισμοί': 'Γεωργική επιχειρηματικότητα,Συνεταιρισμοί',
    'Γεωργική επιχειρηματικότηταΦορολογία επιχειρήσεων': 'Γεωργική επιχειρηματικότητα,Φορολογία επιχειρήσεων',
    'Δημόσια περιουσία και εθνικά κληροδοτήματα / κοινωφελείς περιουσίεςΑδειοδοτήσεις και συμμόρφωση': 'Δημόσια περιουσία και εθνικά κληροδοτήματα / κοινωφελείς περιουσίες,Αδειοδοτήσεις και συμμόρφωση',
    'Διαχείριση ακίνητης περιουσίαςΓεωργία': 'Διαχείριση ακίνητης περιουσίας,Γεωργία',
    'Διαχείριση ακίνητης περιουσίαςΠεριβάλλον και ποιότητα ζωής': 'Διαχείριση ακίνητης περιουσίας,Περιβάλλον και ποιότητα ζωής',
    'Διαχείριση ακίνητης περιουσίαςΦορολογία επιχειρήσεων': 'Διαχείριση ακίνητης περιουσίας,Φορολογία επιχειρήσεων',
    'Διαχείριση ακίνητης περιουσίαςΦορολογία πολιτών': 'Διαχείριση ακίνητης περιουσίας,Φορολογία πολιτών',
    'Διεύθυνση κατοικίας και επικοινωνίαςΚαταγγελίες': 'Διεύθυνση κατοικίας και επικοινωνίας,Καταγγελίες',
    'Εγγραφή σε σχολείοΠανεπιστήμια και φοίτηση': 'Εγγραφή σε σχολείο,Πανεπιστήμια και φοίτηση',
    'Εκδόσεις και πολιτιστικό περιεχόμενοΚατάρτιση και εκπαιδευτικό περιεχόμενο': 'Εκδόσεις και πολιτιστικό περιεχόμενο,Κατάρτιση και εκπαιδευτικό περιεχόμενο',
    'Ελεύθεροι επαγγελματίεςΑναγνώριση τίτλου σπουδών': 'Ελεύθεροι επαγγελματίες,Αναγνώριση τίτλου σπουδών',
    'Ενημέρωση και επικαιροποίηση στοιχείων πολίτηΑσφάλιση': 'Ενημέρωση και επικαιροποίηση στοιχείων πολίτη,Ασφάλιση',
    'Ενημέρωση και επικαιροποίηση στοιχείων πολίτηΕξ αποστάσεως εξυπηρέτηση πολιτών': 'Ενημέρωση και επικαιροποίηση στοιχείων πολίτη,Εξ αποστάσεως εξυπηρέτηση πολιτών',
    'Ενημέρωση και επικαιροποίηση στοιχείων πολίτηΠολίτες άλλων κρατών': 'Ενημέρωση και επικαιροποίηση στοιχείων πολίτη,Πολίτες άλλων κρατών',
    'Εξ αποστάσεως εξυπηρέτηση πολιτώνΑνεργία': 'Εξ αποστάσεως εξυπηρέτηση πολιτών,Ανεργία',
    'Επίσκεψη και νοσηλεία σε νοσοκομείοΙατροφαρμακευτική περίθαλψη': 'Επίσκεψη και νοσηλεία σε νοσοκομείο,Ιατροφαρμακευτική περίθαλψη',
    'Επαγγελματίες εκπαίδευσηςΑδειοδοτήσεις και συμμόρφωση': 'Επαγγελματίες εκπαίδευσης,Αδειοδοτήσεις και συμμόρφωση',
    'Επαγγελματίες υγείαςΑναγνώριση τίτλου σπουδών': 'Επαγγελματίες υγείας,Αναγνώριση τίτλου σπουδών',
    'Επαγγελματίες υγείαςΑπασχόληση στο δημόσιο τομέα': 'Επαγγελματίες υγείας,Απασχόληση στο δημόσιο τομέα',
    'Επαγγελματίες υγείαςΠανεπιστήμια και φοίτηση': 'Επαγγελματίες υγείας,Πανεπιστήμια και φοίτηση',
    'ΕπιδοτήσειςΕξ αποστάσεως εξυπηρέτηση πολιτών': 'Επιδοτήσεις,Εξ αποστάσεως εξυπηρέτηση πολιτών',
    'ΕπιδόματαΜετακινήσεις': 'Επιδόματα,Μετακινήσεις',
    'Ηλεκτρονικός φάκελος επιχείρησηςΜεταβολές': 'Ηλεκτρονικός φάκελος επιχείρησης,Μεταβολές',
    'Ηλεκτρονικός φάκελος επιχείρησηςΦορολογία επιχειρήσεων': 'Ηλεκτρονικός φάκελος επιχείρησης,Φορολογία επιχειρήσεων',
    'Κατάρτιση και εκπαιδευτικό περιεχόμενοΆτομα με αναπηρίες και χρόνιες παθήσεις': 'Κατάρτιση και εκπαιδευτικό περιεχόμενο,Άτομα με αναπηρίες και χρόνιες παθήσεις',
    'Κτηνοτροφική επιχειρηματικότηταΑδειοδοτήσεις και συμμόρφωση': 'Κτηνοτροφική επιχειρηματικότητα,Αδειοδοτήσεις και συμμόρφωση',
    'ΜετακινήσειςΆσκηση εκλογικού δικαιώματος': 'Μετακινήσεις,Άσκηση εκλογικού δικαιώματος',
    'ΜετακινήσειςΕπιδόματα': 'Μετακινήσεις,Επιδόματα',
    'Πανεπιστήμια και φοίτησηΕκπαιδευτικό βιογραφικό': 'Πανεπιστήμια και φοίτηση,Εκπαιδευτικό βιογραφικό',
    'Πανεπιστήμια και φοίτησηΚατάρτιση και εκπαιδευτικό περιεχόμενο': 'Πανεπιστήμια και φοίτηση,Κατάρτιση και εκπαιδευτικό περιεχόμενο',
    'Πανεπιστήμια και φοίτησηΜετακινήσεις': 'Πανεπιστήμια και φοίτηση,Μετακινήσεις',
    'Περιβάλλον και ποιότητα ζωήςΟχήματα': 'Περιβάλλον και ποιότητα ζωής,Οχήματα',
    'Περιβάλλον και ποιότητα ζωήςΤηλεπικοινωνίες': 'Περιβάλλον και ποιότητα ζωής,Τηλεπικοινωνίες',
    'Πολίτες άλλων κρατώνΑσφάλιση': 'Πολίτες άλλων κρατών,Ασφάλιση',
    'Πολίτες άλλων κρατώνΕκπαιδευτικό βιογραφικό': 'Πολίτες άλλων κρατών,Εκπαιδευτικό βιογραφικό',
    'Πολίτες άλλων κρατώνΕνημέρωση και επικαιροποίηση στοιχείων πολίτη': 'Πολίτες άλλων κρατών,Ενημέρωση και επικαιροποίηση στοιχείων πολίτη',
    'Πολίτες άλλων κρατώνΕξ αποστάσεως εξυπηρέτηση πολιτών': 'Πολίτες άλλων κρατών,Εξ αποστάσεως εξυπηρέτηση πολιτών',
    'Πολίτες άλλων κρατώνΤουρισμός': 'Πολίτες άλλων κρατών,Τουρισμός',
    'Τελωνειακές υπηρεσίεςΑδειοδοτήσεις και συμμόρφωση': 'Τελωνειακές υπηρεσίες,Αδειοδοτήσεις και συμμόρφωση',
    'ΤηλεπικοινωνίεςΤαχυδρομεία': 'Τηλεπικοινωνίες,Ταχυδρομεία',
    'ΤρόφιμαΓεωργία': 'Τρόφιμα,Γεωργία',
    'ΤρόφιμαΕπιδοτήσεις': 'Τρόφιμα,Επιδοτήσεις',
    'Φάκελος υγείαςΕπίσκεψη και νοσηλεία σε νοσοκομείο': 'Φάκελος υγείας,Επίσκεψη και νοσηλεία σε νοσοκομείο',
    'Φορολογία επιχειρήσεωνΑπασχόληση προσωπικού': 'Φορολογία επιχειρήσεων,Απασχόληση προσωπικού'}

site = Site()
site.login(auto=True)

for page in site.categories[Service.CATEGORY_NAME]:
    page_text = page.text()
    for wrong_le, correct_le in WRONG_LIFE_EVENTS_MAP.items():
        if wrong_le in page_text:
            page.edit(page_text.replace(wrong_le, correct_le))
            print(f'Fixed life events {wrong_le} for {page.page_title}')
            break
