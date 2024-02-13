from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pact import Consumer, Provider, Like, Format, Term
from pact.verify import ProviderVerifier

app = FastAPI()

# Mock database for storing employee details
employees_db = {}


class Employee(BaseModel):
    name: str
    age: int
    department: str


# Employee Service Endpoints
@app.post("/employees/create/")
async def create_employee(employee: Employee):
    employees_db[employee.name] = employee
    return {"message": f"Employee {employee.name} created successfully."}


@app.put("/employees/update/{name}/")
async def update_employee(name: str, employee: Employee):
    if name not in employees_db:
        raise HTTPException(status_code=404, detail=f"Employee {name} not found")
    employees_db[name] = employee
    return {"message": f"Employee {name} updated successfully."}


@app.get("/employees/{name}/")
async def get_employee(name: str):
    if name not in employees_db:
        raise HTTPException(status_code=404, detail=f"Employee {name} not found")
    return employees_db[name]


# Pact Contract Generation and Verification
consumer = Consumer("Dashboard")
provider = Provider("Employee", host_name="localhost", port=8000)

# Define the expected response format for Employee service
employee_response = {
    "name": Format("John"),
    "age": Like(30),
    "department": Term("IT", "IT|HR|Finance")
}

# Define the interactions for the contract
with consumer:
    with provider:
        (consumer
         .given("An employee exists")
         .upon_receiving("A request to get an employee")
         .with_request("GET", "/employees/John/")
         .will_respond_with(200, body=employee_response))

# Verify the contract
verifier = ProviderVerifier(provider=provider, provider_base_url="http://localhost:8000")


if _name_ == "_main_":
    import uvicorn
    verifier.verify()