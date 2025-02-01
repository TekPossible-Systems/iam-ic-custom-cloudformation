# LAMBDA FUNCTION TO HANDLE NEW IAM IC USERS

import boto3
import cfnresponse

def create_user(event,context, iamic, response_data, identitystore_id):
    username = event['ResourceProperties']['UserName']
    display_name = event['ResourceProperties']['DisplayName']
    group_membership = list(event['ResourceProperties']['GroupIds']) # List of group names to join the user to
    user_email = event['ResourceProperties']['PrimaryEmail'] # Mainly required for inital account setup, so added here
    
    # Create the user
    try:
        new_user = iamic.create_user(
            IdentityStoreId=identitystore_id,
            UserName=username,
            Name={
                'GivenName': display_name.split(' ')[0],
                'FamilyName': display_name.split(' ')[1],
                'Formatted': display_name
            },
            DisplayName=display_name,
            Emails=[{'Value': str(user_email), 'Type': 'Work', 'Primary': True}]       
        )

        for group in group_membership:
            iamic.create_group_membership(
                IdentityStoreId=identitystore_id,
                GroupId = group,
                MemberId={
                        'UserId': new_user['UserId']
                }
            )
        response_data = new_user
        cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)

    except Exception as e:
        print("Exception was found: \n" + str(e))
        response_data['Data'] = str(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data)
def create_group(event,context, iamic, response_data, identitystore_id):
    try:
        display_name = event['ResourceProperties']['DisplayName']
        description = event['ResourceProperties']['Description']
        new_group = iamic.create_group(
            IdentityStoreId=identitystore_id,
            DisplayName=display_name,
            Description=description
        )
        response_data = new_group
        print(response_data)
        cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)   
    except Exception as e:
        print("Exception was found: \n" + str(e))
        response_data['Data'] = str(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data) 
# def update_user(event, context, iamic, response_data, identitystore_id):

# def update_group(event, context, iamic, response_data, identitystore_id):

# def delete_user(event, context, iamic, response_data, identitystore_id):

# def delete_group(event, context, iamic, response_data, identitystore_id):

def lambda_handler(event, context):
    response_data = {}
    try:
        iamic = boto3.client('identitystore')
        event_type = event['RequestType']
        print(event_type)
        # Get parameters from CRD
        resource_type = event['ResourceProperties']['Type'] # Must be one of User,Group
        if str(resource_type) not in ['User', 'Group']:
            response_data['Data'] = "The request type for this CRD must either be User or Group. Dieing of sadness!"
            cfnresponse.send(event, context, cfnresponse.FAILED, response_data)
            raise Exception
        
        # Okay so at least that was defined! Next to check the identity store id!

        identitystore_id =  event['ResourceProperties']['IdentityStoreID']

        if (str(identitystore_id) == "") or identitystore_id == None:
                response_data['Data'] = "The Identitystore ID was not defined or not valid. Please double check that value."
                cfnresponse.send(event, context, cfnresponse.FAILED, response_data)
                raise Exception
        
        if event_type == 'Create':
            if resource_type == "User":         
                create_user(event, context, iamic, response_data, identitystore_id) 

            elif resource_type == "Group":
                create_group(event, context, iamic, response_data, identitystore_id)

        elif event_type == 'Delete':
            if resource_type == 'User':
                print('Not yet implemented!')     
                cfnresponse.send(event, context, cfnresponse.FAILED, response_data)

            elif resource_type == 'Group':
                print('Not yet implemented!')
                cfnresponse.send(event, context, cfnresponse.FAILED, response_data)

        elif event_type == 'Update':
            if resource_type == 'User':
                print('Not yet implemented!') 
                cfnresponse.send(event, context, cfnresponse.FAILED, response_data)
 
            elif resource_type == 'Group':
                print('Not yet implemented!')
                cfnresponse.send(event, context, cfnresponse.FAILED, response_data)


    except Exception as e:
        print(str(e))
        response_data['Data'] = str(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data)
