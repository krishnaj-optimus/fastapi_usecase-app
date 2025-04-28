from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/assign-role")
async def assign_role(request: Request):
    # Get the JSON data from the request body
    input_data = await request.json()  # Parse the JSON data

    # Initialize an empty list to store output values
    output_values = []

    # Iterate over each input item
    for item in input_data.get('values', []):
        record_id = item.get('recordId')  # Get the recordId from input
        data = item.get('data', {})  # Get data for each entry

        # Extract filename (metadata_spo_item_name) from the input
        filename = data.get('metadata_spo_item_name', '')

        # Determine the role based on the filename
        role = "user" if filename == "user.pdf" else "group"

        # Construct the output format
        output_values.append({
            "recordId": record_id,
            "data": {
                "role": role
            },
            "errors": [],
            "warnings": []
        })
    
    # Return the response in the expected format with the 'values' field
    return JSONResponse(content={"values": output_values})

