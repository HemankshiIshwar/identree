# Identree - Tree Identification Web App

**Identree** is a web application that allows users to identify tree species based on images of their leaves. It utilizes a pre-trained machine learning model (CNNs) to provide accurate identifications along with confidence scores. Additionally, the app offers various features for user interaction and engagement.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Database](#database)
- [Acknowledgments](#acknowledgments)

## Features

- **Leaf Identification:** Upload an image of a leaf, and the app will identify the tree species with a confidence score.
- **Related Links:** Get links to Wikipedia for more information about the identified tree species and shop for tree saplings.
- **Location Mapping:** Locate the identified tree species on a map.
- **Profile** Acces the user profile after registration.
- **Tree Trivia:** Enjoy the fun trivia about trees and score up!
- **My Diary:** Keep a record of the identifications on the app.
- **Share with a friend** Send an email about the identified tree to a friend.

## Installation

To set up the Identree web app locally, follow these steps:

1. **Setup the Repository:** Clone the Identree repository from GitHub to your local machine. Open a terminal/command prompt and run:
```
git clone https://github.com/HemankshiIshwar/identree.git
cd identree
```
2. **Create a Virtual Environment:** It's recommended to use a virtual environment to manage project dependencies.

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```
   pip install -r requirements.txt
   ```

4. **Database Setup:** Create and configure the database. You can do this by setting up your database connection in the app configuration. Update the file with your database credentials.

5. **Model Setup:** Place the trained model file (model.h5) in the `model` folder.

6. **Run the Application:**

   ```
   python identree-app.py
   ```

   The app should now be running locally at `http://localhost:9000`.

## Usage

1. Open your web browser and go to `http://localhost:9000`.
2. Upload an image of a tree leaf for identification.
3. Wait for the identification results along with a confidence score.
4. Explore the related links, animation, and mapping options for more engagement.

## Folder Structure

- **templates:** Contains HTML files used for rendering web pages.
- **static:** Contains CSS, JavaScript, and image files used for styling and interactivity.
- **model:** Place the trained machine learning model (model.h5) in this folder.
- **database:** Contains the database setup scripts and models for users, user activity, questions, and answers.
- **app.py:** The main Flask application file.
- **config.py:** Configuration settings for the application.

## Database

The Identree web app uses a database to store user information and activity. You can set up and configure the database according to your requirements. Refer to the database folder for scripts and models related to the database structure.

## Acknowledgments

- **Flask:** The web framework used for building the application.
- **TensorFlow:** The machine learning framework used for the leaf identification model.
- **Leaf image dataset:** The dataset used to train the machine learning model (cite the source if necessary).
- **OpenStreetMap:** Used for mapping tree locations.
- **Wikipedia API:** Used for retrieving information about tree species.
