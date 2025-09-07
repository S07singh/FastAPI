from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Patient Management System API is running."}

@app.get('/about')
def about():
    return {"message": "A fully functional Patient Management System API built with FastAPI."}

def load_data():
    with open('patients.json', 'r') as file:
        data = json.load(file)
    return data

@app.get('/view')
def view_patients():
    data = load_data()
    return data

@app.get('/view/{patient_id}')
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    # return {"error": "Patient not found"} # instead of this json error we can use custom error
    # where we can define status_code
    raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description="Sort patients by 'height', 'weight' or 'bmi'"), order: str = Query('asc', description="Order of sorting: 'asc' for ascending, 'desc' for descending")):
    data = load_data()
    valid_sort_keys = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_sort_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by value. Must be one of {valid_sort_keys}")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order value. Must be 'asc' or 'desc'")
    
    data = load_data()
    reverse = True if order == 'desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=reverse)

    return sorted_data
# To run the application, use the command:
# uvicorn main:app --reload