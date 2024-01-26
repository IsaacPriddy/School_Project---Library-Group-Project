"""
Interface for connecting to books database.
.Net Ninjas - 3/12/2021
Ellie Bruhns, Yifeng Cui, Cameron Jordal, Isaac Priddy, Nick Titzler
"""
import sqlite3
import pandas as pd
from os import path

# location of saved database
DB_LOC = "db/database.sql"
# folder containing all database data tables as excel spreadsheets, only required if db doesn't exist
DB_DATA_LOC = "db/tables/"


# TODO: Fix the teacher add function so that when it adds the teacher_id it actually adds their last name (not number)
# TODO: The above problem is in the return classes/books and should start by looking there

def create_connection():
    # Purpose of this is to try and connect to the db, if it fails tell us
    conn = None
    try:
        conn = sqlite3.connect(DB_LOC)
    except sqlite3.Error as e:
        print(e)
    return conn


class GeneralUse:
    # TODO: Check here, if we need general use queries we can put them here. We can also not have id in other classes
    #   set to none.
    def __init__(self):
        # Needs to connect to the db after making sure it exists
        CheckDB()
        self.conn = create_connection()  # Connect to the database

    def fetch_all_student_ids(self):
        # return all student IDs
        p_query = self.conn.execute("SELECT Student_ID FROM Students")

        temp = p_query.fetchall()

        for i in range(len(temp)):
            temp[i] = temp[i][0]

        return temp

    def fetch_all_teacher_ids(self):
        # return all teacher IDs
        p_query = self.conn.execute("SELECT Teacher_ID FROM Teachers")

        temp = p_query.fetchall()

        for i in range(len(temp)):
            temp[i] = temp[i][0]

        return temp

    def fetch_all_books(self):
        # Fetch each book from Books
        book_pointer = self.conn.execute("SELECT * FROM Books")

        book_list = []
        for book in book_pointer:
            book_list.append(book)

        return book_list


class CheckDB:  # This will check if a DB exists, if not it will create it
    def __init__(self):
        # Check if database exists, if not create it to hold the information from csv's
        self.import_csv()

    @staticmethod
    def import_csv():  # csv filename
        # Connect to the DB  (ie do nothing) if  it exists, if it doesn't create it
        if path.exists(DB_LOC):
            return
        else:
            conn = create_connection()
            # These are the things everyone pulls from
            # Add Books to the db
            books = pd.read_excel(DB_DATA_LOC + "Books.xlsx")
            books.to_sql("Books", conn, if_exists="append", index=False)
            # Add Classes to the db
            classes = pd.read_excel(DB_DATA_LOC + "Classes.xlsx")
            classes.to_sql("Classes", conn, if_exists="append", index=False)

            # These are our user classes
            # Add Students to the db
            students = pd.read_excel(DB_DATA_LOC + "Students.xlsx")
            students.to_sql("Students", conn, if_exists="append", index=False)
            # Add Teachers to the db
            teachers = pd.read_excel(DB_DATA_LOC + "Teachers.xlsx")
            teachers.to_sql("Teachers", conn, if_exists="append", index=False)

            # These are our 'Bridges'
            # Add Books_X_Classes to the db
            bxc = pd.read_excel(DB_DATA_LOC + "Books X Class Bridge.xlsx")
            bxc.to_sql("Books_X_Classes", conn, if_exists="append", index=False)
            # Add Students_X_Classes to the db
            sxc = pd.read_excel(DB_DATA_LOC + "Students X CRN.xlsx")
            sxc.to_sql("Student_X_Classes", conn, if_exists="append", index=False)
            # Add Teachers_X_Classes to the db
            txc = pd.read_excel(DB_DATA_LOC + "Teachers x CRN.xlsx")
            txc.to_sql("Teachers_X_Classes", conn, if_exists="append", index=False)


