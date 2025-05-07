import joblib
import numpy as np
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# Initialize the FastAPI app
app = FastAPI()
# Load the trained model
model = joblib.load("data/model.pkl")


# Define the request body structure
class PredictionRequest(BaseModel):
    article_text: str
    title: str


# Define the predict endpoint
@app.post("/predict")
def predict(request: PredictionRequest):
    # Extract the features from the request
    features = np.array([[request.article_text, request.title]])

    # Make a prediction using the model
    prediction = model.predict(features)

    # Return the prediction as a JSON response
    return {"Detailed_Sentiment": prediction[0]}


# Run the FastAPI app with Uvicorn

if __name__ == "__main__":
    # start the ASGI service
    host = "127.0.0.1"
    port = 8000
    uvicorn.run(app=app, host=host, port=port)
