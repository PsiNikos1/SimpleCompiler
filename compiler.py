#IOANNIS KARAGEORGOS,AM 4071, cs04071
#NIKOLAOS PSILODIMITRAKOPOYLOS, AM 4202, cs04202

import string
import sys

letterCounter = 0  # to count in a specific line,the position in that line.
c = 0
#----Tools i need to create Cfile-----
linesForCfile=[]
functionFlag=True
lineCounter = 0
#----------------

#---tools for symbol table-------
scopeList=[]
nestingLevel=0
#--------------

#----------tools for assembly----------
quadScope=0
#---------------

tokens=[]
declaredVariables=[]
quadList=[]#list of lists,every list is a quad included their number ID.
T_i=0
tempVariables=[]
listBackPatch=[]
numQuad=0
#----------------------------------------------

def lexer():
    token=[]
    list=[]
    str = ""
    char = ""

    currState = 0

    # open file given as second argument in command line.
    try:
        file = open(sys.argv[1], "r")  # only for reading.
        print("File opened")

    except FileNotFoundError:  # if file is not found.
        print('File not found')
        exit(-1)
        return -1

    #

    # reading file char by char and change curr state
    str=file.read(1)
    while (str != "."):


        if(str==" " or str=="\n" or str=="\t"):#if character is space or newLine or tab just skip it.

            str=file.read(1)
            continue
        elif str.isalpha()==True:#if first character is A-Z or a-z.

            while(str.isalnum()==1):#and you keep finding alnum.
                list.append(str)#add it to token.
                str=file.read(1)#read next char.
            token.append("".join(list))#make the elements of the array a string.
            list=[]#empty the list.
        elif(str.isnumeric()==True):#if you find number as a first character.

            while(str.isnumeric()==True):#while you keep finding numbers.
                list.append(str)#add them to the list
                str=file.read(1)#read next char.
            token.append("".join(list))#add token
            list=[]#empty the list.
        else:

            list.append(str)
            str=file.read(1)
            token.append("".join(list))
            list=[]

    token.append(".")#add dot for EOF.

    str=file.read(1)

    if(str.isalnum()==False):
        return token
    else:
        print("Error,found character after the EOF")
        exit(-1)

        return -1



#----------------------------------------------

