from fastapi import FastAPI
from .routers import report_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Origins that are allowed to make requests
    allow_origins=["*"],  # Allow all origins (you can specify specific origins like ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


app.include_router(report_router, prefix="/api")

@app.get("/")
def read_root():

    return {
        "name": "ASL Methods Parameter Generator API Service",
        "version": "0.0.1",
        "description": "This service provides an API for generating ASL methods parameters based on user input. "
                       "It is designed to be used in conjunction with the ASL Methods Parameter Generator frontend application.",
        "organization": "The ISMRM Open Science Initiative for Perfusion Imaging",
        "authors": [
            {"Ibrahim Abdelazim": "ibrahim.abdelazim@fau.de" },
            {"Hanliang Xu": "hxu110@jh.edu"}
        ],
        "supervisors": [
            "Jan Petr",
            "David Thomas",
        ],
        "Specs": {
            "Programming Language": "Python",
            "Framework": "FastAPI",
            "Operating System": "OS Independent",
        },
        "license": "MIT",
    }

