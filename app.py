import streamlit as st
import numpy as np
import pickle
import base64
import pymysql
import pandas as pd

# Background Image

def get_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_img = get_base64("heart.png")

page_bg = f"""
<style>

.stApp {{
    background-image: url("data:image/png;base64,{bg_img}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
    right: 2rem;
}}

</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# MySQL Connection

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="Athul5555@",
    database="heart_db"
)

cursor = conn.cursor()

# Load Model

model = pickle.load(open("knn.save", "rb"))
scaler = pickle.load(open("sc (1).save", "rb"))

# Title

st.markdown(
    "<h1 style='color:black; text-align:center;'>Heart Disease Prediction</h1>",
    unsafe_allow_html=True
)

st.write("Enter Patient Details")

# Inputs

age = st.number_input("Age", 1, 100, 50)

sex = st.selectbox(
    "Sex",
    [0, 1],
    format_func=lambda x: "Female" if x == 0 else "Male"
)

cp = st.selectbox("Chest Pain Type", [0, 1, 2, 3])

trestbps = st.number_input(
    "Resting Blood Pressure",
    50,
    250,
    120
)

chol = st.number_input(
    "Cholesterol",
    100,
    600,
    200
)

fbs = st.selectbox(
    "Fasting Blood Sugar > 120",
    [0, 1]
)

restecg = st.selectbox(
    "Rest ECG",
    [0, 1, 2]
)

thalach = st.number_input(
    "Maximum Heart Rate",
    50,
    250,
    150
)

exang = st.selectbox(
    "Exercise Induced Angina",
    [0, 1]
)

oldpeak = st.number_input(
    "Old Peak",
    0.0,
    10.0,
    1.0
)

slope = st.selectbox(
    "Slope",
    [0, 1, 2]
)

ca = st.selectbox(
    "Number of Major Vessels",
    [0, 1, 2, 3, 4]
)

thal = st.selectbox(
    "Thal",
    [0, 1, 2, 3]
)

# Prediction

if st.button("Predict"):

    input_data = np.array([[
        age,
        sex,
        cp,
        trestbps,
        chol,
        fbs,
        restecg,
        thalach,
        exang,
        oldpeak,
        slope,
        ca,
        thal
    ]])

    # Scaling

    scaled_input = scaler.transform(input_data)

    # Prediction

    prediction = model.predict(scaled_input)

    # Result

    if prediction[0] == 1:
        result = "Heart Disease Detected"
        st.error(result)

    else:
        result = "No Heart Disease"
        st.success(result)

# Save Result to SQL

    query = """
    INSERT INTO predictions
    (
        age,
        sex,
        cp,
        trestbps,
        chol,
        fbs,
        restecg,
        thalach,
        exang,
        oldpeak,
        slope,
        ca,
        thal,
        result
    )

    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        age,
        sex,
        cp,
        trestbps,
        chol,
        fbs,
        restecg,
        thalach,
        exang,
        oldpeak,
        slope,
        ca,
        thal,
        result
    )

    cursor.execute(query, values)

    conn.commit()

    st.success("Prediction Saved Successfully")

# Show Saved Histories

if st.button("Show Saved Histories"):

    query = "SELECT * FROM predictions ORDER BY id DESC"

    df = pd.read_sql(query, conn)

    st.subheader("Prediction History")

    st.dataframe(df)

    # Total Records

    st.write("Total Records:", len(df))

    # Download CSV

    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download History CSV",
        csv,
        "prediction_history.csv",
        "text/csv"
    )

# Delete All Histories

if st.button("Delete All Histories"):

    cursor.execute("DELETE FROM predictions")

    conn.commit()

    st.warning("All Histories Deleted")