def synt():
    lineNum = 1


    boundedWords = [['program'], ['declare'], ['if'], ['else'], ['while'], ['switchcase'],
                    ['forcase'], ['incase'], ['case'], ['default'], ['not'], ['and'],
                    ['or',], ['function'], ['procedure'], ['call'], ['return'], ['in'],
                    ['inout'], ['input'], ['print' ]]

    ID=[]
    funtionsNames=[]

    ADD_OP=["+","-"]
    MUL_OP=["*", "/"]
    REL_OP = ["<", ">", "=", "<=", ">=", "<>"]




    def program(position):
        counter=position
        if (tokens[counter] != "program"):  # the word program MUST always be the first token,if not return -1 and prints error message.
           print("Error,every Cimple program must begin with the keyword 'program'! ")
           exit(-1)
           return -1
        else:
            counter+=1
            ID.append([tokens[counter]])  # add programName to bounded words.

            scope0=Scope(nestingLevel,8)
            scopeList.append(scope0)

            counter+=1#points to '{'.
            if(checkIfClosed(tokens)==-1):
                print("Error,some brackets are not closed")
                exit(-1)
            genQuad("begin_block",tokens[position+1],"_","_,")
            flag=1
            while (tokens[counter] != "." ):

                if(tokens[counter-1]=="}" and tokens[counter+1]=="."):
                    break
                counter = block(counter)




            genQuad("halt","_","_","_",)
            genQuad("end_block",tokens[position+1],"_","_")


            if (functionFlag):
                createCfile()

            for i in quadList:
                print(i,"\n")

    def block(position):#points to { in tokens.
        counter=position+1
        brackets=1
        if(tokens[position+1]=="."):

            return -1
        while( True):#create blockList.

            if(tokens[counter]=="{"):
                brackets+=1
                counter+=1

            elif(tokens[counter]=="}"):
                brackets-=1
                if(brackets==0):
                    break
                else:
                    counter += 1
            else:

                ret=statements(counter)
                counter=ret

        return counter

    def statements(position):

        if (tokens[position] == "declare"):
             return declaration(position)#this retutns points to ;

        if(tokens[position]=="function" or tokens[position]=="procedure"):
            return subprogram(position)

        elif (tokens[position] == "=" and tokens[position - 1] == ":"):
            ret=assingStat(position)

            return ret

        if (tokens[position] == "if"):
             return ifStat(position)
        elif (tokens[position] == "while"):
            return  whileStat(position)
        elif (tokens[position] == "switchcase"):
            return switchcaseStat(position)
        elif (tokens[position] == "forcase"):
            return forcaseStat(position)
        elif (tokens[position] == "incase"):
            return incaseStat(position)
        elif (tokens[position] == "call"):
            return callStat(position)
        elif (tokens[position] == "return"):
            return returnStat(position)
        elif (tokens[position] == "input"):
            return inputStat(position)
        elif (tokens[position] == "print"):
            return printStat(position)
        elif(tokens[position]== "else"):#maybe does not used.
            return elsepart(position)
        elif(tokens[position]=="#"):
            return comments(position)

        else:
            return position+1

    def declaration(position):#position points to 'declare'.
        global nestingLevel,scopeList
        c = position
        state1=1#final state.
        state2=2
        currstate=1

        if(tokens[c]=="declare" and tokens[c+1].isalnum()):
            c+=1


            while(tokens[c]!=";"):#until you find ;

                if(currstate==1):
                    if(tokens[c][0].isnumeric()):
                        exit(-1)
                        return -1
                    elif( tokens[c].isalnum() and  tokens[c+1]==","  ):
                        declaredVariables.append(tokens[c])

                        entity = Entity()
                       # scopeList[-1].setOffset()
                        variableEntity = entity.Variable(tokens[c],"int",scopeList[-1].getOffset(),nestingLevel)
                        scopeList[-1].addEntity(variableEntity)


                        currstate=1
                        c+=1

                    elif(tokens[c].isalnum() and tokens[c+1]==";"):
                        declaredVariables.append(tokens[c])
                        entity = Entity()
                       # scopeList[-1].setOffset()
                        variableEntity = entity.Variable(tokens[c], "int", scopeList[-1].getOffset(),nestingLevel)
                        scopeList[-1].addEntity(variableEntity)


                        return  c+1#points to ; at the end of declare.
                    elif (tokens[c] == "," and tokens[c+1].isalnum() ):
                        c+=1
                        continue
                    elif(tokens[c]=="," and tokens[c+1]==";"):
                        exit(-1)
                        return -1

        else:
            exit(-1)
            return -1


        return c

    def checkIfClosed(tokens):#this funtion checks if a { or [ or ( closes.
        position=0#keeps the position is token[].
        parenthesesCounter=0#counts these ( ).
        curlyBracketCounter=0# counts these {  }.
        squareBracketsCounter=0 #counts these [ ]

        while(tokens[position]!="."):#If you find ( { [ raise each counter by 1.If you find ) } ] reduce each counter by 1
            #When while ends,if all counters are equal to zero we are good to go,else return -1.
            position += 1

            if(tokens[position]=="("):
                parenthesesCounter+=1
                #position+=1
            elif(tokens[position]==")"):
                parenthesesCounter-=1
                #position += 1
            elif(tokens[position]=="{"):
                curlyBracketCounter+=1
                #position += 1
            elif(tokens[position]=="}"):
                curlyBracketCounter-=1
               # position += 1
            elif(tokens[position]=="["):
                squareBracketsCounter+=1
                #position += 1
            elif(tokens[position]=="]"):
                squareBracketsCounter-=1
               # position += 1

        if(parenthesesCounter==0 and squareBracketsCounter==0 and curlyBracketCounter==0):
            return 0
        else:
            return -1

    def subprogram(position):#position points to 'funtion' or 'procedure'.
        global nestingLevel
        global functionFlag
        counter=position
        formalparlist=[]
        ret=None
        #function.
        if(tokens[position]=="function"):
            functionFlag=True
            if(tokens[position+1][0].isnumeric()):#if function's ID starts with num,return -1
                print("invalid function name")
                exit(-1)
                return -1#error
            else:
                counter+=1
                funtionsNames.append(tokens[counter])#add funtion's ID to bounded words




                if(tokens[counter+1]!="("):#if the token after function's ID is not ' ( '.
                    print("after ID '(' expected")
                    exit(-1)
                    return -1 #error
                else:
                    counter+=1#this counter points to ' ( '.
                    while(tokens[counter] !=")"  ):#after this while loop counter points to ).
                        #  reading until you find ')'.
                        formalparlist.append(tokens[counter])
                        counter+=1
                    curlybracketPos=counter+1
                    formalparlist.remove("(")  # remove '(' from the list.Our formal par list is something like ['in' ,'x' , ',' , 'inout' , ' y' etc).
                counter+=1#points to {

                genQuad("begin_block",funtionsNames[-1],"_","_" )  # create block

                # Create scope .
                nestingLevel+=1
                scope=Scope(nestingLevel,8)
                scopeList.append(scope)

                #Create new function entity.
                entity=Entity()
                functionEntity=entity.Function(funtionsNames[-1],"int",nextquad(),0,nestingLevel)#i dont care about  argument & framelength cause it will change in addEntity.
                #Addint entity to scope.
                scopeList[-2].addEntity(functionEntity)

                formalparitem=[]
                formalparlist.append(",")
                tempList=[]
                for i in formalparlist:#create formalparitem list
                    if(i == ","):
                        formalparitem.append(tempList)
                        tempList=[]
                    else:
                        tempList.append(i)

                for i in range(0, len(formalparitem)):
                    if (len(formalparitem[i]) == 0):
                        formalparitem.remove(formalparitem[i])


                #------CHECKING IF FORMALPARLIST IS CORRECT-----------

                idState=0#in this state we have the ID of the parameter.We expect to see in or inout.
                inoutState=1#in this state we have the IN or INOUT.We expect to see ID next.
                currstate=0

                for i in range(0,len(formalparitem)):
                    if(formalparitem[i][0]!="in" and formalparitem[i][0]!="inout"):
                        print("Error in funtion's parameters, \"",formalparitem[i][0],"\"")
                        exit(-1)
                        return -1
                    elif( len(formalparitem[i])==1):
                        print("Error after \"",formalparitem[i][0],"\",expected variable")
                        exit(-1)
                        return -1

                    else:#every parameter starts with in or inout.
                        currstate=1

                        """if(formalparitem[i][1] not in declaredVariables):
                            print("Error in funtion's parameter,variable \"",formalparitem[i][1],"\" not declared.")
                            exit(-1)
                            return -1"""
                # -----END OF CHECKING---------------------

                #After checking if parameter list is valid,we produce the entities

                for i in range(0,len(formalparitem)):
                    if(formalparitem[i][0] == "in"):
                        ent=Entity()
                        inpar=ent.Parameter(formalparitem[i][1],"cv",0,nestingLevel)#Create Parameter Entity.
                        scopeList[-1].addEntity(inpar)#Add Parameter Entity to scope.
                        argument=Argument("cv","int",nestingLevel) #Create Argument
                        functionEntity.addArguments(argument) #Add Argument Entity to function entity.
                    elif(formalparitem[i][0] == "inout"):
                        ent = Entity()
                        inoutpar = ent.Parameter(formalparitem[i][1], "ref", 0,nestingLevel)
                        scopeList[-1].addEntity(inoutpar)
                        argument = Argument("ref", "int",nestingLevel)  # Create Argument.
                        functionEntity.addArguments(argument)  # Add Argument Entity to function entity.



            #Next we will check if function's block is correct.

            hasReturn=True
            bracketcounter=0
            ret=block(counter)
            genQuad("halt", "_", "_", "_")
            genQuad("end_block", funtionsNames[-1], "_", "_")

            writeToSymbolTableFile()
            #Delete scope after the end of function
            del scope
           # scopeList.pop(-1)
            nestingLevel-=1 #decreasin nesting level

            #Checking if function has return.
            while(True):
                if(tokens[curlybracketPos]=="}"):
                    bracketcounter-=1
                if(tokens[curlybracketPos] == "{"):
                    bracketcounter += 1
                if(tokens[curlybracketPos]=="return"):
                    hasReturn=True
                    break
                else:
                    hasReturn=False
                if (bracketcounter == 0):
                    break
                curlybracketPos+=1

            if(hasReturn==False):
                print("return expected in function")
                exit(-1)
                return -1

            return ret

        #procedure

        if (tokens[position] == "procedure"):
            if (tokens[position + 1][0].isnumeric()):  # if function's ID starts with num,return -1
                print("invalid procedure name")
                exit(-1)
                return -1
            else:
                functionFlag = True
                counter += 1
                funtionsNames.append(tokens[counter])  # add funtion's ID to bounded word

                if (tokens[counter + 1] != "("):  # if the token after function's ID is not ' ( '.
                    print("after procedure ID '(' expected")
                    exit(-1)
                    return -1  # error
                else:
                    counter += 1  # this counter points to ' ( '.
                    while (tokens[counter] != ")"):  # keep reading until you find ')'.
                        formalparlist.append(tokens[counter])
                        counter += 1

                formalparlist.remove( "(")  # remove '(' from the list.Our formal par list is something like ['in' ,'x' , ',' , 'inout' , ' y' etc).
                formalparlist.append(")")

                formalparitem = []
                counter+=1

                tempList = []
                for i in formalparlist:  # create formalparitem list
                    if (i == ","):
                        formalparitem.append(tempList)
                        tempList = []
                    else:
                        tempList.append(i)

                for i in range(0,len(formalparitem)):
                    if(len(formalparitem[i])==0):
                        formalparitem.remove(formalparitem[i])


                ########CHECKING IF FORMALPARLIST IS CORRECT######

                idState = 0  # in this state we have the ID of the paramete.We expect to see in or inout.
                inoutState = 1  # in this state we have the IN or INOUT.We expect to see ID next.
                currstate = 0

                for i in range(0, len(formalparitem)):
                    if (formalparitem[i][0] != "in" and formalparitem[i][0] != "inout"):
                        print("Error in funtion's parameters, \"", formalparitem[i][0], "\"")
                        exit(-1)
                        return -1
                    elif (len(formalparitem[i]) == 1):
                        print("Error after \"", formalparitem[i][0], "\",expected variable")
                        exit(-1)
                        return -1

                    else:  # every parameter starts with in or inout.
                        currstate = 1

                        """if (formalparitem[i][1] not in declaredVariables):
                            print("Error in funtion's parameter,variable \"", formalparitem[i][1], "\" not declared.")
                            exit(-1)
                            return -1"""
                formalparlist.pop(-1)
                ####END OF CHECKING#######


            genQuad("begin_block", funtionsNames[-1], "_", "_")

            #Create scope and add it to scope list.
            nestingLevel+=1
            scope=Scope(nestingLevel,8)
            scopeList.append(scope)

            #Create Procedure Entity and add it to scope.
            ent=Entity()
            procEntity=ent.Function(funtionsNames[-1],"int",nextquad(),0,nestingLevel)#I dont care about frameLength,its gonna change ahen we add entity to scope.
            scopeList[-2].addEntity(procEntity)


            ret=block(counter)
            # After checking if parameter list is valid,we produce the entities
            for i in range(0, len(formalparlist)):
                if (formalparlist[i] == "in"):
                    ent = Entity()
                    inpar = ent.Parameter(formalparlist[i][1], "cv", 0,nestingLevel)  # Create Parameter Entity.
                    scopeList[-1].addEntity(inpar)  # Add Parameter Entity to scope.
                    argument = Argument("cv", "int",nestingLevel)  # Create Argument
                    procEntity.addArguments(argument)  # Add Argument Entity to function entity.
                elif (formalparlist[i] == "inout"):
                    ent = Entity()
                    inoutpar = ent.Parameter(formalparlist[i][1], "ref", 0,nestingLevel)
                    scopeList[-1].addEntity(inoutpar)
                    argument = Argument("ref", "int",nestingLevel)  # Create Argument.
                    procEntity.addArguments(argument)  # Add Argument Entity to function entity.
            genQuad("halt", "_", "_", "_")
            genQuad("end_block", funtionsNames[-1], "_", "_")

        writeToSymbolTableFile()
        # Delete scope object and pop it out of scope list
        del scope
        #scopeList.pop(-1)
        nestingLevel-=1

        return ret

    def assingStat(position):#position points to :=.
        global funtionsNames
        c=position+1
        expressionList=[]
        list=[]

        while(tokens[c]!=";"):
            expressionList.append(tokens[c])

            c+=1
        eof=c
        ret=expression([expressionList])


        if(ret!=-1):#assign has correct expression

            if(len(expressionList)==1):#we have something like that x:=0.
                if(expressionList[0] in declaredVariables or expressionList[0].isnumeric()==True):
                    genQuad(":=",expressionList[0],"_",tokens[position-2])
                else:
                    print("Error when trying to  assign a value in '"+str(expressionList[0])+"' ,it is not declared.")
                    exit(-1)
            else:
                expressionList.append(";")
                c=0
                while(expressionList[c]!=";"):#this whuile calculates the MULOP operations first

                    if(expressionList[c] in MUL_OP):
                        t=newTemp()
                        genQuad(expressionList[c],expressionList[c-1],expressionList[c+1],t)
                        line = "L_" + str(nextLineInCfile()) + ": " + t + " = " + str(expressionList[c - 1]) + str(
                        expressionList[c]) + str(expressionList[c + 1])+"; //"+str(quadList[-1])
                        linesForCfile.append(line)
                        expressionList[c-1]=t
                        expressionList.pop(c)
                        expressionList.pop(c)
                        c-=1
                    else:
                        c+=1
                c=0
                while (expressionList[c] != ";"):  # this while calculates the MULOP operations first.

                    if (expressionList[c] in ADD_OP):
                        t = newTemp()
                        genQuad(expressionList[c], expressionList[c - 1], expressionList[c + 1], t)
                        line="L_"+str(nextLineInCfile())+": "+ t +" = " + str(expressionList[c-1])+str(expressionList[c])+str(expressionList[c+1])+"; //"+str(quadList[-1])
                        linesForCfile.append(line)
                        expressionList[c - 1] = t
                        expressionList.pop(c)
                        expressionList.pop(c)
                        c -= 1
                    else:
                        c += 1
                expressionList.pop(-1)
                genQuad(":=",expressionList[0],"_",tokens[position-2])

            return eof


        else:
            print("Error in assingStat")
            exit(-1)
            return -1

    def inputStat(position):#position=input.
        counter=position+1#points to '('.
        id=[]
        if(tokens[counter]=="("):
            counter+=1#points to ID.
            if(tokens[counter][0].isalnum()):
                while(tokens[counter]!=")"):
                    id.append(tokens[counter])
                    counter+=1
                genQuad("inp","".join(id),"_","_")


                return counter
            else:
                print("Invalid input ID,must not start with number!")
                exit(-1)
        else:
            print("Invalid input,expected '('.")
            exit(-1)
            return -1

    def printStat(position):#position=print
        counter=position+1
        if(tokens[counter]=="("):
            expressionList=[]
            counter+=1
            op = []
            while(tokens[counter]!=")"):
                expressionList.append(tokens[counter])
                counter+=1

            if(len(expressionList)>3):
                op=convertCondition(expressionList)

            if(len(expressionList)==3):
                t=newTemp()
                genQuad(expressionList[1], expressionList[0],expressionList[2], t)
                expressionList[0] = t
                expressionList.pop(1)
                expressionList.pop(1)
                op=expressionList
            if(len(expressionList)==2):
                print("Error,false expression in print")
            if(len(expressionList)==1 and "".join(expressionList) in declaredVariables ):
                op="".join(expressionList)
            else:
                print("Variable","".join(expressionList),"is not declared so it cant be printed! ")
            if(op!=1):
                genQuad("out","".join(op),"_","_")
            else:
                print("Error in print,false expression")
                exit(-1)
            return counter
        else:
            print("Error in print,missing '('.")
            exit(-1)

    def expression(expressionList):
        stateTerm=0#in this state we have a variable or int or funtion.We expect to see ADD_OP or MUL_OP after.
        statefactor=1#in this state we have ADD_OP or MUL_OP.We expect to see variable or int or funtion.
        currState=0
        expressionList.pop(-1)
        def evaluateState(token):
            if(token in ADD_OP or token in MUL_OP):
                return 1
            elif(token in declaredVariables or token in funtionsNames or token.isdigit()):
                return 0
            else:
                print("Error in expression")
                exit(-1)
                return -1

        for i in range(0,len(expressionList)):
                if (evaluateState(expressionList[i][-1]) == 1):
                    print("Error in expression \"","".join(expressionList[i]),"\" expect variable or int or funtion!" )
                    exit(-1)
                    return -1

                if(expressionList[i][0] in ADD_OP ):
                    currState=1
                    j=1
                    while(j<len(expressionList[i])):
                        if(evaluateState(expressionList[i][j])==1 and currState==1):
                            print("Invalid expression \"",evaluateState(expressionList[i][j]),"\" expected variable or int or funtion")
                            exit(-1)
                            return -1
                        elif(evaluateState(expressionList[i][j])==1 and currState==0):
                            currState=1
                            j+=1
                        elif(evaluateState(expressionList[i][j])==0 and currState==0):
                            print("Invalid expression\"",evaluateState(expressionList[i][j]),"\" expected ADD_OP or MUL_OP")
                        elif(evaluateState(expressionList[i][j])==0 and currState==1):
                            currState=0
                            j+=1
                        else:
                            print("Error in expression \"" ,"".join(expressionList[i]),"\" !!")
                            exit(-1)
                            return -1


                elif(expressionList[i][0] in declaredVariables or expressionList[i][0] in funtionsNames or expressionList[i][0].isdigit()):
                    currState=0
                    j = 1

                    while (j < len(expressionList[i])):
                        if (evaluateState(expressionList[i][j]) == 1 and currState == 1):
                            print("Invalid expression \" ", "".join(expressionList[i]),"\" expected variable or int or funtion")
                            exit(-1)
                            return -1
                        elif (evaluateState(expressionList[i][j]) == 1 and currState == 0):

                            currState = 1
                            j += 1
                        elif (evaluateState(expressionList[i][j]) == 0 and currState == 0):
                            print("Invalid expression\" ", "".join(expressionList[i]),"\" expected ADD_OP or MUL_OP")

                        elif (evaluateState(expressionList[i][j]) == 0 and currState == 1):

                            currState = 0
                            j += 1
                        else:
                            print("Error in expression \"" ,"".join(expressionList[i]),"\"" )
                            exit(-1)
                            return -1


                else:
                    print("Error in expression \"", "".join(expressionList[i]),"\",character \"","".join(expressionList[i][0]),"\"is an invalid character or undeclared variable!")
                    exit(-1)
                    return -1
        return expressionList

    def returnStat(position):#positios=return
        expressionList=[]
        c=position+1
        while(tokens[c]!=";"):
            expressionList.append(tokens[c])
            c+=1

        if(len(expressionList)==0):
            #expressionList.append(")")
            print("Error in   return,expected variable or int or function call ")
            exit(-1)
        elif(expression([expressionList])!=-1):#return expression is OK
            # print("exit return:",tokens[c])
            retList=[]
            i=0
            expressionList.append(";")
            while (expressionList[i] != ";"):  # this while calculates the MULOP operations first

                if (expressionList[i] in MUL_OP):
                    t = newTemp()
                    genQuad(expressionList[i], expressionList[i - 1], expressionList[i + 1], t)
                    expressionList[i - 1] = t
                    expressionList.pop(i)
                    expressionList.pop(i)
                    i -= 1
                else:
                    i += 1

            i = 0
            while (expressionList[i] != ";"):  # this whuile calculates the MULOP operations first.

                if (expressionList[i] in ADD_OP):
                    t = newTemp()
                    genQuad(expressionList[i], expressionList[i - 1], expressionList[i + 1], t)
                    expressionList[i - 1] = t
                    expressionList.pop(i)
                    expressionList.pop(i)
                    i -= 1
                else:
                    i += 1
            expressionList.pop(-1)
            genQuad("retv",expressionList[0],"_","_")

            return c

        else:

            return  -1

    def callStat(position):#position=call
        functionName=tokens[position+1]
        def actualParList(counter):#position=(
            if(tokens[counter+1]=="in"):#if ypu find in.
                genQuad("par",tokens[counter+2],"CV","_")
                res=expression(counter+1)#call expression.
                return res
            elif(tokens[counter+1]=="inout"):#if you find inout.
                if(tokens[counter+2] in ID):#If ID is declared.
                    genQuad("par", tokens[counter + 2], "REF", "_")
                    return 1
                else:
                    print("error in parameter")
                    exit(-1)
                    return -1
            else:#if you dont find in or inout.
                print("error in parameter")
                exit(-1)
                return  -5
        counter = position
        if (tokens[counter + 1] not  in funtionsNames):#if funtion's name does not exist.
            print("Function '"+str(tokens[counter+1])+"' is not declared.")
            exit(-1)
            return -1
        else:
            counter+=2
            genQuad("par",newTemp(),"RET","_")
            genQuad("call","_","_",functionName)
            return actualParList(counter)

    def condition(conditionList):#position points at '('.

        if(conditionList[0]=="("):
            booltermList=[]
            tempList=[]
            for i in range(1,len(conditionList)-1):
                if(conditionList[i]=="or"):

                    booltermList.append(tempList)
                    tempList=[]

                else:
                    tempList.append(conditionList[i])

            booltermList.append(tempList)
            for list in booltermList:
                if (len(list) == 0):
                  booltermList.remove(list)
            return  boolterm(booltermList)

        else:
            print("Error in condition,expected '('.")
            exit(-1)
            return -1

    def boolterm(booltermList):
        boolfactorList = []
        tempList=[]
        for i in range(0,len(booltermList)):

            for j in range(0,len(booltermList[i])):
                if(booltermList[i][j]=="and"):

                    boolfactorList.append(tempList)
                    tempList=[]
                else:
                    tempList.append(booltermList[i][j])

            boolfactorList.append(tempList)
            tempList = []
        boolfactorList.append(tempList)
        for list in boolfactorList:
            if (len(list) == 0):
                boolfactorList.remove(list)

        return boolfactor(boolfactorList)

    def boolfactor(boolfactorList):
        expressionList=[]
        tempList=[]
        for i in range(0,len(boolfactorList)):
            for j in range(0,len(boolfactorList[i])):
                if(boolfactorList[i][j] in REL_OP):
                    expressionList.append(tempList)
                    tempList=[]
                else:
                    tempList.append(boolfactorList[i][j])

            expressionList.append(tempList)
            tempList=[]

        for list in expressionList:
            if (len(list) == 0):
                expressionList.remove(list)

        return expression(expressionList)

    def ifStat(position):   # position = if

        counter=position+1

        if(tokens[counter]=="("):

            conditionList=[]


            while(tokens[counter]!=")"):#after while end counter points to ')'.
                conditionList.append(tokens[counter])
                counter+=1
            conditionList.append(")")

            expressionList=condition(conditionList)

            #while(conditionList[op]!=)

            if(expressionList!=-1):#if condition are correct.


                if(tokens[counter+1] == "{"):
                    counter+=1
                    conditionList2=convertCondition(conditionList)[0]
                    if(len(conditionList)>3):
                        genQuad(str(conditionList[1]+conditionList[2]),conditionList[0],conditionList[3],"_")
                        genQuad("jump", "_", "_", "_")  # false
                        b_true = quadList[-2][0]
                        b_false = quadList[-1][0]
                        backpatch(b_true, nextquad() + 1)


                    else:

                        genQuad(str(conditionList[1]),str(conditionList[0]),str(conditionList[2]),"_")#true
                        genQuad("jump", "_", "_", "_")#false
                        b_true=quadList[-2][0]
                        b_false=quadList[-1][0]
                        backpatch(b_true, nextquad() + 1)



                    while(tokens[counter]!="}"):#when this loop end counter points to '}' just before else.
                        counter=statements(counter)
                    genQuad("jump", "_", "_", "_")#if jump
                    if_jump=quadList[-1][0]
             


                    if(tokens[counter+1]=="else"):#ELSE
                        counter+=1#points to else.
                        backpatch(b_false,nextquad()+1)
                        counter=elsepart(counter)
                        genQuad("jump", "_", "_", "_")#else jump
                        else_jump=quadList[-1][0]
                        backpatch(else_jump,nextquad()+1)
                        backpatch(if_jump,nextquad()+1)
                        
                    else:
                        print("Missing elsepart in statement")
                        exit(-1)
                        return -1
                else:
                    print("Missing '{' in if statement.")
                    exit(-1)
                    return -1

            else:
                print("Error in conditions in if statement.")
                exit(-1)
                return  -1

        else:
            print("Error,missing ')' is if statement")
            exit(-1)
            return -1

        return counter

    def elsepart(counter):
        while (tokens[counter] != "}"):
            counter += 1
            statements(counter)


        return counter

    def whileStat(position):#position points to while

        counter = position + 1
        whileJump=""

        if (tokens[counter] == "("):

            conditionList = []

            while (tokens[counter] != ")"):  # after while end counter points to ')'.
                conditionList.append(tokens[counter])
                counter += 1
            conditionList.append(")")

            expressionList = condition(conditionList)

            if (expressionList != -1):  # if condition are correct.

                if (tokens[counter + 1] == "{"):
                    counter += 1
                    conditionList2 = convertCondition(conditionList)[0]
                    if (len(conditionList) > 3):
                        whileJump = nextquad() + 1

                        genQuad(str(conditionList[1] + conditionList[2]), conditionList[0], conditionList[3], "_") #create quad for while's condition
                        genQuad("jump", "_", "_", "_")  # false
                        b_true = quadList[-2][0]
                        b_false = quadList[-1][0]
                        #print("bfalse ", b_false)
                        backpatch(b_true, nextquad() + 1)


                    else:
                        whileJump = nextquad() + 1

                        genQuad(conditionList[1], conditionList[0], conditionList[2], "_")  # true
                        genQuad("jump", "_", "_", "_")  # false
                        b_true = quadList[-2][0]
                        b_false = quadList[-1][0]
                        backpatch(b_true, nextquad() + 1)

                    while (tokens[counter] != "}"):  # when this loop end counter points to '}' just before else.
                        counter = statements(counter)
                    backpatch(b_false, nextquad() + 2)
                    genQuad("jump", "_", "_", "_")  # to jump after the end of while.
                    backpatch(quadList[-1][0],whileJump)
                else:
                    print("Missing '{' in if statement.")
                    exit(-1)
                    return -1

            else:
                print("Error in conditions in if statement.")
                exit(-1)
                return -1

        else:
            print("Error,missing ')' is if statement")
            exit(-1)
            return -1

        return counter

    def switchcaseStat(position):#position=switchcase.
        counter=position+1#points to case
        conditionList=[]
        caseJump=[]
        caseState=0#expect to find either case or default
        defaultState=1 #expect to find an expression and only that.
        currState=0
        defaultID=""
        while(True):
            conditionList=[]
            if(currState==caseState):

                if(tokens[counter]=="case"):
                    counter+=1#points to '('.

                    if(tokens[counter]=="("):
                        conditionListist = []
                        while (tokens[counter] != ")"):
                            conditionList.append(tokens[counter])
                            counter += 1
                        conditionList.append(")")
                        expression=condition(conditionList)


                        if(expression!=-1):
                            counter+=1#points '{' to after case(...)
                            if(tokens[counter]=="{"):

                                conditionList2 = convertCondition(conditionList)[0]

                                if (len(conditionList) > 3):
                                    genQuad(conditionList[1] + conditionList[2], conditionList[0], conditionList[3],"_")
                                    genQuad("jump", "_", "_", "_")  # false
                                    b_true = quadList[-2][0]
                                    b_false = quadList[-1][0]
                                    backpatch(b_true, nextquad() + 1)
                                    line="L_"+str(nextLineInCfile())+": if ("+str(conditionList2[0]) + str(conditionList2[1] + str(conditionList2)[2]) +str(
                                        conditionList2[3])+ ") goto L_"+str(nextquad()+1)+"; \\\\ "+str(quadList[-2])
                                    linesForCfile.append(line)


                                else:
                                    genQuad(conditionList[1], conditionList[0], conditionList[2], "_")  # true
                                    genQuad("jump", "_", "_", "_")  # false
                                    cfileb_false=quadList[-1]
                                    b_true = quadList[-2][0]
                                    b_false = quadList[-1][0]
                                    backpatch(b_true, nextquad() + 1)



                                while (tokens[counter] != "}"):  # after this while loop counter points to '}' just before default
                                    statements(counter)
                                    counter += 1
                                counter+=1#points after '}' after the end on case's statements
                                genQuad("jump", "_", "_", "_")
                                caseJump.append(quadList[-1][0])
                                backpatch(b_false,nextquad()+1)



                                if(tokens[counter]=="case"):
                                    continue
                                elif(tokens[counter]=="default"):
                                    currState=defaultState
                                else:
                                    print("Error in switchcase,expected case or default after case. ")
                                    exit(-1)
                            else:
                                print("Expected '{' after case,in switch case")
                                exit(-1)
                        else:
                            print("Error in switchcase,false condition in case.")
                            exit(-1)
                    else:
                        print("Missing '(' after case in switchcase")
                        exit(-1)
                else:
                    print("Missing 'case' from switchcase")
                    exit(-1)
            elif(currState==defaultState):

                if(tokens[counter]=="default"):
                    counter+=1
                    while(tokens[counter]!=";"):
                        counter=statements(counter)
                    genQuad("jump","_","_","_")
                    defaultJump=quadList[-1][0]
                    backpatch(defaultJump,nextquad()+1)
                    break
                else:
                    print("Expected default in switchcase.")
                    exit(-1)
            else:
                print("Error in switchcase:")
                exit(-1)

        for i in range(len(caseJump)):
            for j in range (len(quadList)):
                if(quadList[j][0] == caseJump[i]):
                    backpatch(caseJump[i],nextquad()+1)

        return counter

    def forcaseStat(position):  # position=forcase.
        counter = position + 1  # points to case
        caseIndex = counter
        conditionList=[]
        caseState = 0  # expect to find either case or default
        defaultState = 1  # expect to find an expression and only that.
        currState = 0
        firstCaseID="0"
        if(tokens[counter]=="case"):
            counter += 1  # points to '('.

            if (tokens[counter] == "("):
                conditionList = []
                while (tokens[counter] != ")"):
                    conditionList.append(tokens[counter])
                    counter += 1
                conditionList.append(")")
                expression = condition(conditionList)

                if (expression != -1):
                    counter += 1  # points '{' to after case(...)
                    if (tokens[counter] == "{"):

                        conditionList2 = convertCondition(conditionList)[0]
                        firstCaseID = nextquad() + 1
                        if (len(conditionList) > 3):
                            genQuad(conditionList[1] + conditionList[2], conditionList[0], conditionList[3],"_")
                            genQuad("jump", "_", "_", "_")  # false
                            b_true = quadList[-2][0]
                            b_false = quadList[-1][0]
                            backpatch(b_true, nextquad() + 1)
                        else:
                            genQuad(conditionList[1], conditionList[0], conditionList[2], "_")  # true
                            genQuad("jump", "_", "_", "_")  # false
                            b_true = quadList[-2][0]
                            b_false = quadList[-1][0]
                            backpatch(b_true, nextquad() + 1)

                        while (tokens[counter] != "}"):  # after this while loop counter points to '}' just before default
                            statements(counter)
                            counter += 1
                        counter += 1  # points after '}' after the end on case's statements
                        genQuad("jump", "_", "_", "_")

                        backpatch(quadList[-1][0], firstCaseID)
                        backpatch(b_false, nextquad() + 1)
        conditionList=[]
        while (True):

            if (currState == caseState):
                counter= caseIndex
                if (tokens[counter] == "case"):
                    counter += 1  # points to '('.

                    if (tokens[counter] == "("):
                        conditionList = []
                        while (tokens[counter] != ")"):

                            conditionList.append(tokens[counter])
                            counter += 1
                        conditionList.append(")")
                        expression = condition(conditionList)
                       # print(conditionlist)


                        if (expression != -1):
                            counter += 1  # points '{' to after case(...)
                            if (tokens[counter] == "{"):

                                conditionList2 = convertCondition(conditionList)[0]
                                if (len(conditionList) > 3):
                                    genQuad(conditionList[1] + conditionList[2], conditionList[0], conditionList[3],
                                            "_")
                                    genQuad("jump", "_", "_", "_")  # false
                                    b_true = quadList[-2][0]
                                    b_false = quadList[-1][0]
                                    backpatch(b_true, nextquad() + 1)
                                else:
                                    genQuad(conditionList[1], conditionList[0],conditionList[2], "_")  # true
                                    genQuad("jump", "_", "_", "_")  # false
                                    b_true = quadList[-2][0]
                                    b_false = quadList[-1][0]
                                    backpatch(b_true, nextquad() + 1)

                                while (tokens[counter] != "}"):  # after this while loop counter points to '}' just before default
                                    statements(counter)
                                    counter += 1
                                counter += 1  # points after '}' after the end on case's statements
                                genQuad("jump","_","_","_")

                                backpatch(quadList[-1][0],firstCaseID)
                                backpatch(b_false, nextquad() + 1)
                                if (tokens[counter] == "case"):
                                    continue
                                elif (tokens[counter] == "default"):
                                    currState = defaultState
                                else:
                                    print("Error in forcase,expected case or default after case. ")
                                    exit(-1)
                            else:
                                print("Expected '{' after case,in forcase")
                                exit(-1)
                        else:
                            print("Error in forcase,false condition in case.")
                            exit(-1)
                    else:
                        print("Missing '(' after case in forcase")
                        exit(-1)
                else:
                    print("Missing 'case' from forcase")
                    exit(-1)
            elif (currState == defaultState):

                if (tokens[counter] == "default"):
                    counter += 1
                    while (tokens[counter] != ";"):
                        counter = statements(counter)

                    genQuad("jump","_","_","_")#create jump after we end with default
                    backpatch(quadList[-1][0],nextquad()+1)#the default jump will point at the next quad it will be created.
                    return counter
                else:
                    print("Expected default in forcase.")
                    exit(-1)
            else:
                print("Error in forcase:")
                exit(-1)
        return counter

    def incaseStat(position):  # position=switchcase.
        return 2

    def comments(position):#position= '#'
        counter=position+1
        while(tokens[counter]!="#"):
            counter+=1
        return counter+1 #!!!!!! this must be counter+1 because it keep searching for # if we return "#".

    def convertCondition(list):
        i=1
        relopflag=False
        conditionList=list
        while(conditionList[i]!=")"):
            if (conditionList[i] in MUL_OP):
                if(conditionList[i] in REL_OP):
                    relopflag=True
                t = newTemp()
                genQuad(conditionList[i], conditionList[i - 1], conditionList[i + 1], t)
                conditionList[i - 1] = t
                conditionList.pop(i)
                conditionList.pop(i)
                i -= 1
            else:
                i += 1
        i=0

        while (conditionList[i] != ")"):
            if (conditionList[i] in ADD_OP):
                t = newTemp()
                genQuad(conditionList[i], conditionList[i - 1], conditionList[i + 1], t)
                conditionList[i - 1] = t
                conditionList.pop(i)
                conditionList.pop(i)
                i -= 1
            else:
                i += 1

        conditionList.pop(0)
        conditionList.pop(-1)
        if(relopflag==True):
            if(conditionList[1] in REL_OP and conditionList[2] in REL_OP):
                flag=True
            else:
                flag=False
            return conditionList,flag

        return conditionList


