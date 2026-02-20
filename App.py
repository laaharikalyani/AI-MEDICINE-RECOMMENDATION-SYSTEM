import streamlit as st
import base64
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os
import ast

# === Set up the page ===
st.set_page_config(page_title="Disease Prediction", layout="wide")

# === Add Custom CSS for Styling ===
st.markdown("""
    <style>
    /* Page Title Styling */
    .app-title {
        font-size: 2.5em;
        color: #00008B; /* Dark Blue color for elegance */
        text-align: center;
        font-weight: bold;
        margin-top: 20px;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); /* Subtle shadow for better contrast */
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #D8BFD8; /* Thistle background color */
        border-radius: 10px;
        padding: 15px;
    }
    .sidebar .sidebar-content h3 {
        color: #4B0082; /* Indigo heading text */
        font-weight: bold;
    }

    /* Button Styling */
    .stButton > button {
        font-size: 16px;
        font-weight: bold;
        color: white;
        background-color: #4B0082; /* Indigo button color */
        border-radius: 10px;
        padding: 12px;
        border: 2px solid #FFA500; /* Border color */
        transition: 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #FFA500; /* Orange on hover */
        color: white;
    }

    /* Section Headers */
    h3 {
        font-size: 1.8em;
        color: #4B0082;
        text-align: center;
        font-weight: bold;
    }

    /* Enlarged Text for Outputs */
    .large-text {
        font-size: 1.5em;
        color: #00008B; /* Deep Blue text */
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# === Helper Function to Set Background Dynamically ===
def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    css = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

def predict_disease(symptoms):
    input_data = [0] * len(X.columns)
    for i, col in enumerate(X.columns):
        if col.strip().lower() in [s.strip().lower() for s in symptoms]:
            input_data[i] = 1
    return model.predict([input_data])[0]

def get_info(disease):
    disease = disease.strip().lower()
    desc_row = description_df[description_df['Disease'].str.strip().str.lower() == disease]
    precaution_row = precautions_df[precautions_df['Disease'].str.strip().str.lower() == disease]
    diet_row = diets_df[diets_df['Disease'].str.strip().str.lower() == disease]
    meds_row = medications_df[medications_df['Disease'].str.strip().str.lower() == disease]

    desc = desc_row['Description'].values
    precaution = precaution_row.iloc[:, 1:].values.flatten() if not precaution_row.empty else []
    diet = diet_row.iloc[:, 1:].values.flatten() if not diet_row.empty else []
    meds = meds_row.iloc[:, 1:].values.flatten() if not meds_row.empty else []

    return {
        'Description': desc[0] if len(desc) > 0 else "No description available.",
        'Precautions': [str(item) for item in precaution if pd.notna(item)],
        'Diet': [str(item) for item in diet if pd.notna(item)],
        'Medications': [str(item) for item in meds if pd.notna(item)]
    }

# === Load Data ===
model_path = "medicine.pkl"
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    model = RandomForestClassifier(n_estimators=100, random_state=42)

training_df = pd.read_csv("Filtered_Training.csv")
description_df = pd.read_csv("description.csv")
precautions_df = pd.read_csv("precautions_df.csv")
diets_df = pd.read_csv("diets.csv")
medications_df = pd.read_csv("medications.csv")

X = training_df.drop(columns=['prognosis'])
y = training_df['prognosis']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# === Sidebar Navigation ===
menu = ["Home", "Predict Disease", "Medicines", "Diet", "Precautions", "Description"]
choice = st.sidebar.radio("Navigation Menu", menu)


# Page content based on the selected menu item
st.markdown("""
    <style>
    .app-title {
        font-size: 36px; /* Adjust font size if needed */
        color: black; /* Change text color to black */
        font-weight: bold; /* Makes the text bold */
        text-align: center; /* Centers the title */
    }
    </style>
    <div class="app-title">AI-Powered Disease Diagnosis and Medicine Recommendation System</div>
""", unsafe_allow_html=True)

# === Page Navigation Logic with Dynamic Background ===
if choice == "Home":
    set_background("Home_bg.jpeg")  # Replace with the image for the Home page
    st.markdown("<h3>Navigate through the menu to explore different features!</h3>", unsafe_allow_html=True)

elif choice == "Predict Disease":
    set_background("prediction_bg.jpg")  # Replace with the image for Predict Disease page
    st.title("Predict Your Disease")
    all_symptoms = list(X.columns)
    user_symptoms = st.multiselect("Select your symptoms", options=all_symptoms)

    if st.button("Predict Disease"):
        if not user_symptoms:
            st.error("Please select at least one symptom.")
        else:
            predicted_disease = predict_disease(user_symptoms)
            st.session_state.predicted_disease = predicted_disease
            st.markdown(f"<h3 class='large-text'>Predicted Disease: {predicted_disease}</h3>", unsafe_allow_html=True)

elif choice == "Medicines":
    set_background("medication_bg.jpg")  # Replace with the image for Medicines page
    st.title("Medicines for Your Predicted Disease")
    if 'predicted_disease' in st.session_state:
        predicted_disease = st.session_state.predicted_disease
        info = get_info(predicted_disease)

        # Clean conversion to a list of medications
        medications = eval(info['Medications'][0])  # Safely evaluate string to list
        
        # Display medications with increased font size and black color
        st.subheader("Medications:")
        for medication in medications:
            st.markdown(
                f"<p style='font-size:24px; color:black; font-weight:bold;'>&bull; {medication}</p>",
                unsafe_allow_html=True
            )  # Bullet point with larger font size and black color
    else:
        st.error("Please predict a disease first!")
elif choice == "Diet":
    set_background("diets_bg.jpg")  # Replace with the image for Diet page
    st.title("Recommended Diet")
    if 'predicted_disease' in st.session_state:
        predicted_disease = st.session_state.predicted_disease
        info = get_info(predicted_disease)

        # Clean conversion to a list of diet items
        diet_items = eval(info['Diet'][0])  # Safely evaluate string to list
        
        # Display diet items one by one with updated font size
        st.subheader("Recommended Diet:")
        for diet_item in diet_items:
            st.markdown(
                f"<p style='font-size:20px; color:black; font-weight:bold;'>&bull; {diet_item}</p>",
                unsafe_allow_html=True
            )  # Bullet point with reduced font size and black color
    else:
        st.error("Please predict a disease first!")

elif choice == "Precautions":
    set_background("precaution_bg.jpg")  # Replace with the image for Precautions page
    st.title("Precautions to Take")
    if 'predicted_disease' in st.session_state:
        predicted_disease = st.session_state.predicted_disease
        info = get_info(predicted_disease)

        # Display precautions one by one
        st.subheader("Precautions:")
        for precaution in info['Precautions']:
            st.markdown(
                f"<p style='font-size:20px; color:black; font-weight:bold;'>&bull; {precaution}</p>",
                unsafe_allow_html=True
            )  # Bullet point with styling similar to medications
    else:
        st.error("Please predict a disease first!")

elif choice == "Description":
    set_background("description_bg.jpg")  # Replace with the image for Description page
    st.title("Disease Description")
    if 'predicted_disease' in st.session_state:
        predicted_disease = st.session_state.predicted_disease
        info = get_info(predicted_disease)
        st.markdown(f"<h3 class='large-text'>Description: {info['Description']}</h3>", unsafe_allow_html=True)
    else:
        st.error("Please predict a disease first!")