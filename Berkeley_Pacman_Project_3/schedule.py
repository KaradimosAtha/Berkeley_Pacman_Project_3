from csp import*
import pandas as pd
import time


class Exam_timetabling(CSP):

    def __init__(self):
        lessons = pd.read_csv("h3-data.csv") #Διαβαζουμε το csv file  , μεσα την παρενθεση βαζουμε το ονομα του αρχειου που θα διαβασουμε , το οποιο πρεπει να βρισκεται στον τρεχον φακελο με το αρχειο schedule.py

        self.variables = []#Τις μεταβλητες τις αποθηκευω σε μια λιστα
        self.domains= {} #Τα domains ειναι ενα dictionary με κλειδι το ονομα τις μεταβλητης και σαν value μια λιστα με ολες τις δυνατες τιμες 
        self.neighbors = {}#Τα neighbors ειναι ενα dictionary με κλειδι το ονομα της μεταβλητης και σαν value μια λιστα με ολες τις μεταβλητες με τις οποιες εμπλεκεται σε περιορισμο

        #other_data = [teacher , semister , hard_lesson , Lab]
        self.other_data = {}#Στο dictionary other_data αποθηκευω για καθε μεταβλητη μια λιστα που περιεχει το ονομα του καθηγητη που διδασκει το μαθημα , το εξαμηνο στο οποιο διδασκεται  , εαν ειναι hard(True ή False) και εαν εχει Lab(True ή False)
        days = list(range(1 , 22))#Εχουμε μια μεταβλητη days που ειναι μια λιστα που περιεχει ολες τις μερες τις εξεταστικης(1 εως 21)
        time = ["9-12" , "12-3" , "3-6"]#Το time ειναι μια λιστα που περιεχει ολες τις δυνατες ωρες που μπορει να εξεταστει ενα μαθημα κατα την διαρκεια της ημερας

        self.num_of_constraint_checks = 0 #Εχουμε ενα counter που θα μετραει ποσες φορες μπηκαμε στην συναρτηση Exam_constraint. Αυτο το counter θα το χρησιμοποιησουμε σαν μετρο συγκρισης των αλγοριθμων(Περισσοτερη εξηγηση σχετικα με αυτο υπαρχει στο pdf file)

        #Οι μεταβλητες του προβληματος εχω επιλεξει να ειναι τα ονοματα των μαθηματων(εχουμε 38 μαθηματα , τα lab δεν τα μετραω σαν ξεχωριστω μαθημα)
        #Το domain καθε μεταβλητης ειναι μια λιστα που περιεχει ολους τους δυνατους συνδιασμους ημερας/ωρας που μπορει να εξεταστει το μαθημα . Καθε συνδιασμος ειναι ενα string της μορφης "day_hour" οπου day ειναι μια μερα απο το (1-21) και hour ειναι μια τιμη απο την λιστα time
        #Καθε μαθημα εχει σαν γειτονα ολα τα υπολοιπα , αφου εχουμε μονο μια αιθουσα και μπορουμε να εξετασουμε μονο 1 μαθημα καθε τρεις ωρες 
        for i in range(0 , len(lessons)): #Για καθε γραμμη του csv
            var = lessons.iloc[i,1] #Παιρνουμε το ονομα του μαθητος  
            semester_num = lessons.iloc[i , 0] #Τον αριθμο του εξαμηνου
            is_hard = lessons.iloc[i,3] #Εαν ειναι hard ή οχι 
            Lab = lessons.iloc[i , 4] #Εαν το μαθημα εχει Lab ή οχι 
            teacher = lessons.iloc[i,2] #Το ονομα του καθηγητη
            self.variables.append(var)#Προσθετουμε την μεταβλητη στο τελος της λιστας 
            self.other_data[var] = [teacher , semester_num , is_hard , Lab] #Αποθηκευουμε τις extra πληροφοριες της μεταβλητης 
            self.domains[var] = []  
            for day in days:
                for hour in time:
                    self.domains[var].append(str(day) + '_' + hour) #Δημιουργουμε ολους τους πιθανους συνδιασμους τιμων μερας/ωρας  και τους εισαγουμε στο domain της μεταβλητης var

        for i in range(0 , 38): #Για καθε μεταβλητη δημιουργουμε την γειτονια της 
            self.neighbors[self.variables[i]] = [] 
            for j in range(0 , 38):#Οπως ειπα και πιο πανω καθε μεταβλητη εχει σαν γειτονα ολες τις υπολοιπες 
                if self.variables[i] != self.variables[j]:
                    self.neighbors[self.variables[i]].append(self.variables[j])

        CSP.__init__(self , self.variables , self.domains , self.neighbors , self.Exam_constraints) #Καλουμε τον constructor του CSP με ορισματα τις μεταβλητες του προβληματος , τα domains , τους γειτονες και τελος την συναρτηση Exam_constraints

    def Exam_constraints(self ,A, a, B, b):#Συναρτηση Exam_constraints η οποια δεχεται δυο μεταβλητες A,B και δυο τιμες απο τα domains τους a , b αντιστοιχα και ελεγχει εαν πληρουνται ολοι οι περιορισμοι μεταξυ των δυο μεταβλητων για την συγκεκριμενη αναθεση τιμων.
        self.num_of_constraint_checks+=1#Οπως ειπα και πιο πανω θελουμε να μετραμε ποσες φορες μπηκαμε μεσα στης συναρτηση αυτη , αρα αυξανουμε τον counter num_of_constraint_checks κατα 1 

        splited_str = a.split("_") #Επειδη τα a και b ειναι strings της μορφης day_time κανουμε split το string για να παρουμε την μερα και την ωρα που εξεταζεται το μαθημα
        day_a = int(splited_str[0])#Μετατρεπουμε την μετα σε int
        time_a = splited_str[1] #Το time ειναι ενα απο τα string "9-12" , "12-3" , "3-6"

        splited_str = b.split("_")
        day_b = int(splited_str[0])
        time_b = splited_str[1] 

        a = self.other_data[A] #other_data = [teacher , semister , hard_lesson , Lab]
        b = self.other_data[B]
        

        if(day_a== day_b and time_a == time_b):#Εαν τα μαθηματα εξεταζονται την ιδια μερα και ωρα τοτε επιστρεφουμε false 
            return False

        if((a[1] == b[1]) and (day_a == day_b)): #Μαθηματα ιδιου εξαμηνου δεν πρεπει να εξεταζονται την ιδια μερα
            return False
        
        if(day_a == day_b and a[2] == True and b[2] == True): #Μαθηματα που ειναι hard δεν πρεπει να εξεταζονται την ιδια μερα 
            return False

        if(a[3] == True and time_a == "3-6"  or  b[3] == True and time_b == "3-6"): #Εαν καποιο απο τα δυο μαθηματα εχει Lab και το μαθημα εξεταζεται 3-6 τοτε επιστρεφουμε false γιατι δεν υπαρχει ωρα που να μπορει να εξεταστει το Lab αμεσος μετα
            return False
        
        if((day_a == day_b) and (a[3]== True or b[3] == True)):#Εαν η μερα του A και του Β ειναι ιδιες και ενα απο τα δυο ή και τα δυο εχουν εργαστηριο τοτε:
            if(a[3] == True and b[3] == True):#Εαν εχουν και τα δυο Lab την ιδια μερα τοτε επιστρεφουμε False γιατι εχουμε μονο τρεια slots και εχουμε 4 μαθηματα(2 + 2 LAB)
                return False
            if(a[3] == True):#Eαν το A ειναι εκεινο που εχει Lab
                if( (time_a == "9-12" and time_b == "12-3") or (time_a == "12-3" and time_b == "3-6") ):#Εαν το B εξεταζεται αμεσως μετα το A τοτε επιστρεφουμε False γιατι το Lab του A πρεπει να εξεταστει αμεσως μετα την εξεταση της θεωριας
                    return False
            else:#Εαν το B ειναι εκεινο που εχει Lab
                if((time_b == "9-12" and time_a == "12-3") or (time_b == "12-3" and time_a == "3-6") ):#Περνουμε τους ιδιους περιορισμους με πανω απλος αντι για time_a βαζουμε time_b και οπου time_b βαζουμε time_a
                    return False
            
        if (a[0] == b[0] and day_a == day_b):#Μαθηματα ιδιου καθηγητη δεν πρεπει να εξεταζονται την ιδια μερα
            return False
        if(a[2] == True and b[2] == True) and ( abs(day_a - day_b) <2) : #Τα δυσκολα μαθηματα πρεπει να απεχουν τουλαχιστον δυο μερες
            return False #Οποτε εαν και το Α και το B ειναι hard μαθηματα και η απολυτη τιμη της διαφορας των ημερων ειναι μικροτερη απο το 2 τοτε επιστρεφουμε False
        return True #Εαν δεν παραβιαστει κανενας απο τους παραπανω περιορισμους τοτε επιστρεφουμε True καθως με την  αναθεση της τιμης a στην μεταβλητη A και της τιμης b στην μεταβλητη B ικανοποιουνται ολοι οι περιορισμοι

    def Print_Result(self , result):#Συναρτηση Print_Result η οποια δεχεται μια σωστη αναθεση τιμων στις μεταβλητες του csp και τυπωνει το προγραμμα της εξεταστικης ξεκινωντας απο την ημερα 1
        if result == None:#Εαν το result ειναι None τοτε τυπωνουμε καταλληλο μυνημα καθως ο αλγοριθμος δεν βρηκε λυση 
            print("No result found")
        else:
            #Το result ειναι dictionary που περιεχει σαν κλειδι το ονομα του μαθηματος και σαν value μια τιμη απο το domain του που ικανοποιει ολους τους περιορισμους με τις υπολοιπες μεταβλητες.
            print("The Timetable is: ")
            print()
            for day in range(1 , 22):#Για καθε μερα
                for time in ["9-12" , "12-3" , "3-6"]:#Για καθε ωρα
                    for var in self.variables:#Περνουμε καθε μετραβλητη
                        str = result[var].split("_")#Κανουμε split το string για να παρουμε την μερα και την ωρα που εξεταζεται το μαθημα
                        day_of_var = int(str[0])
                        time_of_var = str[1]
                        if day_of_var == day and time_of_var == time: #Εαν η μερα που εξεταζεται αντιστοιχει στο day και η ωρα στο time τοτε τυπωνουμε καταλληλα μυνηματα
                            print(f"{var} | Day: {day_of_var}  Time: {time_of_var}")
                            print()
                            if self.other_data[var][3] == True:#Εαν το μαθημα εχει Lab
                                if time_of_var == "9-12":#Τοτε εαν η ωρα που εξεταζεται το μαθημα ειναι "9-12 " , το Lab θα εξεταστει στις "12-3"
                                    print(f"Lab  {var}  | Day: {day_of_var}  Time: 12-3")
                                else:#Αλλιως θα εξεταστει στις "3-6"
                                    print(f"Lab {var} | Day: {day_of_var}  Time: 3-6")
                                print()    