#----------MAIN PROGRAM----------------
    tokens=lexer()  # lexer fills the list with tokens.
    program(0)
    createIntFile()
#-----------END OF MAIN PROGRAM-----------------------------------


def nextquad():#returns the number of quad which is about to be created.
    return numQuad

def genQuad(operation,operant1,operant2,localVar):
    global numQuad
    global quadList
    numQuad += 1
    quad= []#create a local list so i can add it in quadList.


    quad.append(str(nextquad())+":")#adding number first.
    quad.append(operation)#adding the operation.
    quad.append(operant1)#adding first operant.
    quad.append(operant2)#adding second operant.
    quad.append(localVar)#adding local variable.

    quadList.append(quad)

def newTemp():
    global T_i,scopeList,nestingLevel

    localList=['T_']
    localList.append(str(T_i))
    newTempVar="".join(localList)#newTempVar= T_0...T_1...etc

    tempVariables.append(newTempVar)
    T_i += 1

    #Create new Temporary Variable Entity.
    entity=Entity()
    tempVarEntity=entity.TemporaryVariable(newTempVar,0,nestingLevel)
    scopeList[-1].addEntity(tempVarEntity)#add temprary variable to scope.

    return newTempVar

def emptyList():
    list=[]
    return  list

def makeList():

    list=[x]

    return list

