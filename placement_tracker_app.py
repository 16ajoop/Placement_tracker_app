import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

CSV_FILE = "placements.csv"

# ----------------------------------------
# Initialize CSV if it doesn't exist
# ----------------------------------------
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "Company", "Role", "Package(LPA)", 
            "Eligibility_CGPA", "Backlogs_Allowed"
            "Eligibility_10th", "Eligibility_12th"
        ])
        df.to_csv(CSV_FILE, index=False)

# ----------------------------------------
# Load Data
# ----------------------------------------
def load_data():
    return pd.read_csv(CSV_FILE)

# ----------------------------------------
# Save Data
# ----------------------------------------
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# ----------------------------------------
# Streamlit UI
# ----------------------------------------
def main():
    st.set_page_config(page_title="Placement Tracker", layout="wide")
    st.title("🎓 Placement Tracker App")

    init_csv()
    df = load_data()

    menu = [
        "📋 View Companies",
        "➕ Add Company", 
        "✅ Check Eligibility", 
        "📊 Visualize Packages",
        "🗑️ Remove Company"
    ]
    choice = st.sidebar.radio("Menu", menu)

    # ------------------------------
    # View Companies (with search & sort)
    # ------------------------------
    if choice == "📋 View Companies":
        st.subheader("All Companies")

        if df.empty:
            st.warning("No companies added yet.")
        else:
            # --- Search Filter ---
            search_term = st.text_input("🔍 Search by Role / Company")
            filtered_df = df.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df["Role"].str.contains(search_term, case=False, na=False) |
                    filtered_df["Company"].str.contains(search_term, case=False, na=False)
                ]

            # --- Sorting ---
            sort_order = st.radio("Sort by Package (LPA)", ["None", "Highest → Lowest", "Lowest → Highest"], horizontal=True)
            if sort_order == "Highest → Lowest":
                filtered_df = filtered_df.sort_values(by="Package(LPA)", ascending=False)
            elif sort_order == "Lowest → Highest":
                filtered_df = filtered_df.sort_values(by="Package(LPA)", ascending=True)

            st.dataframe(filtered_df.reset_index(drop=True))

    
    # ------------------------------
    # Add Company
    # ------------------------------
    elif choice == "➕ Add Company":
        st.subheader("Add a New Company")
        with st.form("add_form"):
            company = st.text_input("Company Name")
            role = st.text_input("Role")
            package = st.number_input("Package (LPA)", min_value=1.0, step=0.5)
            cgpa = st.number_input("Minimum CGPA Required", min_value=0.0, max_value=10.0, step=0.1)
            backlogs = st.number_input("Backlogs Allowed", min_value=0, step=1)
            perc_10th = st.number_input("Minimum 10th Percentage Required", min_value=0.0, max_value=100.0, step=0.1)
            perc_12th = st.number_input("Minimum 12th Percentage Required", min_value=0.0, max_value=100.0, step=0.1)
            submitted = st.form_submit_button("Add Company")

        if submitted:
            new_entry = {
                "Company": company,
                "Role": role,
                "Package(LPA)": package,
                "Eligibility_CGPA": cgpa,
                "Backlogs_Allowed": backlogs,
                "Eligibility_10th": perc_10th,
                "Eligibility_12th": perc_12th
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)
            st.success(f"{company} added successfully!")

    # ------------------------------
    # Check Eligibility
    # ------------------------------
    elif choice == "✅ Check Eligibility":
        st.subheader("Check Your Eligibility")
        user_cgpa = st.number_input("Enter your CGPA", min_value=0.0, max_value=10.0, step=0.1)
        user_backlogs = st.number_input("Enter your no. of backlogs", min_value=0, step=1)
        user_10th = st.number_input("Enter your 10th Percentage", min_value=0.0, max_value=100.0, step=0.1)
        user_12th = st.number_input("Enter your 12th Percentage", min_value=0.0, max_value=100.0, step=0.1)

        if st.button("Check Eligibility"):
            eligible = df[
                (df["Eligibility_CGPA"] <= user_cgpa) &
                (df["Backlogs_Allowed"] >= user_backlogs) &
                (df["Eligibility_10th"] <= user_10th) &
                (df["Eligibility_12th"] <= user_12th)
                ]
            if eligible.empty:
                st.error("❌ No companies available for your profile.")
            else:
                st.success("✅ You are eligible for the following companies:")
                st.dataframe(eligible[["Company", "Role", "Package(LPA)"]])
                eligible.to_csv("eligible_companies.csv", index=False)
                st.download_button("📥 Download Eligible Companies", eligible.to_csv(index=False), "eligible_companies.csv")

    # ------------------------------
    # Visualize Packages 
    # ------------------------------
    elif choice == "📊 Visualize Packages":
        st.subheader("📊 Company Packages Comparison")

        if df.empty:
            st.warning("No companies to visualize yet.")
        else:
            import plotly.express as px

            # Sort by package descending for clarity
            df_sorted = df.sort_values(by="Package(LPA)", ascending=False)

            # Create interactive bar chart
            fig = px.bar(
                df_sorted,
                x="Company",
                y="Package(LPA)",
                color="Package(LPA)",
                text="Role",
                color_continuous_scale="Viridis",  # gradient colors
                title="💼 Salary Packages by Company",
            )

            # Customize chart
            fig.update_traces(
                textposition="outside",
                marker=dict(line=dict(width=0.8, color="black"))
            )
            fig.update_layout(
                xaxis_title="Company",
                yaxis_title="Package (LPA)",
                title_x=0.5,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(size=14),
            )

            st.plotly_chart(fig, use_container_width=True)
    
    # ------------------------------
    # Remove Company 
    # ------------------------------
    elif choice == "🗑️ Remove Company":
        st.subheader("Remove a Company")

        if df.empty:
            st.warning("No companies to remove.")
        else:
            # Create unique labels like "Company - Role"
            df["Company_Role"] = df["Company"] + " - " + df["Role"]
            company_role_list = df["Company_Role"].tolist()

            selected_entry = st.selectbox("Select a company to remove", company_role_list)

            if st.button("Delete Company"):
                # Remove the selected row only
                df = df[df["Company_Role"] != selected_entry].drop(columns=["Company_Role"])
                save_data(df)

                st.success(f"{selected_entry} removed successfully!")

                # Refresh UI properly
                st.rerun()




if __name__ == "__main__":
    main()
