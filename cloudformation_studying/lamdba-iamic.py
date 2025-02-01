# LAMBDA FUNCTION TO HANDLE NEW IAM IC USERS

import boto3
import cfnresponse

def lambda_handler(event, context):
    iam_idc = boto3.client('identitystore')
    response_data = {}

    iamic = boto3.resource

    event_type = event['RequestType']

    # Get parameters from CRD
    request_type = event['ResourceProperties']['Type'] # Must be one of User,Group

    if str(request_type) not in ['User', 'Group']:
        response_data['DATA'] = "The request type for this CRD must either be User or Group. Dieing of sadness!"
        cfnresponse.send(event, context, cfnresponse.FAILURE, response_data)
        raise Exception
    
    # Okay so at least that was defined! Next to check the identity store id!

    identitystore_id =  event['ResourceProperties']['IdentityStoreID']

    if (str(identitystore_id) == "") or identitystore_id == None:
            response_data['DATA'] = "The Identitystore ID was not defined or not valid. Please double check that value."
            cfnresponse.send(event, context, cfnresponse.FAILURE, response_data)
            raise Exception

    if request_type == "User":         
        username = event['ResourceProperties']['UserName']
        display_name = event['ResourceProperties']['DisplayName']
        group_membership = list(event['ResourceProperties']['GroupIds']) # List of group names to join the user to
        user_email = event['ResourceProperties']['PrimaryEmail'] # Mainly required for inital account setup, so added here
        
        # Create the user
        try:
            new_user = iamic.create_user(
                IdentityStoreId=identitystore_id,
                UserName=username,
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
            response_data['DATA'] = "User was created with userid " + new_user['UserId']  + '. User was added to specified groups.'
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)

        except Exception as e:
            print("Exception was found: " + str(e))
            response_data['DATA'] = str(e)
            
        
    
    
    if request_type == "Group":
        group_name = ""
        print("Not yet implemented!")

        cfnresponse.send(event, context, cfnresponse.FAILURE, response_data)
        # For now we will just implement Group
        
    