class StudentSqlCommands:
    def __init__(self, my_id):
        # Needs to connect to the db after making sure it exists
        CheckDB()
        self.conn = create_connection()  # Connect to the database
        self.cur = self.conn.cursor()  # Make a pointer to the database that we will use to execute
        self.student_id = my_id

    def select_student(self):
        # Fetch all the rows from the students table
        p_query = self.conn.execute("SELECT * FROM Students WHERE Student_ID=?", (self.student_id,))

        # If we just used p_query we would get nothing, by doing fetchone() we have our cursor return what the above did
        temp = p_query.fetchone()
        # for row in p_query:
        #     temp = row[1]
        return temp

    def return_classes(self):
        # Fetch each class ID first from student_x_classes
        first_query = self.conn.execute("SELECT * FROM Student_X_Classes WHERE Student_ID=?", (self.student_id,))

        # Create a list of the CRN's that link to that student id of above
        class_crn_list = []
        for i in first_query:
            class_crn_list.append(i[0])  # Each iteration will add the whole list (STUDENT_ID/CRN) when I only want CRN

        # Compare that list of CRN's to the class library and pull each of the classes a student is taking
        full_class_list = []
        for val in class_crn_list:
            # val is not the 1,2,3... like normal, if we want that we enumerate(thing)
            second_query = self.conn.execute("SELECT * FROM Classes WHERE CRN=?", (val,))
            temp = second_query.fetchall()
            full_class_list.append(temp)
        return full_class_list

    def return_books(self, crn):
        # Fetch each ISBN first from Books_X_Classes, must loop to find all the books for each crn
        first_query = self.conn.execute("SELECT * FROM Books_X_Classes WHERE CRN=?", (crn,))

        # Create a list of the ISBN's that link to that query above
        book_isbn_list = []
        for i in first_query:
            book_isbn_list.append(i[1])

        # Create a list of Books that link to the list given above
        full_book_list = []
        for isbn in book_isbn_list:
            second_query = self.conn.execute("SELECT * FROM Books WHERE ISBN=?", (isbn,))
            temp = second_query.fetchall()
            full_book_list.append(temp)

        return full_book_list


class TeacherSqlCommands:
    def __init__(self, my_id):
        # Just like student, needs to connect to the db after making sure it exists
        CheckDB()
        self.conn = create_connection()  # Connect to the database
        self.teacher_id = my_id
        # self.Last_name  # At this point I want it to = the functions that find the user in teachers and assign last name

    def select_teacher(self):
        # Fetch all the rows from the students table
        p_query = self.conn.execute("SELECT * FROM Teachers WHERE Teacher_ID=?", (self.teacher_id,))
        temp = p_query.fetchone()
        return temp

    def return_classes(self):
        # Fetch each class ID first from teacher_x_classes
        first_query = self.conn.execute("SELECT * FROM Teachers_X_Classes WHERE Teacher_ID=?", (self.teacher_id,))

        # Create a list of the CRN's that link to that teacher id of above
        class_crn_list = []
        for i in first_query:
            class_crn_list.append(i[0])  # Each iteration will add the whole list (TEACHER_ID/CRN) when I only want CRN

        # Compare that list of CRN's to the class library and pull each of the classes a student is taking
        full_class_list = []
        for val in class_crn_list:
            # val is not the 1,2,3... like normal, if we want that we enumerate(thing)
            second_query = self.conn.execute("SELECT * FROM Classes WHERE CRN=?", (val,))
            temp = second_query.fetchall()
            full_class_list.append(temp)
        return full_class_list

    def return_books(self, crn):
        # Fetch each ISBN first from Books_X_Classes, must loop to find all the books for each crn
        first_query = self.conn.execute("SELECT * FROM Books_X_Classes WHERE CRN=?", (crn,))

        # Create a list of the ISBN's that link to that query above
        book_isbn_list = []
        for i in first_query:
            book_isbn_list.append(i[1])

        # Create a list of Books that link to the list given above
        full_book_list = []
        for isbn in book_isbn_list:
            second_query = self.conn.execute("SELECT * FROM Books WHERE ISBN=?", (isbn,))
            temp = second_query.fetchall()
            full_book_list.append(temp)

        return full_book_list

    # The above function (return_classes) is mostly a copy/paste so will need some checking and work done
    # The normal functions like select_teacher/find_classes/find_books will be here
    # The reason being that the teachers will still see a list of their classes they are teaching and the books they
    #   are requiring.

    def add_class(self, crn, subject, course_number, class_name, class_start):
        # Check if the class already exists
        checking_classes_query = self.conn.execute("SELECT * FROM Classes WHERE CRN=?", (crn,))
        classes_result = checking_classes_query.fetchone()
        checking_bridge_query = self.conn.execute("SELECT * FROM Teachers_X_Classes WHERE CRN=? AND Teacher_ID=?",
                                                  (crn, self.teacher_id))
        bridge_result = checking_bridge_query.fetchone()

        # Now add to each table the stuff IF it doesn't exist
        if classes_result is None:
            # We want to add a class to the Classes table
            first_query = "INSERT INTO Classes VALUES (?, ?, ?, ?, ?, ?)"
            self.conn.execute(first_query, (crn, subject, course_number, class_name, self.teacher_id, class_start))
            self.conn.commit()
        if bridge_result is None:
            # Must update our bridge when we add or remove anything
            second_query = "INSERT INTO Teachers_X_Classes VALUES (?, ?)"
            self.conn.execute(second_query, (crn, self.teacher_id))
            self.conn.commit()

        # temp = self.conn.execute("SELECT * FROM Classes")
        # print(*temp.fetchall(), sep='\n')

    def remove_class(self, crn):
        # Check if the class already exists
        checking_classes_query = self.conn.execute("SELECT * FROM Classes WHERE CRN=?", (crn,))
        classes_result = checking_classes_query.fetchone()
        checking_bridge_query = self.conn.execute("SELECT * FROM Teachers_X_Classes WHERE CRN=? AND Teacher_ID=?",
                                                  (crn, self.teacher_id))
        bridge_result = checking_bridge_query.fetchone()

        # Now delete the class if it is there
        if classes_result is not None:
            self.conn.execute("DELETE FROM Classes WHERE CRN=?", (crn,))
            self.conn.commit()
        if bridge_result is not None:
            self.conn.execute("DELETE FROM Teachers_X_Classes WHERE CRN=?", (crn,))
            self.conn.commit()

        # temp = self.conn.execute("SELECT * FROM Classes")
        # print(*temp.fetchall(), sep='\n')

    def add_book(self, crn, ISBN):
        # Check if the Book already exists in the class_X_books
        book_on_list = self.conn.execute("SELECT * FROM Books_X_Classes WHERE CRN=? AND ISBN=?", (crn, ISBN))
        book_result = book_on_list.fetchone()

        # Now add to each table the stuff IF it doesn't exist
        if book_result is None:
            # We want to add a class to the Classes table
            first_query = "INSERT INTO Books_X_Classes VALUES (?, ?)"
            self.conn.execute(first_query, (crn, ISBN))
            self.conn.commit()
        else:
            print("That book is already assigned to the class.")

        # temp = self.conn.execute("SELECT * FROM Classes")
        # print(*temp.fetchall(), sep='\n')

    def remove_book(self, crn, ISBN):
        # Check if the Book already exists in the class_X_books
        book_on_list = self.conn.execute("SELECT * FROM Books_X_Classes WHERE CRN=? AND ISBN=?", (crn, ISBN))
        book_result = book_on_list.fetchone()

        # Now add to each table the stuff IF it doesn't exist
        if book_result is not None:
            # We want to add a class to the Classes table
            first_query = "DELETE FROM Books_X_Classes WHERE CRN=? AND ISBN=?"
            self.conn.execute(first_query, (crn, ISBN))
            self.conn.commit()
        else:
            print("That book is not currently assigned to the class.")

        # temp = self.conn.execute("SELECT * FROM Classes")
        # print(*temp.fetchall(), sep='\n')


