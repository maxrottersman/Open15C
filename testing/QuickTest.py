import pandas as pd
import re

filename = r'C:\Files2020_Data\XBRLFolders_485BPOS\0000005138-19-000036\0000005138-19-000036.csv'
filename = r'C:\Files2020_Data\XBRLFolders_485BPOS\0000051931-20-000080\0000051931-20-000080.csv'
df = pd.read_csv(filename)
#print(df)

#print(df.count())
#print(list(df.columns.values))
#print(df['Label'])

for i, row in enumerate(df.values):
    #print(row[1])
    contextRef = str(row[1])
    pattern = r'[S]\d{4,9}'
    SeriesNum = re.search(pattern, contextRef) 
    pattern = r'[C]\d{4,9}'
    ClassNum = re.search(pattern, contextRef) 
    print(row[1])
    if not SeriesNum == None:
        print(SeriesNum[0])
    if not ClassNum == None:
        print(ClassNum[0])
    
    #print(str(SeriesNum[0]) +'|'+str(ClassNum[0]))
  

    # for char_index in range(len(contextRef)-9):
    #     # Only if we can next char for numeric
    #     if char_index < len(contextRef):
    #         # Get letter
    #         char =contextRef[char_index]
    #         # if potential Series or Class
    #         if char == 'S' or char == 'C':
    #             # if followed by at least 2-digit number
    #             if contextRef[char_index+1].isnumeric() and contextRef[char_index+2].isnumeric():
    #                 string_number = ''
    #                 start_number_index = char_index+1
    #                 checkstringlength = len(contextRef)
    #                 for start_number_index in range(len(contextRef)-checkstringlength):
    #                     if contextRef[start_number_index].isnumeric():
    #                         string_number = string_number+contextRef[start_number_index]
    #                     else:
    #                         break
    #                 string_number = char + string_number
    #                 print(string_number)




    