def backpatch(id,z):

    for quad in quadList:
        for position in quad:
            if(position==id):
                quad[-1]=z

def createIntFile():

    file=sys.argv[1]+".int"
    testfilename=[]
    for i in file:
        if(i=="."):
            break
        else:
            testfilename.append(i)

    newfile="".join(testfilename[0:len(testfilename)])+".int"


    testFile =open(newfile,"w")
    for quad in quadList:
        testFile.write(str(quad)+"\n")

def createCfile():
    file = sys.argv[1]
    testfilename = []
    mainC="int main ()\n { \n"
    for i in file:
        if (i == "."):
            break
        else:
            testfilename.append(i)

    newfile = "".join(testfilename[0:len(testfilename)]) + ".c"
    testFile=open(newfile,"w+")


    variablesUsed ="int "
    for var in declaredVariables:
        variablesUsed = variablesUsed + var
        variablesUsed += ","
    for tempvar in tempVariables:
        variablesUsed = variablesUsed  +tempvar
        variablesUsed+=","
    variablesUsed =variablesUsed[:-1] +";\n"#to remove last ','
    testFile.write("#include <stdio.h>\n")
    testFile.write(variablesUsed)
    testFile.write(mainC)

    global quadList
    ADD_OP = ["+", "-"]
    MUL_OP = ["*", "/"]
    REL_OP = ["<", ">", "=", "<=", ">=", "<>"]
    for i in quadList:
        if(i[1]=="begin_block"):
            testFile.write("L_" + str(i[0]) +"\n")
        elif(i[1] in ADD_OP):
            line="L_"+str(i[0])+" "+ str(i[4]) +"="+ str(i[2]) +str(i[1])+ str(i[3])+ ";"
            testFile.write(line+"\n")
        elif(i[1] in MUL_OP):
            line = "L_" + str(i[0]) + " " + str(i[4]) + "=" + str(i[2]) + str(i[1]) + str(i[3])+ ";"
            testFile.write(line + "\n")
        elif(i[1] in REL_OP):
            if(i[1] == "<>"):
                line = "L_" + str(i[0]) + " if (" + str(i[2]) + " != " + str(i[3]) + ") goto L_"+ str(i[4])+ ";"
                testFile.write(line+"\n")
            elif(i[1] == "="):
                line = "L_" + str(i[0]) + " if (" + str(i[2]) + " == " + str(i[3]) + ") goto L_"+ str(i[4])+ ";"
                testFile.write(line+"\n")            
            else:
                line = "L_" + str(i[0]) + " if (" + str(i[2]) + str(i[1]) + str(i[3]) + ") goto L_"+ str(i[4])+ ";"
                testFile.write(line+"\n")            
            
        elif(i[1]=="jump"):
            line="L_"+str(i[0])+" goto L_"+str(i[4])+ ";"
            testFile.write(line+"\n")
        elif(i[1]=="retv"):
            line="L_" + str(i[0])+" " +"return "+ " "+str(i[2])+ ";"
            testFile.write(line+"\n")
        elif(i[1]==":="):
            line="L_"+ str(i[0])+ " " + str(i[4]) + "=" +str(i[2])+ ";"
            testFile.write(line+"\n")
        elif(i[1]=="out"):#print
            line="L_"+ str(i[0]) + "printf(\"%i" + " \\" + 'n' + "\", " + str(i[2]) + ");"
            testFile.write(line+"\n")
        elif (i[1] == "inp"):  # scanf
            line = "L_" + str(i[0]) + "scanf(\"%i"  + "\",& " + str(i[2]) + ");"
            testFile.write(line + "\n")
        elif(i[1]=="halt"):
            line= "L_"+str(i[0]) + ";"
            testFile.write(line)
           
    testFile.write("\n}")

