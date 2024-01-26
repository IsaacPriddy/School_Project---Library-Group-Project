
import queries as q

student = q.TeacherSqlCommands()

print(student.fetch_all_ids())


"""
user_db = {
    "admin": "password"
}

teacher_db = {
    "admin": "password"
}

idList = db.StudentSqlCommands().fetch_all_ids()
tidList = db.TeacherSqlCommands().fetch_all_ids()

for item in idList:
    user_db[str(item)] = "password"
for item in tidList:
    teacher_db[str(item)] = "password"



def fetch_all_ids(self):
        #return all student IDs
         p_query = self.conn.execute("SELECT Student_ID FROM Students")

         temp = p_query.fetchall()

         for i in range(len(temp)):
            temp[i] = temp[i][0]
         
         return temp
   """