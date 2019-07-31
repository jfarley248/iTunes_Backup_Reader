'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunes_Backup_Reader
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   structs.py
   ------------

   Parsing MBDB made possible by:
   https://www.securitylearn.net/2012/05/05/iphone-backup-mbdb-file-structure/


'''
from construct import *







'''Really sketchy way of, quote on quote, parsing the iTunes Prefs FRPD to find last 3 users/machines connected to'''
def frpdHelper(data, logger):

    '''Array to store usernames and computers'''
    userComps = ""

    '''Creates bytearrays for finding magic key and full name'''
    logger.debug("Data being interpreted for FRPD is of type: " + str(type(data)))
    x = type(data)
    byteArr = bytearray(data)
    userByteArr = bytearray()

    '''The bytes here are always 88 bytes before the start of host usernames'''
    magicOffset = byteArr.find(b'\x01\x01\x80\x00\x00')
    magic = byteArr[magicOffset:magicOffset + 5]

    flag = 0

    if magic == b'\x01\x01\x80\x00\x00':
        logger.debug("Found magic bytes in iTunes Prefs FRPD... Finding Usernames and Desktop names now")
        '''93 is the offset after the magic that we see user names'''
        for x in range (int(magicOffset + 92), len(data)):
            if (data[x]) == 0:
                '''157 is the offset after the magic where the computer name is found'''
                x = int(magicOffset) + 157
                if userByteArr.decode() == "":
                    continue
                else:
                    if flag == 0:
                        userComps += userByteArr.decode() + " - "
                        flag = 1
                    else:
                        userComps += userByteArr.decode() + "\n"
                        flag = 0
                    userByteArr = bytearray()
                    continue
            else:
                char =  (data[x])
                userByteArr.append(char)


        return userComps

'''Really sketchy way of, quote on quote, parsing the SINF to find the full name'''
def sinfHelper(data, logger):

    '''Creates bytearrays for finding magic key and full name'''
    byteArr = bytearray(data)
    userByteArr = bytearray()

    '''Looks for magic keyword of name'''
    magicOffset = byteArr.find(b"name")
    magic= byteArr[magicOffset:magicOffset+4]
    if magic == b"name":
        '''Finds characters until null terminator, appends to userByteArr'''
        logger.debug("Found magic name in SINF")
        for x in range (int(magicOffset+4), len(data)):
            if (data[x]) == 0:
                break
            else:
                char =  (data[x])
                userByteArr.append(char)

        userName = userByteArr.decode()
        logger.debug("Found user's name from SINF: " + userName)
        return userName
    else:
        return ""



CUST_STRING = Struct (
    "unknown00" / Byte,
    "Length" / Byte,
    "String" / If(this.Length != 255, Bytes(this.Length))


)

PROPERTY = Struct (
    "Name" / CUST_STRING,
    "Value" / CUST_STRING
)

MBDB = Struct (
    "Domain" / CUST_STRING,
    "Path" / CUST_STRING,
    "LinkTarget" / CUST_STRING,
    "DataHash" / CUST_STRING,
    "Encryption_Key" / CUST_STRING,
    "Mode" / Int16ub,
    "inodeNumber" / Int64ub,
    "UserID" / Int32ub,
    "GroupID" / Int32ub,
    "LastModifiedTime" / Int32ub,
    "LastAccessedTime" / Int32ub,
    "CreatedTime" / Int32ub,
    "Size" / Int64ub,
    "ProtectionClass" / Byte,
    "PropertyCount" / Byte,
    "Properties" / PROPERTY[this.PropertyCount]



)

MBDB_HEADER = Struct (
    "Header" / PaddedString(4, "utf-8"),
    "Unknown" / Bytes(2),
    "Records" / GreedyRange(MBDB)



)
#38
#