def nextLineInCfile():
    global lineCounter
    lineCounter+=1
    return lineCounter

def writeToSymbolTableFile():
    # WRITE TO FILE EVERY TIME A SCOPE IS DELETED.
    global scopeList
    str=[sys.argv[1],"_Symboltable"]
    filename="".join(str)
    file=open(filename,"w")

    for scope in scopeList:

        file.write("\nScope: ")
        file.write("%s" %scope.getNestingLevel()+"\n")
        for entity in scope.getEntityList():

            if(type(entity) is Entity.Function):
                argList=entity.getArguments()#this is a list with Arguments Entities.
                argListParMode=[]#this is a list which is going to be filled with cv,ref.
                for argument in argList:#fill argListParMode list with cv,ref.
                    argListParMode.append(argument.getParMode())
                str="/".join(argListParMode)#join cvs and refs with '/'.
                file.write(entity.getName() + "/%s"%entity.getOffset()+"/" +str+"\n")#write to file.
            else:
                file.write(entity.getName()+"/%s"%entity.getOffset()+"\n")

    file.write("----------------------------------------------------------------\n")
    file.close()

class Scope:

    def __init__(self,level,offset):
        self.entityList=[]
        self.nestingLevel=level
        self.offset=offset

    def getNestingLevel(self):
        return self.nestingLevel

    def addEntity(self,newEntity):
        self.offset+=4
        newEntity.setOffset(self.getOffset())
        self.entityList.append(newEntity)
        #writeToSymbolTableFile()

    def getEntityList(self):
        return self.entityList

    def setOffset(self,newOffset):
        self.offset=newOffset

    def getOffset(self):
        return self.offset