#ΒΓΑΛΤΕ ΑΠΟ ΣΧΟΛΙΟ ΤΟΝ ΑΝΤΟΙΣΤΙΧΟ ΑΛΓΟΡΙΘΜΟ ΠΟΥ ΕΠΙΘΥΜΕΙΤΕ ΝΑ ΤΡΕΞΕΤΕ ΓΙΑ ΝΑ ΔΕΙΤΕ ΤΟ ΑΠΟΤΕΛΕΣΜΑ ΤΟΥ ΠΡΟΓΡΑΜΜΑΤΟΣ 
#Ο ΑΛΓΟΡΙΘΜΟΣ DOM/WDEG ΕΧΕΙ ΥΛΟΠΟΙΗΘΕΙ ΣΤΟ ΑΡΧΕΙΟ CSP.py

if __name__ == '__main__': #Main

    z = Exam_timetabling()

    start = time.time() #Μετραμε τον χρονο που χρειαζεται για να ολοκληρωθει το προβλημα 
    
    result = backtracking_search(z , mrv ,  inference=forward_checking) #BACKTRACKING + MRV + FC 
    
    #result = backtracking_search(z , dom_wdeg ,  inference=forward_checking) #BACKTRACKING + DOM/WDEG + FC

    #result = backtracking_search(z , mrv , inference=mac) #BACKTRACKING + MRV + MAC  

    #result = backtracking_search(z , dom_wdeg , inference=mac) #BACKTRACKING + DOM/WDEG + MAC 

    #result = min_conflicts(z) # MIN_CONFLICTS

    end = time.time()

    z.Print_Result(result) #Τυπωνουμε το προγραμμα

    print(f'Total time: {end-start}') #Τυπωνουμε τον συνολικο χρονο εκτελεσης του BT ή του MIN CONFLICTS
    print()
    print(f'Number of Assignments : {z.nassigns}') #Τυπωνουμε ποσα assignments εγιναν σε μεταλβητες
    print()
    print(f'Number of Constraint Checks: {z.num_of_constraint_checks}') #Τυπωνουμε ποσες φορες μπηκαμε στην constraint function
