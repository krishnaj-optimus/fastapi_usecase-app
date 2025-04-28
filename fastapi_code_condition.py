from fastapi import FastAPI, Request, Response

app = FastAPI()

@app.post("/assign-role")
async def assign_role(request: Request):
    # Get the plain text data from the request body
    data = await request.body()  # Get raw byte data from the body
    filename = data.decode("utf-8")  # Decode the byte data to a string (UTF-8)

    # Determine the role based on the filename
    role = "user" if filename == "user.pdf" else "group"
    
    # Return the role as a plain string response
    return Response(role, media_type="text/plain")  # Return plain text response

