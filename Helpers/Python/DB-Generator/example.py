from db_writer import S7Db,S7DbDataType,S7DbDataDint,S7DbDataArray,S7DbDataBool,S7DbDataString

# create db 
db = S7Db("test_db")

# create Bool data
isActive = S7DbDataBool("is_active",True)

# create Dint Data
len = S7DbDataDint("length",100)

# create String data
text = S7DbDataString("text","example string")

# create custom Dint array
arrayDint = S7DbDataArray("example_array_Dint",S7DbDataType.DInt,[1,2,3,4,5,6,7,8])

# create custom Bool array
arrayBool = S7DbDataArray("example_array_Bool",S7DbDataType.Bool,[True,False,False,True])

# create custom multidimensional array [in theory this should support n dimensional arrays but is only tested up to n=3]
arrayMultidimensional = S7DbDataArray("example_array_multidimensional",S7DbDataType.DInt,[[10,10],[2,2],[1,250]])

# add everything to db
db.addData(isActive)
db.addData(len)
db.addData(text)
db.addData(text)
db.addData(arrayDint)
db.addData(arrayBool)
db.addData(arrayMultidimensional)

# write db to file
db.writeToFile("test_db.db")
    