class Entity:



    class Variable:

        def __init__(self,name,type,offset,nestingLevel):
            self.nestingLevel=nestingLevel
            self.name=name
            self.type=type
            self.offset=offset #apostasi apo thn arxh toy eggrafimatos.

        def getName(self):
            return self.name

        def getOffset(self):
            return self.offset

        def getType(self):
            return self.type

        def getNestingLevel(self):
            return self.nestingLevel

        def setOffset(self,newOffset):
            self.offset=newOffset

    class Function:

        def __init__(self,name,type,startQuad,offset,nestingLevel):
            self.nestingLevel=nestingLevel
            self.name=name
            self.type=type
            self.startQuad=startQuad
            self.arguments=[]

            self.offset=offset #mikos eggrafimatos.

        def setFrameLength(self,newFrameLength):
            self.offset=newFrameLength

        def setOffset(self, newOffset):
            self.offset = newOffset

        def addArguments(self,newArgument):
            if(newArgument != 0):# if 0 is given as newArgument just ignore it.
                self.arguments.append(newArgument)

        def getName(self):
            return self.name

        def getArguments(self):
            return self.arguments

        def getOffset(self):
            return self.offset

        def getFrameLength(self):
            return self.frameLength

        def getNestingLevel(self):
            return self.nestingLevel

    class Constant:

        def __init__(self,name,value,nestingLevel):
            self.nestingLevel=nestingLevel
            self.name=name
            self.value=value

        def getName(self):
            return self.name

        def getValue(self):
            return self.value

        def getNestingLevel(self):
            return self.nestingLevel

    class Parameter:

        def __init__(self,name,parMode,offset,nestingLevel):
            self.nestingLevel=nestingLevel
            self.name=name
            self.parMode=parMode
            self.offset=offset #apostash apo thn korufh ths stoibas.

        def getName(self):
            return self.name

        def getNestingLevel(self):
            return self.nestingLevel

        def getParMode(self):
            return self.parMode

        def getOffset(self):
            return self.offset

        def setOffset(self, newOffset):
            self.offset = newOffset

    class TemporaryVariable:

        def __init__(self,name,offset,nestingLevel):
            self.nestingLevel=nestingLevel
            self.name=name
            self.offset=offset #apostasi apo korifi stoibas.

        def setOffset(self, newOffset):
            self.offset = newOffset

        def getName(self):
            return self.name

        def getOffset(self):
            return self.offset
        def getNestingLevel(self):
            return self.nestingLevel

