# Earthquake Prediction System

# Overview

The Earthquake Prediction System is a web-based application built with Django to predict earthquake metrics and visualize seismic data. Users can input earthquake details (latitude, longitude, magnitude, depth), generate predictions using a machine learning model, visualize results through interactive graphs (Chart.js) and maps (Leaflet), and export data as PDF reports. This project aims to enhance disaster risk reduction by providing actionable insights for communities and authorities in earthquake-prone regions.
Developed by: CHOGE VINCENTDate: May 14, 2025Technologies: Python, Django, HTML, JavaScript, Chart.js, Leaflet, NumPy, scikit-learn, geopy, reportlab

# Features

Data Input: Users can input earthquake data (latitude, longitude, magnitude, depth).

Prediction: Predicts earthquake magnitude using a linear regression model.

Visualization: Displays results with bar graphs (magnitude, confidence, probability, accuracy) and real-world maps.

PDF Export: Generates landscape PDF reports of prediction data.

Admin Interface: Allows deletion of records for data management.

Alignment: Supports disaster risk reduction goals (Sendai Framework, SDG 11).

# Prerequisites

Before running the project, ensure you have the following installed:

Python 3.13.2 or higher
pip (Python package manager)
Git (optional, for cloning the repository)
A web browser (e.g., Chrome, Firefox)


# Installation

Clone the Repository:
git clone https://github.com/yourusername/earthquake-prediction-system.git
cd earthquake-prediction-system


Replace yourusername with your GitHub username.

Set Up a Virtual Environment:
python -m venv env
source env/Scripts/activate  # On Windows

# OR
source env/bin/activate     # On macOS/Linux


# Install Dependencies:

pip install django==5.2 numpy scikit-learn geopy reportlab


Apply Database Migrations:
python manage.py makemigrations
python manage.py migrate


Run the Development Server:
python manage.py runserver


Access the app at http://127.0.0.1:8000/.



# Usage

Home Page: Visit http://127.0.0.1:8000/ to explore the application and navigate to key features.
Make a Prediction:
Go to http://127.0.0.1:8000/predict/.
Enter earthquake data (e.g., Latitude: 34.05 N, Longitude: 118.24 W, Magnitude: 5.0, Depth: 10).
Click "Predict" to view the predicted magnitude, confidence, probability, accuracy, and location on a map.


View Dashboard: Access http://127.0.0.1:8000/dashboard/ to see all recorded earthquakes and predictions with a map.
Download PDF: Navigate to http://127.0.0.1:8000/download_pdf/ to download a PDF report of all predictions.
Admin Interface: Visit http://127.0.0.1:8000/admin_dashboard/ to manage and delete records.

# Project Structure

earthquake_project/: Main Django project directory.

earthquake/: App containing models, views, and templates.

models.py: Defines Earthquake and Prediction models.

views.py: Handles logic for prediction, visualization, and PDF generation.

templates/: HTML templates for rendering pages.


manage.py: Django management script.


README.md: Project documentation.
.gitignore: Excludes unnecessary files (e.g., virtual environment, database).

Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).

Make your changes and commit (git commit -m "Add your feature").

Push to your branch (git push origin feature/your-feature).

Open a Pull Request on GitHub.

Please ensure your code follows PEP 8 standards and includes appropriate comments.
Future Enhancements

Integrate real-time seismic data (e.g., USGS API).

Implement advanced machine learning models (e.g., deep learning).

Develop a mobile application for broader accessibility.

Add multi-language support for global users.


# Contact
For questions, support, or collaboration, contact:  

Name: CHOGE VINCENT  
Email: vincentchoge71@gmail.com  
Telephone: +254 726 390 388

