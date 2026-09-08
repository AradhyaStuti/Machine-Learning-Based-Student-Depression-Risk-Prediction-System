# Student Depression Risk Prediction System

<<<<<<< HEAD
A machine learning application that predicts depression risk among students using academic, lifestyle, and personal factors.

I initially focused on training and evaluating the models, then extended the project into a small application with a desktop interface, REST API, prediction history, and Docker support.
=========================================================================================================================================================================================

A machine learning project that predicts depression risk among students using academic, lifestyle, and personal factors.

I started this project by training and comparing the models and later added a desktop application, web interface, REST API, prediction history, and Docker support.

>>>>>>> 2592015 (changed docker and update README)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

> **Note:** This project is for educational purposes only. It is not a medical diagnostic tool.

## What it does

## Input Features

The model uses the following inputs:

| Feature            | Description                      |
| ------------------ | -------------------------------- |
| Gender             | Male / Female                    |
| Age                | Student age                      |
| Work/Study Hours   | Daily study duration             |
| Academic Pressure  | Academic stress level            |
| Financial Stress   | Financial stress level           |
| Study Satisfaction | Satisfaction with studies        |
| Sleep Duration     | Average sleep duration           |
| Dietary Habits     | Quality of dietary habits        |
| Suicidal Thoughts  | Presence of suicidal thoughts    |
| Family History     | Family history of mental illness |

## Machine Learning

I used Logistic Regression as a baseline and a small PyTorch neural network for comparison.

### Preprocessing

The data pipeline includes:

* One-hot encoding for categorical features
* Scaling of numerical features
* Interaction features
* Train-test splitting

### Neural Network

The neural network uses:

=======
A short recommendation is also shown based on the predicted risk level.

## Input Features

| Feature            | Description                                   |
| ------------------ | --------------------------------------------- |
| Gender             | Male / Female                                 |
| Age                | Student age                                   |
| Work/Study Hours   | Daily study duration                          |
| Academic Pressure  | Academic stress level                         |
| Financial Stress   | Financial stress level                        |
| Study Satisfaction | Satisfaction with studies                     |
| Sleep Duration     | Average sleep duration                        |
| Dietary Habits     | Dietary habits                                |
| Suicidal Thoughts  | Whether the student has had suicidal thoughts |
| Family History     | Family history of mental illness              |

## Machine Learning

I used **Logistic Regression** as a baseline and a small **PyTorch neural network** to compare the results.

### Preprocessing

* One-hot encoding for categorical features
* Scaling of numerical features
* Interaction features
* Train-test split

### Neural Network

>>>>>>> 2592015 (changed docker and update README)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

* Fully connected layers
* ReLU activation
* Dropout (0.3)
* Adam optimizer
* Learning-rate scheduling
* Early stopping

## Results

<<<<<<< HEAD
The models were evaluated on a held-out 20% test set.
=====================================================

The models were tested on 20% of the dataset.

>>>>>>> 2592015 (changed docker and update README)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

| Metric   | Neural Network | Logistic Regression |
| -------- | -------------: | ------------------: |
| Accuracy |           0.85 |                0.85 |
| F1 Score |           0.87 |                0.87 |
| ROC-AUC  |           0.92 |                0.92 |

<<<<<<< HEAD
Both models gave almost identical results, so the neural network did not offer a clear advantage over Logistic Regression on this dataset. I kept the neural network as part of the project to experiment with PyTorch and compare it with a simpler baseline.

## Application

The trained model is connected to a desktop application built with CustomTkinter.

The application allows users to:

* Enter the required student information
* Get a depression risk prediction
* View the predicted probability and risk category
* View the recommendation associated with the result
* Access previous predictions

The project also includes a FastAPI service that exposes the prediction functionality through a REST API.

Prediction history is stored locally using SQLite.
==================================================

Both models gave almost the same results. The neural network did not perform better than Logistic Regression on this dataset, but I kept it to compare the two approaches and get some hands-on experience with PyTorch.

## Application

The project has a desktop application as well as a web version.

### Desktop Application

The desktop GUI is made using  **CustomTkinter** .

It allows users to:

* Enter the required student information
* Get a depression risk prediction
* See the predicted probability and risk category
* See the recommendation
* View previous predictions

### Web Application

The web interface is made using **Gradio** and the API is handled using  **FastAPI** .

The Gradio interface provides a simple form where users can enter the student details and get the prediction in the browser.

The FastAPI application provides endpoints for:

* Health check
* Prediction
* Previous predictions
* API documentation

