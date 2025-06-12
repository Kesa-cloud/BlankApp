# Module used in loading pre trained modules
import pickle

# For numerical ops
import numpy as np

# For creating the web app
import streamlit as st

# Loading the pre trained module we were given
model = pickle.load(open('model.pkl', 'rb'))

#Centering the title
col0, col1, col2, col3, col4, col5, col6 = st.columns(7)
with col0:
    st.write('')
with col1:
    st.write('')
with col2:
    st.write('')    
with col3:
    st.title("Salary") # Title of the app
with col4:
    st.write('')
with col5:
    st.write('')
with col6:
    st.write('')

# Centering the description of the app
col7, col8, col9 = st.columns(3)
with col7:
    st.write('')    
with col8:
    st.markdown("<h6 style='text-align: center;'>A simple web app to predict annual salary</h6>", unsafe_allow_html=True)
with col9:
    st.write('')

# Input options for the user
gen_list = ["Female", "Male"] # Lists the Gender/Sex options
edu_list = ["Bachelor's", "Master's", "PhD"] # Lists the Education levels
job_list = ["Director of Marketing", "Director of Operations", "Senior Data Scientist", "Senior Financial Analyst", "Senior Software Engineer"] # Lists the Job titles/ positions
job_idx = [0, 1, 10, 11, 20]# Encoded job indexes for prediction

# Input fields for the user i.e, prompts
gender = st.radio('Choose your gender', gen_list) # Choose between male and female
age = st.slider('Choose your age', 21, 70) # Age range from 21 to 70 using a slider
education = st.selectbox('Choose your education level', edu_list) # Choose between Bachelor's, Master's, and PhD
job = st.selectbox('Choose your job title', job_list) # Choose between different job titles
experience = st.slider('Input your years of experience', 0.0, 25.0, 0.0, 0.5, "%1f") # Years of experience using a slider

# Centering the predict button
col10, col11, col12, col13, col14 = st.columns(5)
with col10:
    st.write('')
with col11:
    st.write('')    
with col12:
    predict_btn = st.button('Predict Salary') # Button that triggers prediction
with col13:
    st.write('')
with col14:
    st.write('')


if(predict_btn):
    inp1 = int(age) # Converts age to integer
    inp2 = float(experience) # Converts experience to float
    inp3 = int(job_idx[job_list.index(job)]) # Gets the index of the job title in numerical form
    inp4 = int(edu_list.index(education)) # Gets the index of the education level in numerical form
    inp5 = int(gen_list.index(gender)) # Get the index of the gender in numerical form
    X = [inp1, inp2, inp3, inp4, inp5] # Formating input data as a list
    salary = model.predict([X]) # Predicting the salary using the model
    
    # Centering the estimated salary
    col15, col16, col17 = st.columns(3) 
    with col15:
        st.write('')    
    with col16:
        st.text(f"Estimated salary: ${int(salary[0])}") # Displaying the estimated salary
    with col17:
        st.write('') 
