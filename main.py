from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the patient resides")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal['Male', 'Female', 'Other'], Field(..., description="Height of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in mtrs")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kg")]

    @computed_field
    @property
    def bmi(self) -> float:
        height_in_meters = self.height / 100
        return round(self.weight / (height_in_meters** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None)]
    gender: Annotated[Optional[Literal['Male', 'Female', 'Other']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None)]
    weight: Annotated[Optional[float], Field(default=None)]
        
def load_data():
    with open('patients.json', 'r') as file:
        data = json.load(file)
    return data

def save_data(data):
    with open('patients.json', 'w') as file:
        json.dump(data, file, indent=4)

@app.get("/")
def hello():
    return {"message": "Patient Management System API is running."}

@app.get('/about')
def about():
    return {"message": "A fully functional Patient Management System API built with FastAPI."}



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

@app.post('/create')
def create_patient(patient: Patient):
    # Load existing data
    data = load_data()
    # Check if patient with same ID already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists.")
    
    # new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    # Save updated data back to the  json file
    save_data(data) 
    
    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})

@app.put('/update/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found!")
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value
    
    # existing_patient_info -> pydantic object -> update bmi + verdict -> pydantic object -> dict
    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted successfully'})

# To run the application, use the command:
# uvicorn main:app --reload