class Argument:
    def __init__(self,parMode,type,nestingLevel):
        self.nestingLevel = nestingLevel
        self.parMode=parMode
        self.type=type

    def getParMode(self):
        return self.parMode

    def getNestingLevel(self):
        return self.nestingLevel

def searchEntityVariable(name):
    global scopeList
    for scope in scopeList:
        for entity in scope.getEntityList():
            if(entity.getName()==name):
                    return scope,entity

    print("Error,did not find entity with name:",name)
    exit(-1)

def gnlvcode(name):
    global scopeList,quadScope
    name = sys.argv[1]
    name = name[:-3]
    name = name
    filename = name + ".asm"
    file = open(filename, "a")

    file.write("lw $t0,-4($t0)\n")#write to father's stack.
    #find in which entity name belongs to thus in which scope belongs to thus the nesting level.
    (scope,entity)=searchEntityVariable( name )
    nestingDiff=quadScope-entity.getNestingLevel()

    for i in range(0,nestingDiff):
        file.write("lw $t0,-4($t0)\n")

    file.write("addi $t0,$t0,-",entity.getOffset(),"\n")

    file.close()

def loadvr(variable,r):
    global  quadScope
    name = sys.argv[1]
    name = name[:-3]
    name = name
    filename = name + ".asm"
    file = open(filename, "a")

    if(variable.isdigit()):# If variable is constant.
        file.write("li %s"%r + ",%s"%variable +"\n")
        return 0

    (scope, entity) = searchEntityVariable(variable)
    

    if(entity.getNestingLevel() == 0 ):# If variable is global.
       
       # file.write("lw "+str(r) + ",-" + str(entity.getOffset()) + "($s0)\n")
        file.write("skata")
    elif(quadScope == entity.getNestingLevel() ): #variable has same nesting level with the function in which it gow declared.

        if(type(entity) is Entity.Variable):
            file.write("lw t%s"%r + ",-" + "%s"%entity.getOffset() + "($sp)\n")

        if(type(entity) is Entity.TemporaryVariable):
            print(entity.getName())
            file.write("lw t%s"%r + ",-" + "%s"%entity.getOffset() + "($sp)\n")

        if(type(entity) is Entity.Parameter and entity.getParMode()=="cv"):
            print(entity.getName())

            file.write("lw t%s"%r + ",-" + "%s"%entity.getOffset() + "($sp)\n")

        if (type(entity) is Entity.Parameter and entity.getParMode() == "ref"):
            print(entity.getName())

            file.write("lw t%s"%r + ",-" + "%s"%entity.getOffset() + "($sp)\n")
            file.write("lw t%s"%r + ",-" + "($t0)\n")

    elif(quadScope>entity.getNestingLevel()):# variable declared in ancestor and it is variable or parameter with type=cv.

        if(type(entity) is Entity.Variable):
            gnlvcode(variable)
            file.write("lw t%s"%r + ",-" + "%s"%entity.getOffset() + "($sp)\n")
        elif(type(entity) is Entity.Parameter and entity.getParMode()=="cv"):
            gnlvcode(variable)
            
            file.write("lw t%s" % r + ",-" + "%s" % entity.getOffset() + "($sp)\n")
        elif (type(entity) is Entity.Parameter and entity.getParMode() == "ref"):
            gnlvcode(variable)
            file.write("lw $t0,($t0)\n")
            file.write("lw $t%s" %r + "$t0\n" )

    file.close()

