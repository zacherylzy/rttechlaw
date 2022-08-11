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

def get_existing_devices():
    return supabase.table("devices").select("*").execute()

existing_devices_rows = get_existing_devices()

existing_devices = []

for row in existing_devices_rows.data:
    existing_devices.append(row)

def get_existing_assignments():
    return supabase.table("assignments").select("*").execute()

existing_assignments_rows = get_existing_assignments()

existing_assignments = []

for row in existing_assignments_rows.data:
    existing_assignments.append(row)

def endAssg(admin_user_name):
    endAssg_heading = st.empty()
    endAssg_heading_show = endAssg_heading.subheader("End Assignment")
    current_assignments = []
    current_assignments_all = []
    current_assignments_rows = []
    for row in existing_assignments:
        if row['assigned_current']:
            current_assignments.append([row['device_no'], row['device_type'], row['assigned_to'], row['assigned_from'], row['assigned_till'], row['assigned_current'], row['assigned_by']])
            current_assignments_all.append([row['id'], row['created_at'], row['device_no'], row['device_type'], row['assigned_to'], row['assigned_from'], row['assigned_till'], row['assigned_current'], row['assigned_by']])
    df_actual = pd.DataFrame(current_assignments, columns = ["Device No.", "Device Type", "Assigned To", "Assigned From", "Assigned Till", "Current Assignment", "Assigned By"])
    st.dataframe(df_actual)
    for row in current_assignments:
        current_assignments_rows.append(row)
    print(current_assignments)
    current_assignments_rows_strings = []
    for row in current_assignments_rows:
        row_string = ""
        row_string = str(row[0]) + ", " + str(row[1]) + ", " + str(row[2]) + ", " + str(row[3]) + ", " + str(row[4]) + ", " + str(row[6])
        current_assignments_rows_strings.append(row_string)
    current_assignments_rows_strings = ["Please select"] + current_assignments_rows_strings
    select_current_assg = st.selectbox("Select Current Assignment", current_assignments_rows_strings)
    select_assigned_till = st.date_input("Assigned Till")
    end_assg_button = st.button("End Assignment")
    no_fill_error = st.empty()
    till_more_from = st.empty()
    success_end_assg = st.empty()
    if end_assg_button:
        if select_current_assg == "Please select":
            no_fill_error_show = no_fill_error.markdown("Please select Current Assignment.")
        else:
            no_fill_error.empty()
            current_assigned_from = dt.strptime(select_current_assg.split(", ")[3], '%Y-%m-%d')
            if current_assigned_from > dt.strptime(str(select_assigned_till), '%Y-%m-%d'):
                till_more_from_show = till_more_from.markdown("Assigned From should be less than or equal to Assigned Till.")
            else:
                till_more_from.empty()
                current_row_index = current_assignments_rows_strings.index(select_current_assg) - 1
                current_row = current_assignments_all[current_row_index]
                success_end_assg_show = success_end_assg.markdown("This assignment has been successfully ended.")
                return supabase.table("assignments").update({
                    'assigned_till': str(select_assigned_till),
                    'assigned_current': False
                }).match({'id': current_row[0]}).execute()

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
        admin_user_name = existing_users_names[existing_users_passwords.index(key_input_show)]
        endAssg(admin_user_name)
    else:
        key_error_show = key_error.markdown("You have entered an incorrect Key.")