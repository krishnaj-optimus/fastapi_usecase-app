from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import os
import requests
from dotenv import load_dotenv


# Load variables from .env file
load_dotenv()

# Replace with your actual Azure Search details
AI_SEARCH_URL = os.getenv('AI_SEARCH_URL')  # e.g. "my-search-service"
AI_SEARCH_API_KEY = os.getenv('AI_SEARCH_API_KEY')  # Azure Search admin API key

# Replace with your Azure AD app registration details
CLIENT_ID = "1cea657c-c9d0-4b4c-a4a1-a89d3afe2db4"
CLIENT_SECRET = "1mV8Q~Tk3DxcamnEssvhBwRI~V20gOM1p2aMYcsL"
TENANT_ID = "b5db11ac-8f37-4109-a146-5d7a302f5881"
SHAREPOINT_SITE_URL='https://optimusinfo.sharepoint.com/sites/USECASE_SHAREPOINT'
GRAPH_API = 'https://graph.microsoft.com/v1.0'
SITE_NAME ='USECASE_SHAREPOINT'
SHAREPOINT_DOMAIN = 'optimusinfo.sharepoint.com'

app = FastAPI()

def get_access_token():

    # Microsoft Graph scope
    scope = 'https://graph.microsoft.com/.default'

    # OAuth 2.0 token endpoint
    token_url = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'

    # Prepare request headers and body
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': scope
    }

    # Send the POST request
    response = requests.post(token_url, headers=headers, data=data)

    # Handle the response
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    else:
        raise Exception("access token request failed.")
        
    

def get_site_id(token):
    
    url = f"{GRAPH_API}/sites/{SHAREPOINT_DOMAIN}:/sites/{SITE_NAME}"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
      
        site_id=response.json()['id']
        return site_id
    else:
        raise Exception("Site ID request failed.")
    
def get_drive_id(site_id, token):
    url = f"{GRAPH_API}/sites/{site_id}/drives"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        
        drives = response.json().get('value', [])

        for drive in drives:
           
            if drive['name'] == 'Documents':
                return drive['id']  # ⬅ pick by name
            
        return drives[0]['id'] if drives else None
    else:
        raise Exception("Drive ID request failed.")


def get_permissions(item_id: str,drive_id: str, access_token: str):
    url = f"{GRAPH_API}/drives/{drive_id}/items/{item_id}/permissions"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("value", [])
    else:
         raise Exception("permission request failed.")




@app.post("/assign-role")
async def assign_role(request: Request):
    # # Get the JSON data from the request body
    # input_data = await request.json()  # Parse the JSON data

    # # Initialize an empty list to store output values
    # output_values = []

    # # Iterate over each input item
    # for item in input_data.get('values', []):
    #     record_id = item.get('recordId')  # Get the recordId from input
    #     data = item.get('data', {})  # Get data for each entry

    #     # Extract filename (metadata_spo_item_name) from the input
    #     filename = data.get('metadata_spo_item_name', '')

    #     # Determine the role based on the filename
    #     role = "user" if filename == "user.pdf" else "group"

    #     # Construct the output format
    #     output_values.append({
    #         "recordId": record_id,
    #         "data": {
    #             "role": role
    #         },
    #         "errors": [],
    #         "warnings": []
    #     })
    
    # # Return the response in the expected format with the 'values' field
    # return JSONResponse(content={"values": output_values})

    ####......above commented code is used to extrace role based on file name.....


    
   
    input_data = await request.json()
   

      # Initialize an empty list to store output values
    output_values = []

    # Iterate over each input item
    for item in input_data.get('values', []):
        record_id = item.get('recordId')  # Get the recordId from input
        data = item.get('data', {})  # Get data for each entry

         # Get the recordId from input
        # Get data for each entry
      
        # Extract filename (metadata_spo_item_name) from the input
        item_id = data.get('metadata_spo_item_id', '')

       

        access_token=get_access_token()
        site_id=get_site_id(access_token)
        drive_id=get_drive_id(site_id,access_token)
        permission=get_permissions(item_id,drive_id,access_token)

        # List to store email addresses
        emails = []

        # Loop through the 'value' key and check if 'email' exists in the nested dictionary
        for item in permission:
            # Check if the 'email' field exists in the user details
            if 'grantedToV2' in item and 'user' in item['grantedToV2'] and 'email' in item['grantedToV2']['user']:
                emails.append(item['grantedToV2']['user']['email'])
            elif 'grantedTo' in item and 'user' in item['grantedTo'] and 'email' in item['grantedTo']['user']:
                emails.append(item['grantedTo']['user']['email'])

            # Construct the output format
        output_values.append({
                "recordId": record_id,
                "data": {
                    "role": emails
                },
                "errors": [],
                "warnings": []
            })
    
    # Return the response in the expected format with the 'values' field
    return JSONResponse(content={"values": output_values})