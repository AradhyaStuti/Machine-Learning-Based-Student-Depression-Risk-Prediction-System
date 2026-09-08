# Student Depression Risk Prediction System

A machine learning application that predicts depression risk among students using academic, lifestyle, and personal factors.

I started this project by training and comparing different models. I then turned it into an application with a desktop GUI, a web interface, a REST API, prediction history, and Docker support.

> **Note:** This project is for educational purposes only. It is not a medical diagnostic tool.

## What it does

The system takes 10 student-related inputs and returns a predicted depression probability along with a risk category:

* Low Risk
* Moderate Risk
* High Risk

It also shows a short recommendation based on the predicted risk level.

## Input Features

| Feature            | Description                                   |
| ------------------ | --------------------------------------------- |
| Gender             | Male / Female                                 |
| Age                | Student age                                   |
| Work/Study Hours   | Daily study or work duration                  |
| Academic Pressure  | Academic stress level                         |
| Financial Stress   | Financial stress level                        |
| Study Satisfaction | Satisfaction with studies                     |
| Sleep Duration     | Average sleep duration                        |
| Dietary Habits     | Dietary habit category                        |
| Suicidal Thoughts  | Whether the student has had suicidal thoughts |
| Family History     | Family history of mental illness              |

## Machine Learning

I used **Logistic Regression** as a baseline and a small **PyTorch neural network** for comparison.

### Preprocessing

The data pipeline includes:

* One-hot encoding for categorical features
* Scaling of numerical features
* Interaction features
* Train-test splitting

### Neural Network

The neural network uses:

* Fully connected layers
* ReLU activation
* Dropout (0.3)
* Adam optimizer
* Learning-rate scheduling
* Early stopping

## Results

The models were evaluated on a held-out 20% test set.

| Metric   | Neural Network | Logistic Regression |
| -------- | -------------: | ------------------: |
| Accuracy |           0.85 |                0.85 |
| F1 Score |           0.87 |                0.87 |
| ROC-AUC  |           0.92 |                0.92 |

Both models produced almost identical results on this dataset. The neural network did not give a clear improvement over Logistic Regression, but I kept it to experiment with PyTorch and compare a neural network with a simpler baseline.

## Application

The project has both a **desktop application** and a **web application**.

### Desktop GUI

The desktop interface is built with **CustomTkinter**. It allows users to:

* Enter the student information
* Get a depression risk prediction
* View the predicted probability and risk category
* View the recommendation
* Access previous predictions

### Web Application

The web version uses **Gradio** for the user interface and **FastAPI** for the backend API.

The Gradio interface provides a browser-based form for entering the same student information and viewing the prediction.

The FastAPI service provides endpoints for:

* Health checks
* Predictions
* Prediction history
* API documentation

The API documentation is available through FastAPI's `/docs` endpoint when the application is running.

### Prediction History

Prediction history is stored locally using **SQLite**.

## Docker

The application can also be run in a Docker container.

The Docker setup packages the Python environment, application code, dataset, and saved model files together so the application can run in a consistent environment.

## Project Structure

```text
main.py
app.py
│
├── src/
│   ├── GUI.py              # Desktop interface
│   ├── api.py              # FastAPI endpoints
│   ├── config.py           # Application configuration
│   ├── database.py         # SQLite operations
│   ├── evaluate.py         # Model evaluation
│   ├── logging_config.py   # Logging setup
│   ├── model_definition.py # Model and prediction logic
│   └── validation.py       # Input validation
│
├── tests/                  # Automated tests
├── model_files/            # Saved model files
├── data/                   # Dataset
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Tech Stack

* **Python**
* **PyTorch**
* **Scikit-learn**
* **FastAPI**
* **Gradio**
* **CustomTkinter**
* **SQLite**
* **Docker**
* **Pytest**

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/AradhyaStuti/Machine-Learning-Based-Student-Depression-Risk-Prediction-System.git
cd Machine-Learning-Based-Student-Depression-Risk-Prediction-System
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the desktop application

```bash
python main.py
```

### 4. Run the web application

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

The Gradio interface will be available at:

```text
http://localhost:7860
```

FastAPI's interactive API documentation will be available at:

```text
http://localhost:7860/docs
```

### 5. Run with Docker

```bash
docker compose up --build
```

The web application will then be available through the port configured in `docker-compose.yml`.

## Dataset

The project uses the **Student Depression Dataset** from Kaggle, containing around 28,000 student records with demographic, academic, lifestyle, and mental-health-related features.

## Limitations

This model should not be used for clinical diagnosis or medical decision-making.

The model was trained on a specific dataset, so its performance may not generalize to other student populations or real-world clinical settings.

The recommendations displayed by the application are simple rule-based messages based on the predicted risk category.

## Author

**Aradhya Stuti**

GitHub: @AradhyaStuti
