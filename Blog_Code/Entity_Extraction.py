# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0


import boto3
import os
import glob
from decimal import *

#replace the name of your corresponding dynamodb table between the single quotes below. You can find the name of the table in the outputs tab of the cloudforrmation stack.
ddb_table = 'CompMedDemo-ddbtable-1R0JWXLE0PRL'



notes_dir = 'notes'
note_files = glob.glob(os.path.join(notes_dir, '*'))
note_files.sort()

dynamoDBResource = boto3.resource('dynamodb', region_name = 'us-east-1')
table = dynamoDBResource.Table(ddb_table)
hera  = boto3.client(service_name='comprehendmedical', use_ssl=True, region_name = 'us-east-1')


#set innitial values of the counters and variables
raw_rowid=1
rowid = 1
Trait_List = []
Attribute_List = []



#loop for each note file
for file in note_files:
    print ('Processing '+file+ '...')
    # Open the file and read it into a variable
    testtext = open(file).read()
    
    # Call the detect_entities API to extract the entities
    testresult = hera.detect_entities(Text = testtext)
    
    # Create a list of entities
    testentities = testresult['Entities']
    
    #insert the JSON output into a dataframe.
    raw_rowid = raw_rowid+1
    
    # Create a loop to iterate through the individual entities
    for row in testentities:
        # Remove PHI from the extracted entites
        if row['Category'] != "PERSONAL_IDENTIFIABLE_INFORMATION":
            
            # Create a loop to iterate through each key in a row 
            for key in row:
                
                # Create a list of traits
                if key == 'Traits':
                    if len(row[key])>0:
                        Trait_List = []
                        for r in row[key]:
                            Trait_List.append(r['Name'])
                
                # Create a list of Attributes
                elif key == 'Attributes':
                    Attribute_List = []
                    for r in row[key]:
                        Attribute_List.append(r['Type']+':'+r['Text'])
            
            
            # Enter the row into DynamoDB
            table.put_item(
                Item={
                        'ROWID' : rowid,
                        'ID' : row['Id'],
                        'Text': row['Text'],
                        'Type' : row['Type'],
                        'Category' : row['Category'],
                        'Score' : Decimal(str(row['Score'])),
                        'Trait_List' : str(Trait_List),
                        'Attribute_List' : str(Attribute_List)
                        }
                    )

        rowid = rowid+1

print ('Entities extracted and inserted into dynamodb.')

