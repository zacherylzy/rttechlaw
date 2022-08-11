import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
from csv import reader, writer
from pandas import DataFrame, ExcelWriter, read_csv
from copy import deepcopy
import altair as alt
from datetime import datetime as dt
from supabase import create_client, Client
from time import sleep
from math import ceil

@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = init_connection()

@st.experimental_memo(ttl=600)
def get_existing_users():
    return supabase.table("users").select("*").execute()

existing_users_rows = get_existing_users()

existing_users_names = []
existing_users_emails = []
existing_users_passwords = []
existing_users_types = []

for row in existing_users_rows.data:
    existing_users_names.append(row['name'])
    existing_users_emails.append(row['email'])
    existing_users_passwords.append(row['password'])
    existing_users_types.append(row['user_type'])

def createNewUser():
    insertNewUser_heading = st.empty()
    insertNewUser_heading_show = insertNewUser_heading.subheader("Create User")
    user_name = st.text_input("Name")
    user_email = st.text_input("Email")
    user_type = st.selectbox("User Type", ["user", "admin"])
    user_password = st.text_input("Password", type = "password")
    user_confirm_password = st.text_input("Confirm Password", type = "password")
    submit_button = st.button("Create User")
    not_filled_error = st.empty()
    name_error = st.empty()
    email_error = st.empty()
    password_error = st.empty()
    passwords_not_match = st.empty()
    create_success = st.empty()
    if submit_button:
        if user_name == "" or user_email == "" or user_password == "":
            not_filled_error_show = not_filled_error.markdown("Please fill in the User's Name, Email and/or Password.")
        else:
            not_filled_error.empty()
            if user_password != user_confirm_password:
                passwords_not_match_show = passwords_not_match.markdown("Please ensure Password and Confirm Password match.")
            else:
                passwords_not_match.empty()
                name_in = False
                for name in existing_users_names:
                    if name.lower() == user_name.lower():
                        name_in = True
                        break
                email_in = False
                for email in existing_users_emails:
                    if email.lower() == user_email.lower():
                        email_in = True
                        break
                password_in = False
                for password in existing_users_passwords:
                    if password == user_confirm_password:
                        password_in = True
                        break
                if name_in == True or email_in == True or password_in == True:
                    if name_in == True:
                        name_error_show = name_error.markdown("This Name has already been signed up.")
                    else:
                        name_error.empty()
                    if email_in == True:
                        email_error_show = email_error.markdown("This Email has already been signed up.")
                    else:
                        email_error.empty()
                    if password_in == True:
                        password_error_show = password_error.markdown("This Password has already been signed up.")
                    else:
                        password_error.empty()
                else:
                    create_success_show = create_success.markdown("The User has been created successfully.")
                    return supabase.table("users").insert({'name': user_name, 'email': user_email, 'password': user_confirm_password, 'user_type': user_type}).execute()
    return

st.title("Welcome to R&TT's Inventory Management System")
st.write("This can only be accessed by an Admin.")

# Key page
key_heading = st.empty()
key_heading_show = key_heading.subheader("Admin Home Login")
key_input = st.empty()
key_input_show = key_input.text_input("Key", type = "password")

if key_input_show:
    admin_passwords = []
    for i in range(len(existing_users_passwords)):
        if existing_users_types[i] == "admin":
            admin_passwords.append(existing_users_passwords[i])
    key_error = st.empty()
    if key_input_show in admin_passwords:
        key_heading.empty()
        key_input.empty()
        key_error.empty()
        createNewUser()
    else:
        key_error_show = key_error.markdown("You have entered an incorrect Key.")