def main():
    # More testing may be required but it looks like it successfully add/removes classes
    '''
    teacher = TeacherSqlCommands(879498654)
    print(*teacher.return_classes(), sep='\n')  # The current classes a teacher is teaching before adding one
    # print(*teacher.return_books(39342), sep='\n')   # The current books required for the crn class being taken
    '''

    # This section is for testing add/remove class (TEACHER)
    '''
    teacher.add_class(21624, 'CIS', 422, 'Software Method 1', 1215)  # Needs 5 values
    print("-----------------------------------------------------------------------")
    print("Removing a class: ")
    teacher.remove_class(21624)
    print(*teacher.return_classes(), sep='\n')  # The current classes a teacher is teaching after removing one
    print("-----------------------------------------------------------------------")
    '''

    # This section is for add/remove books (TEACHER)
    '''
    crn = 39342
    print("The following are all the books required for CRN", crn, ": ")
    print(*teacher.return_books(crn), sep='\n')
    print("-----------------------------------------------------------------------")
    print("After adding another book to the class we get the following: ")
    teacher.add_book(39342, 9781337696609)
    print(*teacher.return_books(crn), sep='\n')
    print("-----------------------------------------------------------------------")
    print("After removing a book to the class we get the following: ")
    teacher.remove_book(39342, 9781337696609)
    print(*teacher.return_books(crn), sep='\n')
    '''

    # Commenting out this block so I can test teachers
    '''
    student = StudentSqlCommands(932266549)
    newTemp = student.select_student()
    print("The students name is: ", newTemp[1], newTemp[2])
    # Added the * at the front, and sep='\n' to print each entry on a new line
    print(newTemp[1], "is taking the following courses: ")
    print(*student.return_classes(), sep='\n')
    class_list = student.find_classes()

    book_list = []
    for i in class_list:
        book_list.append(student.return_books(i[0][0]))
    # print(*book_list, sep='\n')
    '''

    # List of commands likely needed from each user class
    '''
    Student commands
        select student (used elsewhere in student commands. Student ID should be const
        return classes
        return books (loop through each class returned by return classes, print all books for said class)
        read book (takes ISBN, make sure it is available, read it)
            May need to be done on the front end
        
    Teacher commands
        select teacher
        return classes
        return books
        read book
        add/remove class (takes in crn, adds/removes from teacherXclasses the crn and teacher ID)
        add/remove books (takes in isbn, adds/removes from classXbooks the crn and ISBN)
        
    Admin commands (May not implement)
        select admin
        add/remove teacher
        add/remove book
        add/remove classes
        add/remove student
    
    '''


if __name__ == "__main__":
    main()
