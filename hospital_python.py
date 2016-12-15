import sqlite3
import sys
from terminaltables import AsciiTable


DB_NAME = "hospital.db"

class DataBaseConnection:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)

    def list_all_patients(self):
        c = self.db.cursor()
        query = """SELECT * FROM patients"""
        c.execute(query)
        patients = c.fetchall()
        patients.insert(0, ("Id","Firstname", "Lastname", "Age", "Gender", "DrID"))
        table = AsciiTable(patients)
        print(table.table)

    def list_all_doctors_in_the_hospital(self):
        c = self.db.cursor()
        query = """ SELECT * FROM doctors"""
        c.execute(query)
        doctors = c.fetchall()
        doctors.insert(0, ("Id", "Firstname", "Lastname"))
        table = AsciiTable(doctors)
        print(table.table)

    def add_new_patient(self, firstname, lastname, age, gender, doctor_id):
        c = self.db.cursor()
        query = """INSERT INTO PATIENTS (FIRSTNAME, LASTNAME, AGE, GENDER, DOCTOR)
                 VALUES (?, ?, ?, ?, ?)"""
        c.execute(query, (firstname, lastname, age, gender, doctor_id))
        self.db.commit()

    def add_new_doctor(self, firstname, lastname):
        c = self.db.cursor()
        query = """INSERT INTO DOCTORS (FIRSTNAME, LASTNAME)
                 VALUES (?, ?)"""
        c.execute(query, (firstname, lastname))
        self.db.commit()


    def update_patient_information(self, patient_id, firstname=None, lastname=None,
                                   age=None, gender=None, doctor_id=None):
        c = self.db.cursor()
        update_columns = ""
        if firstname:
            update_columns += """FIRSTNAME = "{0}", """.format(firstname)
        if lastname:
            update_columns += """LASTNAME = "{0}", """.format(lastname)
        if age:
            update_columns += """AGE = {0}, """.format(age)
        if gender:
            update_columns += """GENDER = "{0}", """.format(gender)
        if doctor_id:
            update_columns += """doctor = {0}, """.format(doctor_id)
        update_columns = update_columns[:-2]
        query = """UPDATE patients
                     SET """ + update_columns + """ WHERE ID = {0}""".format(patient_id)
        c.execute(query)
        self.db.commit()

    def update_doctors_information(self, dr_id, firstname=None, lastname=None):
        c = self.db.cursor()
        update_columns = ""
        if firstname:
            update_columns += """FIRSTNAME = "{0}", """.format(firstname)
        if lastname:
            update_columns += """LASTNAME = "{0}", """.format(lastname)
        update_columns = update_columns[:-2]
        query = """UPDATE doctors
                     SET """ + update_columns + """ WHERE ID = {0}""".format(dr_id)
        print(query)
        c.execute(query)
        self.db.commit()

    def update_hospitals_information(self, stay_id, room=None, startdate=None, \
                                     enddate=None, injury=None, patient=None):
        c = self.db.cursor()
        update_columns = ""
        if room:
            update_columns += """ROOM = {0}, """.format(room)
        if startdate:
            update_columns += """STARTDATE = "{0}", """.format(startdate)
        if enddate:
            update_columns += """ENDDATE = "{0}", """.format(enddate)
        if injury:
            update_columns += """INJURY = "{0}", """.format(injury)
        if patient:
            update_columns += """PATIENT = {0}, """.format(patient)
        update_columns = update_columns[:-2]
        query = """UPDATE hospital_stay
                     SET """ + update_columns + """ WHERE ID = {0}""".format(stay_id)
        c.execute(query)
        self.db.commit()

    def delete_patient(self, patient_id):
        c = self.db.cursor()
        query = """DELETE FROM PATIENTS WHERE ID = ?"""
        c.execute(query, (patient_id,))
        self.db.commit()

    def delete_doctor(self, dr_id):
        query = """DELETE FROM DOCTORS WHERE ID = ?"""
        c.execute(query, (dr_id,))
        db.commit()

    def delete_hospital_stay(self, stay_id):
        c = self.db.cursor()
        query = """DELETE FROM HOSPITAL_STAY WHERE ID = ?"""
        c.execute(query, (stay_id,))
        self.db.commit()

    def list_all_patients_of_a_doctor(self, dr_id):
        c = self.db.cursor()
        name_query = """SELECT firstname, lastname FROM DOCTORS WHERE ID = ?"""
        c.execute(name_query, (dr_id,))
        dr_name = c.fetchone()

        patients_query = """SELECT
                    GROUP_CONCAT(firstname ||  " " || lastname)
                    FROM PATIENTS
                    WHERE DOCTOR = ?
                    GROUP BY DOCTOR"""
        c.execute(patients_query, (dr_id,))
        drs_patients = c.fetchone()[0].split(",")

        dr_and_patients = [p.split(" ") for p in drs_patients]
        dr_and_patients.insert(0, ["Dr. " + dr_name[0], dr_name[1] + "'s patients:"])
        table = AsciiTable(dr_and_patients)
        print(table.table)


    def all_sick_patients_group_by_their_sicknesses(self, injury):
        c = self.db.cursor()
        query = """SELECT INJURY,
                    GROUP_CONCAT ((SELECT firstname || " " || lastname
                                    FROM patients
                                    WHERE id=PATIENT)) AS patients
                    FROM hospital_stay
                    WHERE INJURY = ?
                    GROUP BY INJURY"""
        c.execute(query, (injury,))
        grouped_patients = c.fetchall()
        table_title = grouped_patients[0][0] + ":"
        table_content = (grouped_patients[0][1]).split(",")
        table_content = [r.split(" ") for r in table_content]

        table = AsciiTable(table_content)
        table.inner_heading_row_border = False
        table.title = table_title
        print(table.table)


    def list_all_doctors_and_the_diseases_they_treat(self):
        c = self.db.cursor()
        query = """SELECT FIRSTNAME, LASTNAME,
                    GROUP_CONCAT(INJURY)
                    FROM (SELECT DOCTORS.ID AS DOCTOR, DOCTORS.FIRSTNAME,
                                    DOCTORS.LASTNAME, HOSPITAL_STAY.INJURY
                          FROM PATIENTS , DOCTORS, HOSPITAL_STAY
                          WHERE HOSPITAL_STAY.PATIENT = PATIENTS.ID AND
                                    PATIENTS.DOCTOR = DOCTORS.ID)
                    GROUP BY DOCTOR"""
        c.execute(query)
        drs_and_diseases = c.fetchall()

        table = AsciiTable(drs_and_diseases)
        table.inner_heading_row_border = False
        table.title = "Doctors and the deseases they treat:"
        print(table.table)

    def show_all_patients_in_period(self, startdate, enddate):
        c = self.db.cursor()
        query = """SELECT *
                    FROM HOSPITAL_STAY
                    WHERE startdate >= ? AND enddate <= ?"""
        c.execute(query, (startdate, enddate))
        all_patients = c.fetchall()
        all_patients.insert(0, ["Id", "Room", "Startdate", "Enddate", "Diagnose", "Dr_Id"])

        table = AsciiTable(all_patients)
        print(table.table)


def main():
    console_args = sys.argv[1::]
    dbconn = DataBaseConnection(DB_NAME)
    if console_args[0] == "list_patients":
        dbconn.list_all_patients()
    if console_args[0] == "add_patient":
        dbconn.add_new_patient(*console_args[1::])
    if console_args[0] == "delete_patient":
        dbconn.delete_patient(*console_args[1::])
    dbconn.db.close()

if __name__ == "__main__":
    main()

