from db_writer import S7Db,S7DbDataDint,S7DbDataArray,S7DbDataBool,S7DbDataString

# create db 
db = S7Db("test_db")

# create Bool data
isActive = S7DbDataBool("is_active",True)

# create Dint Data
len = S7DbDataDint("length",100)
wit = S7DbDataDint("with",200)

# create String data
text = S7DbDataString("text","example string")

# create custom Dint array
arrayDint = S7DbDataArray("example_array_Dint",S7DbDataDint,[1,2,3,4,5,6,7,8])

# create custom Bool array
arrayBool = S7DbDataArray("example_array_Bool",S7DbDataBool,[True,False,False,True])

# add everything to db
db.addData(isActive)
db.addData(len)
db.addData(wit)
db.addData(text)
db.addData(text)
db.addData(arrayDint)
db.addData(arrayBool)

# write db to file
db.writeToFile("test_db")
    