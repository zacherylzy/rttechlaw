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
def get_assignments():
    return supabase.table("assignments").select("*").execute()

existing_assignments_rows = get_assignments()

existing_assignments = []

for row in existing_assignments_rows.data:
    existing_assignments.append([row['device_no'], row['device_type'], row['assigned_to'], row['assigned_from'], row['assigned_till'], row['assigned_current'], row['assigned_by']])

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
    existing_devices.append([row['device_no'], row['device_type'], row['purchase_date'], row['price']])

def insert_new_user(name, email, password):
    return supabase.table("users").insert({'name': name, 'email': email, 'password': password, 'user_type': 'user'}).execute()

st.title("Welcome to R&TT's Inventory Management System")
st.write("This can only be accessed by an Admin.")

def viewAssg():
    viewAssg_heading = st.empty()
    viewAssg_heading_show = viewAssg_heading.subheader("View All Assignments")
    existing_assignments_df = st.empty()
    existing_assignments_df_actual = pd.DataFrame(existing_assignments, columns = ["Device No.", "Device Type", "Assigned To", "Assigned From", "Assigned Till", "Current Assignment", "Assigned By"])
    existing_assignments_df_show = existing_assignments_df.dataframe(existing_assignments_df_actual)
    return

def searchByUsers():
    searchByUsers_heading = st.empty()
    searchByUsers_heading_show = searchByUsers_heading.subheader("Search Assignments by Users")
    df = pd.DataFrame(existing_assignments, columns = ["Device No.", "Device Type", "Assigned To", "Assigned From", "Assigned Till", "Current Assignment", "Assigned By"])
    users = df['Assigned To'].drop_duplicates()
    users = ["Please select"] + list(users)
    current = df['Current Assignment'].drop_duplicates()
    current = ["Please select"] + list(current)
    user_choice = st.selectbox("Select User", users)
    current_choice = st.selectbox("Select Current Assignment", current)
    results_text = st.empty()
    results_df = st.empty()
    if user_choice != "Please select":
        results = []
        if current_choice == "Please select":
            for row in existing_assignments:
                if row[2] == user_choice:
                    results.append(row)
        else:
            for row in existing_assignments:
                if row[2] == user_choice and row[5] == current_choice:
                    results.append(row)
        results_text_show = results_text.markdown("There is **" + str(len(results)) + "** result(s) for your search.")
        if len(results) != 0:
            results_df_show = results_df.dataframe(pd.DataFrame(results, columns = ["Device No.", "Device Type", "Assigned To", "Assigned From", "Assigned Till", "Current Assignment", "Assigned By"]))
        else:
            results_df.empty()
    else:
        results_text.empty()
        results_df.empty()
    return

def searchByDevices():
    searchByDevices_heading = st.empty()
    searchByDevices_heading_show = searchByDevices_heading.subheader("Search Assignments by Devices")
    df = pd.DataFrame(existing_assignments, columns = ["Device No.", "Device Type", "Assigned To", "Assigned From", "Assigned Till", "Current Assignment", "Assigned By"])
    device_types = ["Please select"]
    device_nos = ["Please select"]
    for row in existing_assignments:
        if row[1] not in device_types:
            device_types.append(row[1])
    for row in existing_assignments:
        if row[0] not in device_nos:
            device_nos.append(row[0])
    current = df['Current Assignment'].drop_duplicates()
    current = ["Please select"] + list(current)
    device_type_choice = st.selectbox("Select Device Type", device_types)
    device_no_choice = st.empty()
    device_no_choice_show = device_no_choice.selectbox("Select Device No.", device_nos)
    if device_type_choice != "Please select":
        results = []
        device_no_choice.empty()
        related_device_nos = ["Please select"]
        for row in existing_assignments:
            if row[1] == device_type_choice:
                if row[0] not in related_device_nos:
                    related_device_nos.append(row[0])
        device_no_choice_show = st.selectbox("Select Device No.", related_device_nos)
        if device_no_choice_show == "Please select":
            for row in existing_assignments:
                if row[1] == device_type_choice:
                    results.append(row)
        else:
            for row in existing_assignments:
                if row[1] == device_type_choice and row[0] == device_no_choice_show:
                    results.append(row)
        results_text = st.empty()
        results_df = st.empty()
        results_text_show = results_text.markdown("There is **" + str(len(results)) + "** result(s) for your search.")
        if len(results) != 0:
            results_df_show = results_df.dataframe(pd.DataFrame(results, columns = ["Device No.", "Device Type", "Assigned To", "Assigned From", "Assigned Till", "Current Assignment", "Assigned By"]))
        else:
            results_text.empty()
            results_df.empty()
    return

def viewUsersNoAssg():
    viewUsersNoAssg_heading = st.empty()
    viewUsersNoAssg_heading_show = viewUsersNoAssg_heading.subheader("Users without any Current Assignments")
    df = pd.DataFrame(existing_assignments, columns = ["Device No.", "Device Type", "Assigned To", "Assigned From", "Assigned Till", "Current Assignment", "Assigned By"])
    all_users = existing_users_names
    usersNoCurrentAssg = []
    usersCurrentAssg = []
    for row in existing_assignments:
        if row[5] and row[2] not in usersCurrentAssg:
            usersCurrentAssg.append(row[2])
    for user in all_users:
        if user not in usersCurrentAssg:
            usersNoCurrentAssg.append(user)
    usersNoCurrentAssg_count = 0
    for user in usersNoCurrentAssg:
        usersNoCurrentAssg_count += 1
        current_email = existing_users_emails[existing_users_names.index(user)]
        st.write(str(usersNoCurrentAssg_count) + ". " + user + " (" + current_email + ")")

def viewDevicesNoAssg():
    viewDevicesNoAssg_heading = st.empty()
    viewDevicesNoAssg_heading_show = viewDevicesNoAssg_heading.subheader("Devices without any Current Assignments")
    df_rows = []
    all_device_nos = []
    for row in existing_devices:
        if row[0] not in all_device_nos:
            all_device_nos.append(row[0])
    assg_device_nos = []
    for row in existing_assignments:
        if row[5]:
            if row[0] not in assg_device_nos:
                assg_device_nos.append(row[0])
    no_assg_device_nos = []
    for device_no in all_device_nos:
        if device_no not in assg_device_nos:
            no_assg_device_nos.append(device_no)
    for row in existing_devices:
        if row[0] in no_assg_device_nos:
            df_rows.append(row)
    df = pd.DataFrame(df_rows, columns = ["Device No.", "Device Type", "Purchase Date", "Price in (S$)"])
    st.dataframe(df)
    return

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
        viewAssg()
        searchByUsers()
        searchByDevices()
        viewUsersNoAssg()
        viewDevicesNoAssg()
    else:
        key_error_show = key_error.markdown("You have entered an incorrect Key.")