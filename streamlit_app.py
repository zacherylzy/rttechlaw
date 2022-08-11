import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
from csv import reader, writer
from pandas import ExcelWriter, read_csv
from copy import deepcopy
import altair as alt
from datetime import datetime as dt

st.title('Welcome to LUPL Statistics')

########## INPUT ########################################################################################################
st.header('Input')
input_form = st.form("Input")
lawyers = input_form.file_uploader("Lawyers List")
secretaries = input_form.file_uploader("Secretaries List")
mad = input_form.file_uploader("Monthly Activity Data")
submit = input_form.form_submit_button("Submit")

if submit:

    if lawyers is not None:
        # To read file as bytes:
        bytes_data = lawyers.getvalue()
        # To convert to a string based IO:
        stringio = StringIO(lawyers.getvalue().decode("utf-8"))
        # To read file as string:
        string_data = stringio.read()
        # Can be used wherever a "file-like" object is accepted:
        dataframe1 = pd.read_csv(lawyers)
        lawyers_data = dataframe1.values.tolist()

    if secretaries is not None:
        # To read file as bytes:
        bytes_data = secretaries.getvalue()
        # To convert to a string based IO:
        stringio = StringIO(secretaries.getvalue().decode("utf-8"))
        # To read file as string:
        string_data = stringio.read()
        # Can be used wherever a "file-like" object is accepted:
        dataframe2 = pd.read_csv(secretaries)
        secretaries_data = dataframe2.values.tolist()

    if mad is not None:
        # To read file as bytes:
        bytes_data = mad.getvalue()
        # To convert to a string based IO:
        stringio = StringIO(mad.getvalue().decode("utf-8"))
        # To read file as string:
        string_data = stringio.read()
        # Can be used wherever a "file-like" object is accepted:
        dataframe3 = pd.read_csv(mad)
        mad_data = dataframe3.values.tolist()

    if lawyers is None or secretaries is None or mad is None:
        st.write("Please upload the input files before viewing results.")
    else:
        output_raw = []

        for row in mad_data:
            if type(row[1]) != float:
                if row[1].lower() not in output_raw:
                    output_raw.append(row[1].lower())

        for row in lawyers_data:
            if row[1] is not None and row[1].lower() not in output_raw:
                output_raw.append(row[1].lower())

        for row in secretaries_data:
            if row[1] is not None and row[1].lower() not in output_raw:
                output_raw.append(row[1].lower())

        output_raw_v2 = []

        for email in output_raw:
            output_raw_v2.append([email, "", "", ""])
        
        for row1 in output_raw_v2:
            for row2 in lawyers_data:
                if row1[0].lower() == row2[1].lower():
                    row1[1] = row2[0]
                    row1[2] = row2[2]
                    row1[3] = "Lawyer"

        for row1 in output_raw_v2:
            for row2 in secretaries_data:
                if row1[0].lower() == row2[1].lower():
                    row1[1] = row2[0]
                    row1[2] = row2[2]
                    row1[3] = "Secretary"

        output_final = []

        for row in output_raw_v2:
            if row not in output_final:
                output_final.append(row)

        months = []

        for row in mad_data:
            if row[0] not in months:
                months.append(row[0])

        for row in output_final:
            for month in months:
                row.append(0)
                row.append(0)

        for row1 in output_final:
            for row2 in mad_data:
                month_index = months.index(row2[0])
                if type(row2[1]) != float:
                    if row1[0].lower() == row2[1].lower():
                        row1[(month_index + 2) * 2] = int(row2[2])
                        row1[((month_index + 2) * 2) + 1] = int(row2[3])

        output_final_header = ["Email", "Name", "Department", "Type"]
        
        for month in months:
            output_final_header.append(month + " Days")
            output_final_header.append(month + " Time")

        output_final_no_empty = []

        for row in output_final:
            if row[0] != "":
                output_final_no_empty.append(row)

        all = []

        for row in output_final_no_empty:
            email_parts = row[0].split("@")
            email_end = email_parts[-1].lower()
            if email_end not in all and email_end != "email address":
                all.append(email_end)

        all_with_users = []

        for branch in all:
            temp_branch = []
            for row in output_final_no_empty:
                if row[0].lower().endswith(branch):
                    temp_branch.append(row)
            all_with_users.append(temp_branch)

        output_final_no_empty_with_average = deepcopy(output_final_no_empty)

        for row in output_final_no_empty_with_average:
            end_limit = (len(months) * 2) + 4
            for w in range(4, end_limit, 2):
                average_days_time = (row[w] + row[w + 1]) / 2
                row.append(average_days_time)

        output_final_no_empty_with_change = deepcopy(output_final_no_empty_with_average)

        for row in output_final_no_empty_with_change:
            start = (len(months) * 2) + 4 + 1
            end = (len(months) * 2) + 4 + len(months)
            for v in range(start, end):
                if row[v - 1] == 0.0 and row[v] - row[v - 1] == 0.0:
                    row.append(0.0)
                elif row[v - 1] == 0.0 and row[v] - row[v - 1] != 0.0:
                    row.append(100.0)
                else:
                    percent_change_only = round(((row[v] - row[v - 1]) / row[v - 1]) * 100, 1)
                    row.append(percent_change_only)

        output_final_no_empty_only_change = []

        for row in output_final_no_empty_with_change:
            end_limit = (len(months) * 2) + 4 + len(months)
            temp_change_only = row[0:4] + row[end_limit:]
            output_final_no_empty_only_change.append(temp_change_only)

        all_with_users_change = []

        output_final_change_header = ["Email", "Name", "Department", "Type"]
        
        for q in range(1, len(months)):
            output_final_change_header.append(months[q] + " Avg % Change")

        for branch in all:
            temp_branch_change = []
            for row in output_final_no_empty_only_change:
                if row[0].lower().endswith(branch):
                    temp_branch_change.append(row)
            all_with_users_change.append(temp_branch_change)

    ########## OVERVIEW #####################################################################################################    
    st.title("Overview")
    st.write("(Rajah & Tann Singapore ONLY)")
    if lawyers is None or secretaries is None or mad is None:
        st.write("Please upload the input files before viewing results.")
    else:
        total_lawyers_per_pg = []
        total_secretaries_per_pg = []
        total_lawyers = 0
        total_secretaries = 0

        pgs = []

        for row in lawyers_data:
            if row[2] not in pgs:
                pgs.append(row[2])

        for row in secretaries_data:
            if row[2] not in pgs:
                pgs.append(row[2])

        for pg in pgs:
            lawyer_count = 0
            secretary_count = 0
            for row in output_final_no_empty:
                if row[2] == pg:
                    if row[3] == "Lawyer":
                        lawyer_count += 1
                    elif row[3] == "Secretary":
                        secretary_count += 1
            total_lawyers_per_pg.append(lawyer_count)
            total_secretaries_per_pg.append(secretary_count)

        for pg in total_lawyers_per_pg:
            total_lawyers += pg

        for pg in total_secretaries_per_pg:
            total_secretaries += pg

        power_users_only_average = []

        for row in output_final_no_empty_with_average:
            end_limit = (len(months) * 2) + 4
            temprow_average = row[0:4] + row[end_limit:]
            power_users_only_average.append(temprow_average)

        monthly_users_count = []

        for branch in all:
            monthly_users_count.append([])

        for branch in all:
            branch_users = []
            end_limit = len(months) + 4
            for n in range(4, end_limit):
                count = 0
                for row in power_users_only_average:
                        if row[n] > 0.0 and row[0].lower().endswith("rajahtann.com"):
                            count += 1
                monthly_users_count.append([months[n - 4], count])

        monthly_users_count_v2 = []

        for row in monthly_users_count:
            if row != []:
                if row not in monthly_users_count_v2:
                    monthly_users_count_v2.append(row)

        for row in monthly_users_count_v2:
            if row != []:
                row[0] = dt.strptime(row[0], '%b-%y').strftime('%Y-%m')

        monthly_users_count_dataframe = pd.DataFrame(monthly_users_count_v2, columns = ["Month", "Users Count"])

        st.subheader("Count of Total Monthly Users")
        monthly_users_count_chart_data = alt.Chart(monthly_users_count_dataframe).mark_bar().encode(
            x = "Month:O",
            y = "Users Count:Q"
        )

        st.altair_chart(monthly_users_count_chart_data, use_container_width = True)
        st.table(monthly_users_count_dataframe)

        monthly_users_count_by_type = []
        monthly_users_count_by_type_v2 = []

        end_limit = len(months) + 4

        for n in range(4, end_limit):
            lawyer_count = 0
            sec_count = 0
            other_count = 0
            for row in power_users_only_average:
                if row[n] > 0.0:
                    if row[3] == "Lawyer":
                        lawyer_count += 1
                    elif row[3] == "Secretary":
                        sec_count += 1
                    else:
                        other_count += 1
            monthly_users_count_by_type.append([months[n - 4], lawyer_count, total_lawyers, sec_count, total_secretaries, other_count])
            monthly_users_count_by_type_v2.append([months[n - 4], "Lawyer", lawyer_count])
            monthly_users_count_by_type_v2.append([months[n - 4], "Secretary", sec_count])
            monthly_users_count_by_type_v2.append([months[n - 4], "Other", other_count])

        for row in monthly_users_count_by_type_v2:
            if row != []:
                row[0] = dt.strptime(row[0], '%b-%y').strftime('%Y-%m')
        
        
        monthly_users_count_by_type_dataframe = pd.DataFrame(monthly_users_count_by_type, columns = ["Month", "Lawyer Users Count", "Total Lawyers", "Secretary Users Count", "Total Secretaries", "Others User Count"])
        
        monthly_users_count_by_type_dataframe_v2 = pd.DataFrame(monthly_users_count_by_type_v2, columns = ["Month", "Type", "Users Count"])

        st.subheader("Count of Total Monthly Users by Type (Lawyer/Secretary/Other)")
        monthly_users_count_by_type_chart_data = alt.Chart(monthly_users_count_by_type_dataframe_v2).mark_line().encode(
            x = "Month",
            y = "Users Count",
            color = "Type"
        )

        st.altair_chart(monthly_users_count_by_type_chart_data, use_container_width = True)

        st.table(monthly_users_count_by_type_dataframe)

        monthly_users_count_by_pg_type = []

        for pg in pgs:
            pg_users_count = []
            for p in range(4, end_limit):
                lawyer_count = 0
                sec_count = 0
                other_count = 0
                for row in power_users_only_average:
                    if row[p] > 0.0 and row[2] == pg:
                        if row[3] == "Lawyer":
                            lawyer_count += 1
                        elif row[3] == "Secretary":
                            sec_count += 1
                        else:
                            other_count += 1
                pg_users_count.append([months[p - 4], lawyer_count, sec_count, other_count])
            monthly_users_count_by_pg_type.append([pg, pg_users_count, [total_lawyers_per_pg[pgs.index(pg)], total_secretaries_per_pg[pgs.index(pg)]]])

        monthly_users_count_by_pg_type_excel = []

        for row in monthly_users_count_by_pg_type:
            temprow_excel = []
            temprow_excel.append(row[0])
            for item in row[1]:
                temprow_excel += item[1:]
            temprow_excel.append(row[2][0])
            temprow_excel.append(row[2][1])
            monthly_users_count_by_pg_type_excel.append(temprow_excel)
        
        monthly_users_count_by_pg_type_excel_header = ["Practice Group"]

        for month in months:
            monthly_users_count_by_pg_type_excel_header.append(month + " Lawyer Users Count")
            monthly_users_count_by_pg_type_excel_header.append(month + " Secretary Users Count")
            monthly_users_count_by_pg_type_excel_header.append(month + " Others Users Count")
        monthly_users_count_by_pg_type_excel_header += ["Total Lawyers", "Total Secretaries"]

        individual_charts = []

        for pg in pgs:
            for_each_pg = []
            for_each_pg.append(pg)
            for month in months:
                for_each_pg.append([0, 0, 0])
            for row in power_users_only_average:
                if row[2] == pg:
                    for c in range(4, len(row)):
                        if row[c] > 0:
                            if row[3] == "Lawyer":
                                for_each_pg[c - 3][0] += 1
                            elif row[3] == "Secretary":
                                for_each_pg[c - 3][1] += 1
                            else:
                                for_each_pg[c - 3][2] += 1
            individual_charts.append(for_each_pg)
        
        for pg_row in individual_charts:
            for d in range(1, len(pg_row)):
                pg_row[d].insert(0, dt.strptime(months[d - 1], '%b-%y').strftime('%Y-%m'))

        individual_charts_v2 = []

        for pg_row in individual_charts:
            new_pg_row = [pg_row[0]]
            for e in range(1, len(pg_row)):
                new_pg_row.append([pg_row[e][0], "Lawyer", pg_row[e][1]])
                new_pg_row.append([pg_row[e][0], "Secretary", pg_row[e][2]])
                new_pg_row.append([pg_row[e][0], "Other", pg_row[e][3]])
            individual_charts_v2.append(new_pg_row)

        st.subheader("Count of Total Monthly Users per PG by Type")

        for pg_data in individual_charts_v2:
            st.write(pg_data[0])
            pg_chart_data = []
            for j in range(1, len(pg_data)):
                pg_chart_data.append(pg_data[j])
            dataframe_pg_month = pd.DataFrame()
            dataframe_pg_month = pd.DataFrame(pg_chart_data, columns = ["Month", "Type", "Users Count"])
            monthly_users_count_by_pg_type_chart_data = alt.Chart(dataframe_pg_month).mark_line().encode(
                x = "Month",
                y = "Users Count",
                color = "Type"
            )
            st.altair_chart(monthly_users_count_by_pg_type_chart_data, use_container_width = True)
        
        monthly_users_count_by_pg_type_excel_dataframe = pd.DataFrame(monthly_users_count_by_pg_type_excel, columns = monthly_users_count_by_pg_type_excel_header)
        
        avg_overall = []

        pg_count = 0
        for row in monthly_users_count_by_pg_type_excel:
            total_lawyer = 0
            total_secretary = 0
            explanation = ""
            lawyer_divider = 1 + (len(months) * 3)
            secretary_divider = 1 + (len(months) * 3)
            for l in range(1, len(row) - 2, 3):
                avg_lawyer = (row[l] / lawyer_divider) * 100
                if row[38] != 0:
                    avg_secretary = (row[l + 1] / secretary_divider) * 100
                total_lawyer += avg_lawyer
                total_secretary += avg_secretary
            avg_total_lawyer = total_lawyer / 12
            avg_total_secretary = total_secretary / 12
            if avg_total_lawyer > avg_total_secretary:
                explanation = "Lawyers Using More"
            elif avg_total_secretary > avg_total_lawyer:
                explanation = "Secretaries Using More"
            else:
                explanation = "Equal Usage"
            avg_overall.append([row[0], str(round(avg_total_lawyer, 2)) + "% (" + str(row[l]) + ")", total_lawyers_per_pg[pg_count], str(round(avg_total_secretary, 2)) + "% (" + str(row[l + 1]) + ")", total_secretaries_per_pg[pg_count], explanation])
            pg_count += 1

        avg_overall_df = pd.DataFrame(avg_overall, columns = ["Practice Group", "% of Lawyers Using", "Total Lawyers", "% of Secretaries Using", "Total Secretaries", "Remarks"])
        st.table(avg_overall_df)

    ########## DETAILED #####################################################################################################
    st.title("Detailed")
    if lawyers is None or secretaries is None or mad is None:
        st.write("Please upload the input files before viewing results.")
    else:
        files = []

        st.subheader("There are " + str(len(all)) + " branches which are as follows:")
        count = 0
        for branch in all:
            count += 1
            temp_z_branch = branch.split(".")
            st.write(str(count) + ". " + temp_z_branch[0])

        for z in range(len(all)):
            temp_z = all[z].split(".")
            dataframe_micro = pd.DataFrame()
            dataframe_micro = pd.DataFrame(all_with_users[z], columns = output_final_header)
            dataframe_macro = pd.DataFrame()
            dataframe_macro = pd.DataFrame(all_with_users_change[z], columns = output_final_change_header)
            st.subheader(temp_z[0])
            st.write("Macro View")
            st.write(dataframe_macro)
            st.write("Micro View")
            st.write(dataframe_micro)

    ########## TOP 2 POWER USERS PER PG ####################################################################################
    st.title('Top 2 Power Users per PG')
    if lawyers is None or secretaries is None or mad is None:
        st.write("Please upload the input files before viewing results.")
    else:
        pgs = []

        for row in lawyers_data:
            if row[2] not in pgs:
                pgs.append(row[2])

        for row in secretaries_data:
            if row[2] not in pgs:
                pgs.append(row[2])

        users_raw = deepcopy(output_final_no_empty_with_average)

        users_final = []

        for row in users_raw:
            temprow_raw = row[0:4] + row[28:]
            users_final.append(temprow_raw)

        users_per_pg = []

        for i in range(0, len(pgs)):
            users_per_pg.append([])

        for b in range(len(pgs)):
            for row in users_raw:
                if row[2] == pgs[b]:
                    users_per_pg[b].append(row)

        power_users_final = []

        for l in range(len(users_per_pg)):
            power_users_final_per_pg = []
            for k in range(4, end_limit):
                temp_per_pg = []
                temp_per_pg = users_per_pg[l].sort(key=lambda x: -x[k])
                if users_per_pg[l] == []:
                    power_users_final_per_pg.append([pgs[l], "None", "None", "None", "None"])
                elif len(users_per_pg[l]) == 1:
                    power_user_1 = users_per_pg[l][0]
                    if power_user_1[k] == 0.0:
                        power_users_final_per_pg.append([pgs[l], "None", "None", "None", "None"])
                    else:
                        power_users_final_per_pg.append([pgs[l], power_user_1[1], power_user_1[3], "None", "None"])
                elif len(users_per_pg[l]) > 1:
                    power_user_1 = users_per_pg[l][0]
                    power_user_2 = users_per_pg[l][1]
                    if power_user_1[k] == 0.0 and power_user_2[k] == 0.0:
                        power_users_final_per_pg.append([pgs[l], "None", "None", "None", "None"])
                    elif power_user_1[k] != 0.0 and power_user_2[k] == 0.0:
                        power_users_final_per_pg.append([pgs[l], power_user_1[1], power_user_1[3], "None", "None"])
                    else:
                        power_users_final_per_pg.append([pgs[l], power_user_1[1], power_user_1[3], power_user_2[1], power_user_2[3]])
            power_users_final.append(power_users_final_per_pg)

        power_users_header = ["Practice Group", "Power User 1", "Power User 1 Type", "Power User 2", "Power User 2 Type"]

        files_power_users = []

        for c in range(len(months)):
            files_power_users.append(months[c] + ".csv")
            dataframe_power = pd.DataFrame()
            dataframe_power_rows = []
            for power_users_per_pg in power_users_final:
                dataframe_power_rows.append(power_users_per_pg[c])
            dataframe_power = pd.DataFrame(dataframe_power_rows, columns = power_users_header)
            st.subheader(months[c])
            st.write(dataframe_power)
