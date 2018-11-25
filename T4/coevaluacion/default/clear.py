import os

'''
Function that erase all the content of the database and create the migrations again.
Run this file from terminal (not manage.py shell) while you are on ./T4 folder, run:

python3 coevaluacion/default/clear.py


'''


# reset the data base
def erase_database():
    if os.path.exists("./coevaluacion/migrations/"):
        os.system('rm -r ./coevaluacion/migrations/*')
    if os.path.exists("./db.sqlite3"):
        os.system('rm ./db.sqlite3')
    os.system('python3 manage.py makemigrations coevaluacion')
    os.system('python3 manage.py migrate')


erase_database()