def storerv(r,v):
    global quadScope
    name = sys.argv[1]
    name = name[:-3]
    name = name
    filename = name + ".asm"
    file = open(filename, "a")
    (scope,entity)=searchEntityVariable(v)

    if(entity.getNestingLevel() == 0):# If variable is global.
        file.write("sw %s"%r +",-%s"%entity.getOffset() +"($s0)\n")

    elif( quadScope == entity.getNestingLevel()):
        if(type(entity) is Entity.Variable):
            file.write("sw $t%s"%r +",-%s"%entity.getOffset() + "$sp\n")
        elif(type(entity) is Entity.TemporaryVariable):
            file.write("sw $t%s"%r +",-%s"%entity.getOffset() + "$sp\n")

        elif(type(entity) is Entity.Parameter and entity.getParMode() == "cv"):
            file.write("sw $t%s"%r +",-%s"%entity.getOffset() + "$sp\n")

        elif (type(entity) is Entity.Parameter and entity.getParMode() == "ref"):
            file.write("sw $t%s" % r + ",-%s" % entity.getOffset() + "$sp\n")
            file.write("sw $t%s" % r + "," + "$t0\n")

    elif(quadScope > entity.getNestingLevel()):
            if(type(entity) is Entity.Variable):
                gnlvcode(v)
                file.write("sw $t%s" % r + "," + "($t0)\n")

            elif(type(entity) is Entity.Parameter and entity.getParMode() == "cv"):
                gnlvcode(v)
                file.write("sw $t%s" % r + "," + "($t0)\n")
            elif (type(entity) is Entity.Parameter and entity.getParMode() == "ref"):
                gnlvcode(v)
                file.write("lw $t0"+ ",($t0)\n")
                file.write("sw $t%s" % r +",($t0)\n")
    file.close()

def createAsmFile():
    global quadList,quadScope
    name=sys.argv[1]
    name=name[:-3]
    name=name
    filename =name +".asm"
    
    file = open(filename, "w")
    quadScope=0
    
    for quad in quadList:
        file.write("L_{}".format(quad[0]))
        file.write("\n")

        if(quad[1]=="begin_block"):
            file.write("sw $ra , 0($sp)\n")
            quadScope=+1

        elif(quad[1]=="end_block"):
            file.write("lw $ra , 0($sp)\n")
            quadScope-=1
        elif (quad[1] == ":="):  # "id,:=,x,_,z"
            file.write("\n")
            loadvr(quad[2],"$t1")
            storerv("$t1",quad[4])
        elif(quad[1] == "jump"):
                file.write("b L_%s\n"%quad[4])
        #-----REL_OPS------['9:', <, x, y, z]
        elif(quad[1] == ">"):
            loadvr(quad[2],"$t1")
            loadvr(quad[3],"$t2")
            file.write("bgt,$t1,$t2,L_%s"%quad[4] + "\n")
        elif (quad[1] == "<"):
            loadvr(quad[2], "$t1")
            loadvr(quad[3], "$t2")
            file.write("blt,$t1,$t2,L_%s" % quad[4] + "\n")
        elif (quad[1] == "="):
            loadvr(quad[2], "$t1")
            loadvr(quad[3], "$t2")
            file.write("beq,$t1,$t2,L_%s" % quad[4] + "\n")
        elif (quad[1] == "<>"):
            loadvr(quad[2], "$t1")
            loadvr(quad[3], "$t2")
            file.write("bne,$t1,$t2,L_%s" % quad[4] + "\n")
        elif (quad[1] == "<="):
            loadvr(quad[2], "$t1")
            loadvr(quad[3], "$t2")
            file.write("ble,$t1,$t2,L_%s" % quad[4] + "\n")
        elif (quad[1] == ">="):
            loadvr(quad[2], "$t1")
            loadvr(quad[3], "$t2")
            file.write("bge,$t1,$t2,L_%s" % quad[4] + "\n")

        #------OP-----------['3:', -, x, y, z]
        elif(quad[1] == "+"):
            loadvr(quad[2],"$t1")
            loadvr(quad[3],"$t2")
            file.write("add $t1,$t1,$t2\n")
            storerv(1,quad[4])
        elif (quad[1] == "-"):
            loadvr(quad[2], "$t1")
            loadvr(quad[3], "$t2")
            file.write("sub $t1,$t1,$t2\n")
            storerv("$t1", quad[4])
        elif (quad[1] == "*"):
            loadvr(quad[2], "$t1")
            loadvr(quad[3], "$t2")
            file.write("mul $t1,$t1,$t2\n")
            storerv("$t1", quad[4])
        elif (quad[1] == "/"):
            loadvr(quad[2], "$t1")
            loadvr(quad[3], "$t2")
            file.write("div $t1,$t1,$t2\n")
            storerv("$t1", quad[4])
        ##---------PRINT---------['5:', 'out', 'x', '_', '_']
        elif(quad[1] == "out"):
            file.write("li $v0,1\n")
            loadvr(quad[2],"$a0")
            file.write("syscall\n")
        #--------INPUT----['6:', 'inp', 'x', '_', '_']
        elif(quad[1] == "inp"):
            file.write("li $v0,5\n")
            file.write("syscall\n")
            storerv("%v0",quad[2])
        #-----------RETURN---------[7:', 'retv', '0', '_', '_']
        elif(quad[1] == "retv"):
            loadvr(quad[2],"$t1")
            file.write("lw $t0,-8($sp)\n")
            file.write("sw $t1,($t0)\n")
        #------PARAMETER-----------
        elif(quad[1]=="par"):
            file.write("addi $fp,$sp,framelength\n")#???????
            if(quad[3]=="cv"):
                loadvr(quad[2],"%t0")
                file.write("sw $t0,-(12+4)($fp)\n")
            elif(quad[3] == "ref"):
                file.write("addi $t0,$sp,-offset\n")  # ???????
                file.write("sw $t0,-(12+4)($fp)\n")  # ???????
    file.close()

def start():

    synt()
    writeToSymbolTableFile()



start()
createAsmFile()