### Prediction History

Prediction history is stored locally using  **SQLite** .

>>>>>>> 2592015 (changed docker and update README)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

## Project Structure

```text
main.py
<<<<<<< HEAD
=======
app.py
>>>>>>> 2592015 (changed docker and update README)
│
├── src/
│   ├── GUI.py              # Desktop interface
│   ├── api.py              # FastAPI application
│   ├── config.py           # Configuration
│   ├── database.py         # SQLite operations
<<<<<<< HEAD
│   ├── evaluate.py         # Model evaluation and comparison
│   ├── logging_config.py   # Logging setup
│   ├── model_definition.py # Neural network and training
│   └── validation.py       # Input validation
│
├── tests/                  # Project tests
=======
│   ├── evaluate.py         # Model evaluation
│   ├── logging_config.py   # Logging setup
│   ├── model_definition.py # Model and prediction logic
│   └── validation.py       # Input validation
│
├── tests/                  # Tests
>>>>>>> 2592015 (changed docker and update README)
├── model_files/            # Saved model files
├── data/                   # Dataset
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Tech Stack

<<<<<<< HEAD

* **Python**
* **PyTorch**
* **Scikit-learn**
* **FastAPI**
* **CustomTkinter**
* **SQLite**
* **Docker**

## Running the Project

Clone the repository:

```bash
git clone https://github.com/AradhyaStuti/Machine-Learning-Based-Student-Depression-Risk-Prediction-System.git
cd Machine-Learning-Based-Student-Depression-Risk-Prediction-System
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the desktop application:
============================

* Python
* PyTorch
* Scikit-learn
* FastAPI
* Gradio
* CustomTkinter
* SQLite
* Docker
* Pytest

## Running the Project

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the desktop application

>>>>>>> 2592015 (changed docker and update README)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

```bash
python main.py
```

<<<<<<< HEAD
<<<<<<< HEAD
The API can be run separately using the FastAPI application in `src/api.py`.

## Dataset

=======

## Run the API

>>>>>>> 67625b9 (remove all history and database code, predict-only)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

The project uses the Student Depression Dataset from Kaggle, with around 28,000 student records covering demographic, academic, lifestyle, and mental-health-related factors.

## Limitations

<<<<<<< HEAD
This model should not be used as a clinical diagnosis. It was trained on a specific dataset, so its performance may not generalize to different student populations or real-world clinical settings.

The recommendations shown by the application are simple rule-based messages based on the predicted risk category.
=================================================================================================================

- `GET /health` — health check (also reports if the model file is on disk)
- `POST /predict` — run a prediction

Example request:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Male",
    "age": 22,
    "study_hours": 8,
    "academic_pressure": 4,
    "financial_stress": 3,
    "study_satisfaction": 2,
    "sleep_duration": "5-6 hours",
    "dietary_habits": "Moderate",
    "suicidal_thoughts": "No",
    "family_history": "No"
  }'
=======
### Run the web application

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

The web interface will be available at:

```text
http://localhost:7860
>>>>>>> 2592015 (changed docker and update README)
```

FastAPI documentation:

```text
http://localhost:7860/docs
```

### Run using Docker

```bash
docker compose up --build
```

## Dataset

The project uses the **Student Depression Dataset** from Kaggle, with around 28,000 student records.

The dataset contains demographic, academic, lifestyle, and mental-health-related information.

## Limitations

This project is only for learning and demonstration purposes and should not be used as a clinical diagnosis.

The model was trained on one dataset, so the results may not work the same way for other student groups or real-world clinical data.

<<<<<<< HEAD

## Project layout

```
main.py               launches the GUI
src/
  GUI.py              desktop UI (customtkinter)
  api.py              FastAPI app
  config.py           paths, dataset columns, training settings
  evaluate.py         model metrics + LR baseline
  logging_config.py   basic logging
  model_definition.py PyTorch model, training loop, and predict()
  validation.py       input validation for the GUI
tests/
model_files/          saved model, encoder, scaler
data/                 dataset
```

>>>>>>> 67625b9 (remove all history and database code, predict-only)
>>>>>>> =======
>>>>>>> The recommendations shown by the application are simple rule-based messages based on the predicted risk category.
>>>>>>> 2592015 (changed docker and update README)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

## Author

**Aradhya Stuti**

<<<<<<< HEAD
GitHub: [@AradhyaStuti](https://github.com/AradhyaStuti)
=====================

GitHub: @AradhyaStuti

>>>>>>> 2592015 (changed docker and update README)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>
