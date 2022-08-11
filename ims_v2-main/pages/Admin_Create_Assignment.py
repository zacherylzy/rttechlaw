from ast import Str
from email.policy import default
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
import json

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

def insert_new_assg(device_no, device_type, user, assigned_from, assigned_current, assigned_till, assigned_by):
    supabase.table("assignments").insert({
        'device_no': device_no,
        'device_type': device_type,
        'assigned_to': user,
        'assigned_from': str(assigned_from),
        'assigned_current': assigned_current,
        'assigned_till': str(assigned_till),
        'assigned_by': assigned_by
    }).execute()

def createNewAssg(admin_user_name):
    createNewAssg_heading = st.empty()
    createNewAssg_heading_show = createNewAssg_heading.subheader("Create Assignment")
    used_device_nos = []
    for row in existing_assignments:
        if row['device_no'] not in used_device_nos:
            used_device_nos.append(row['device_no'])
    all_device_nos = []
    for row in existing_devices:
        if row['device_no'] not in all_device_nos:
            all_device_nos.append(row['device_no'])
    non_used_device_nos = []
    for device_no in all_device_nos:
        if device_no not in used_device_nos:
            non_used_device_nos.append(device_no)
    non_used_device_nos = ["Please select"] + non_used_device_nos
    select_device_no = st.selectbox("Select Device No.", non_used_device_nos)
    available_users = ["Please select"] + existing_users_names
    select_user = st.selectbox("Select User", available_users)
    select_assigned_from = st.date_input("Assigned From")
    select_assigned_current = st.checkbox("Current Assignment")
    select_assigned_till = st.date_input("Assigned Till")
    select_assigned_by = st.selectbox("Assigned By", [admin_user_name])
    assign_button = st.button("Create Assignment")
    no_fill_error = st.empty()
    till_more_from = st.empty()
    success_create_assg = st.empty()
    if assign_button:
        if select_device_no == "Please select" or select_user == "Please select":
            no_fill_error_show = no_fill_error.markdown("Please select Device No. and User.")
        else:
            no_fill_error.empty()
            if dt.strptime(str(select_assigned_from), '%Y-%m-%d') > dt.strptime(str(select_assigned_till), '%Y-%m-%d'):
                till_more_from_show = till_more_from.markdown("Assigned From should be less than or equal to Assigned Till.")
            else:
                till_more_from.empty()
                current_device_type = ""
                for row in existing_devices:
                    if row['device_no'] == select_device_no:
                        current_device_type = row['device_type']
                success_create_assg_show = success_create_assg.markdown("This assignment has been successfully created.")
                return insert_new_assg(select_device_no, current_device_type, select_user, select_assigned_from, select_assigned_current, select_assigned_till, select_assigned_by)

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
        createNewAssg(admin_user_name)
    else:
        key_error_show = key_error.markdown("You have entered an incorrect Key.")