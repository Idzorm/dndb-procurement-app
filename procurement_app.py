import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Procurement App", layout="wide")

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Project", "Category", "Description", "Unit", "Quantity", "Unit Cost",
        "Vendor Name", "Vendor Location", "Vendor TIN", "Vendor Reg No"
    ])

# Sidebar: Add new entry
st.sidebar.header("Add Procurement Entry")
with st.sidebar.form("entry_form"):
    project = st.text_input("Project Name")
    category = st.text_input("Category")
    description = st.text_input("Description")
    unit = st.text_input("Unit")
    quantity = st.number_input("Quantity", min_value=0.0)
    unit_cost = st.number_input("Unit Cost", min_value=0.0)
    vendor_name = st.text_input("Vendor Name")
    vendor_location = st.text_input("Vendor Location")
    vendor_tin = st.text_input("Vendor TIN")
    vendor_reg = st.text_input("Vendor Registration No")
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        new_row = {
            "Project": project,
            "Category": category,
            "Description": description,
            "Unit": unit,
            "Quantity": quantity,
            "Unit Cost": unit_cost,
            "Vendor Name": vendor_name,
            "Vendor Location": vendor_location,
            "Vendor TIN": vendor_tin,
            "Vendor Reg No": vendor_reg
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Entry added!")

# Main: Display data
st.title("📋 Procurement Dashboard")
df = st.session_state.data.copy()
df["Total Cost"] = df["Quantity"] * df["Unit Cost"]
st.dataframe(df, use_container_width=True)

# Summary
st.subheader("📊 Project Summary")
project_costs = df.groupby("Project")["Total Cost"].sum().reset_index()
vendor_summary = df.groupby("Vendor Name")["Total Cost"].sum().reset_index()
st.write("Total Cost per Project")
st.dataframe(project_costs)
st.write("Total Spend per Vendor")
st.dataframe(vendor_summary)

# Export PDF
def generate_pdf(po_df, vendor):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Purchase Order - {vendor}", ln=True, align="C")
    pdf.ln(10)

    for index, row in po_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Description']} - {row['Quantity']} {row['Unit']} @ {row['Unit Cost']} = {row['Total Cost']}", ln=True)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output

# Export Excel
def generate_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        data.to_excel(writer, index=False, sheet_name="Procurement")
    return output

# Export buttons
st.subheader("📤 Export Reports")
selected_vendor = st.selectbox("Select Vendor for PO", df["Vendor Name"].unique())
po_df = df[df["Vendor Name"] == selected_vendor]

if st.button("Export PO as PDF"):
    pdf_file = generate_pdf(po_df, selected_vendor)
    st.download_button("Download PDF", pdf_file.getvalue(), file_name=f"PO_{selected_vendor}.pdf")

if st.button("Export Full Report as Excel"):
    excel_file = generate_excel(df)
    st.download_button("Download Excel", excel_file.getvalue(), file_name="Procurement_Report.xlsx")
