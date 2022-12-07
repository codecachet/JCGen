#!/usr/bin/env python3

from tinydb import TinyDB, Query, where

dbname = "test.db"

class MyDB:

    """
    two tables:
    1. image (default)
    2. iserver 
    """

    table_table = {
        'image' : None,
        'iserver' : None,
    }

    def __init__(self, db_path):
        self.db = TinyDB(db_path)
        self.create_tables()
    
    def create_tables(self):
        for table in MyDB.table_table:
            MyDB.table_table[table] = self.db.table(table)
        print("table_table=", MyDB.table_table)


        # self.t_image = self.db.table('image')
        # self.t_iserver = self.db.table('iserver')

        # print(f'name = {self.t_image.name}')

        # print(f'tables={self.db.tables()}')

        self.db.default_table_name = 'image'

    def get_table(self, table_name):
        return MyDB.table_table[table_name]
    
    def clear_all(self):
        tables = self.show_tables()
        for tablename in tables:
            table = self.db.table(tablename)
            table.truncate()
        

    def show_tables(self):
        print(f'tables={self.db.tables()}')
        return self.db.tables()



# def test1():
#     db = MyDb("test.db")
#     db.create_tables()


#     ts = db.show_tables()
#     print('ts =', ts)
# def test2():
#     db = TinyDB('test.db')
#     tab1 = db.table('image')
#     print(f'table name={tab1.name}')
#     print("tables=", db.tables())

#     tab1.insert({'val1': 'hi'})

# def test3():
#     db = MyDb('test.db')
#     db.create_tables()
#     for i in range(50):
#         db.db.insert({'val2': 'hi'})
# def test4():
#     db = MyDb(dbname)
#     tab1 = db.db.table('iserver')
#     for i in range(50):
#         tab1.insert({'val3': 'hi'})

# def test5():
#     db = MyDb(dbname)
#     db.set_current_table('image')

#     for i in range(50):
#         db.insert({'val4': 'hi'})

#     db.set_current_table('iserver')

#     for i in range(50):
#         db.insert({'val5': 'hi'})


# def test6():
#     db = MyDb(dbname)
#     db.set_current_table('image')
#     db.clear()

# def test7():
#     db = MyDb(dbname)
#     db.set_current_table('image')
    
# def test8():
#     db = MyDb(dbname)
#     db.clear_all()

# def test9():
#     db = MyDb(dbname)
#     db.set_current_table('image')
#     for i in range(50):
#         db.insert({'val5': i})

# def test10():
#     db = MyDb(dbname)

#     t_image = db.get_table('image')

#     t_image.truncate()

#     for i in range(50):
#         t_image.insert({'val5': i})

# def test11():
#     db = MyDb(dbname)

#     t_image = db.get_table('image')

#     Q = Query()
#     val = t_image.search(Q.val5 == 4)
#     print('val=', val)

# def query1():
#     db = MyDb(dbname)
#     #db.create_tables()
#     all = db.get_all()
#     print("all=", all)
#     all = db.get_all('image')
#     print(f'all={all}')
#     all = db.get_all('iserver')
#     print(f'all={all}')
# def query2():
#     db = MyDb(dbname)
#     Q = Query()

#     val = db.db.search(Q.val5 == 7)
#     print("val =", val)
#     val = val[0]
#     val['val5'] = 258

#     val = db.db.search(Q.val5 == 7)
#     print("val =", val)

# def query3():
#     db = MyDb(dbname)
#     Q = Query()
#     val = db.db.search(Q.val5 == 258)
#     print("val =", val)

# def query4():
#     db = MyDb(dbname)
#     image_t = db.get_table('image')
#     iserver_t = db.get_table('iserver')

#     Q = Query()
#     val = image_t.search(Q.val5 == 4)
#     print('val=', val)
#     valx = val[0]
#     valx['val6'] = 127

#     print('valx=', valx)

# def query5():
#     db = MyDb(dbname)
#     image_t = db.get_table('image')

#     all = image_t.all()
#     print('all=', all)
# def update1():
#     db = MyDb(dbname)
#     image_t = db.get_table('image')
#     iserver_t = db.get_table('iserver')

#     Q = Query()
#     val = image_t.update({'val7': 300, 'val5': 10000}, Q.val5 == 4)

if __name__ == "__main__":
    #test1()
    #test2()
    #test3()
    #test9()
    #query1()
    #query2()

    #test10()
    #query4()
    
    #test11()
    #query4()


    query5()
    update1()
    query5()