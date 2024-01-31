from enum import Enum
from abc import ABCMeta, abstractmethod

class S7DbDataType(Enum):

    """contains valid datatypes supported by this library"""

    Bool        = "Bool"
    DInt        = "DInt"
    String      = "String"
    Array       = "Array"
    Custom      = "Custom"

class S7DbData(metaclass = ABCMeta):

    """Baseclass for S7Datatypes"""

    name:str
    type:S7DbDataType
    identifier:str

    @abstractmethod
    def initVariables(self) -> str:
        pass

class S7DbDataDint(S7DbData):

    """S7 DInt Datatype"""

    name:str
    type = S7DbDataType.DInt
    value:int
    identifier:str
    
    def __init__(self,name:str,value:int):
        self.name = name
        self.value = value
        self.identifier = '"{}" : {}'.format(self.name,self.type.name)
    
    def initVariables(self) -> str:
        return '   "{}" := {};\n'.format(self.name,self.value)

class S7DbDataBool(S7DbData):

    """S7 Bool Datatype"""

    name:str
    type = S7DbDataType.Bool
    value:bool
    identifier:str
    
    def __init__(self,name:str,value:bool):
        self.name = name
        self.value = value
        self.identifier = '"{}" : {}'.format(self.name,self.type.name)

    def initVariables(self) -> str:
        if self.value:
            return "   {} := true;\n".format(self.name)
        else:
            return "   {} := false;\n".format(self.name)

class S7DbDataString(S7DbData):

    """S7 String Datatype"""

    name:str
    type = S7DbDataType.String
    value:str
    identifier:str
    
    def __init__(self,name:str,value:str):
        self.name = name
        self.value = value
        self.identifier = '"{}" : {}'.format(self.name,self.type.name)

    def initVariables(self) -> str:
        return "   {} := '{}'\n".format(self.name,self.value)

class S7DbDataArray(S7DbData):

    """S7 Array Datatype"""

    supported=[S7DbDataType.DInt,S7DbDataType.Bool]
    type = S7DbDataType.Array
    name:str
    arrayType:S7DbDataType
    array : dict
    length : list
    startOffset:int
    identifier:str
    dimensions:int
    
    def __init__(self,name:str,dataType:S7DbDataType,values:list=[],length:int=0,startOffset:int=0) -> None:
        
        """takes a name of an array together with its elements type and elements\n
        if no values are given the db will declare an empty array with "length" number of elements.\n
        startOffset is used if the array should not start with index "0" """
        
        self.name = name
        self.length = []

        if dataType not in self.supported:
            print("'{}' not a supported type -> choose from ({})".format(dataType,self.supported))
            exit()
        
        self.arrayType = dataType
        
        if len(values) != 0:
            self.array = {}
            for i in range(0,len(values)):
                self.array[i] = values[i]
            self.length.append(len(values))
        else:
            self.length.append(length)
            self.array = {}
        
        self.startOffset = startOffset
        

        # generating list of length of nested lists
        self.length = []
        temp = values
        while type(temp) is list:
            self.length.append(len(temp))
            temp = temp[0]
        self.dimensions = len(self.length)
        

        # checking for multi dimensional array
        if self.dimensions > 1:
            
            # building the used identifier
            self.identifier = '"{}" : Array['.format(self.name)
            self.identifier+= "{}..{}".format(self.startOffset,self.startOffset+self.length[0]-1)
            for e in range(1,len(self.length)):
                self.identifier += ", "
                self.identifier += "{}..{}".format(0,self.length[e]-1)
            self.identifier+="] of {}".format(self.arrayType.name)
        else:
            self.identifier = '"{}" : Array[{}..{}] of {}'.format(self.name,self.startOffset,self.length[0]-1+self.startOffset,self.arrayType.name)

    def initVariables(self) -> str:
    
        variables= ""
        if self.arrayType == S7DbDataType.Bool:
            
            for i in range(0,len(self.array)):
                if self.array[i]:
                    variables+='   "{}"[{}] := true;\n'.format(self.name,i)
                else:
                    variables+='   "{}"[{}] := false;\n'.format(self.name,i)
            return variables

        elif self.arrayType == S7DbDataType.DInt:
            if self.dimensions == 1:
                for i in range(0,len(self.array)):
                    variables+='   "{}"[{}] := {};\n'.format(self.name,i,self.array[i])
                return variables
            
            variables = ""
            
            # recursively flatten list for easy enumeration
            flat_list = []
            for value in self.array.values():
                flat_list.append(value)
            while type(flat_list[0]) is list:
                flat_list = [num for sublist in flat_list for num in sublist]
            
            # progress tracker for every array dimension
            progress = []
            for e in self.length:
                progress.append(0)

            # looping over every data entry
            for i in range(0,len(flat_list)):

                # generating variable declaration for every data entry ("test_array[0,0] := 10") 
                variables += '   "{}"[{}'.format(self.name,progress[0])
                for h in range(1,len(self.length)):
                    variables += ",{}".format(progress[h])
                variables += "] :={};\n".format(flat_list[i])
                
                # incrementing progress tracker
                for j in range(len(self.length)-1,-1,-1):                    
                    if progress[j] < self.length[j]-1:
                        progress[j] += 1
                        break
                    else:
                        progress[j] = 0

            return variables
            


        print("{} not implemented".format(self.arrayType))
        return ""

class S7Db():

    """S7 DB like object containing the data which to write to the db file later"""

    supported = [S7DbDataType.Array,S7DbDataType.Bool,S7DbDataType.DInt,S7DbDataType.String,S7DbDataType.Custom]
    name : str
    optimizedAccess : bool
    readOnly:bool
    accessibleFromOPC:bool
    data:list[S7DbData]
    
    typeMapping = {"dint":"DInt"}
    
    def __init__(self,name:str,optimizedAccess:bool=True,unlinked:bool=False,readonly:bool=False,accessibbleFromOPC:bool=True) -> None:
        self.name = name
        self.optimizedAccess = optimizedAccess
        self.unlinked = unlinked
        self.readOnly = readonly
        self.accessibleFromOPC = accessibbleFromOPC
        self.data = []
    
    def __generateHeader__(self) -> str:
        header = 'DATA_BLOCK "{}"\n'.format(self.name)
        header+="{"
        if not self.accessibleFromOPC:
            header += " DB_Accessible_From_OPC_UA := 'FALSE' ;\n"
        
        if self.optimizedAccess:
            header+=" S7_Optimized_Access := 'TRUE' }\n"
        else:
            header+=" S7_Optimized_Access := 'FALSE' }\n"
    
        header+= "VERSION : 0.1\n"
        
        if self.unlinked:
            header+="UNLINKED\n"
        
        if self.readOnly:
            header+="READ_ONLY\n"
        
        return header
    
    def __generateVariables__(self) -> str:
        variables = "NON_RETAIN\n"
        variables+="   VAR\n"
        for var in self.data:
            variables+="      " + var.identifier +";\n"
        variables += "   END_VAR\n\n\n"
        return variables

    def __initVariables__(self) -> str:
        variables = "BEGIN\n"
        for var in self.data:
            variables += var.initVariables()
        variables += "END_DATA_BLOCK\n"
        return variables

    def addData(self,data:S7DbData) -> None:
        if data.type not in self.supported:
            print("'{}' not a supported type -> choose from ({})".format(data.type,self.supported))
        self.data.append(data)
    
    def writeToFile(self,filename:str="") -> bool:
        if filename == "":
            filename = "{}.db".format(self.name)
        with open(filename,"w") as f:
            f.write(self.__generateHeader__())
            f.write(self.__generateVariables__())
            f.write(self.__initVariables__())
        return True
