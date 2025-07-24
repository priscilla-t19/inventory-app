import streamlit as st
import pandas as pd
import re
from database import init_db, SessionLocal, Asset, User
from sqlalchemy import text
from auth import create_user, authenticate_user




init_db()

#  CSS Styling 
st.markdown("""
    <style>
        .stButton>button {
            border-radius: 0.5rem;
            background-color: #4CAF50;
            color: white;
            padding: 8px 20px;
        }
        .stTextInput>div>input, .stTextArea>div>textarea, .stSelectbox>div {
            border-radius: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

#  AUTH UI 
def auth_ui():
    st.title("🔐 IT Asset Inventory - Login / Sign Up")

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "Sign Up"

    mode = st.sidebar.radio("Choose Mode", ["Sign Up", "Login"], 
                            index=0 if st.session_state.auth_mode == "Sign Up" else 1)
    st.session_state.auth_mode = mode

    allowed_domain = "gov.bw"

    if mode == "Login":
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                with SessionLocal() as db:
                    user = authenticate_user(db, email, password)
                    if user:
                        st.session_state.user = {"email": user.email}
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

    elif mode == "Sign Up":
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up", key="signup_btn"):
            if not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif not email.endswith(f"@{allowed_domain}"):
                st.error(f"Only @{allowed_domain} email addresses allowed.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Invalid email format.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                with SessionLocal() as db:
                    existing_user = db.query(User).filter(User.email == email).first()
                    if existing_user:
                        st.error("User already exists.")
                    else:
                        create_user(db, email, password)
                        st.success("✅ Account created successfully! Please log in.")
                        st.session_state.auth_mode = "Login"
                        st.rerun()



#  Fetch Inventory 


def fetch_inventory():
    with SessionLocal() as db:
        assets = db.query(Asset).all()
        df = pd.DataFrame([{
            k: v for k, v in a.__dict__.items() if k != "_sa_instance_state"
        } for a in assets])
        if not df.empty and "id" not in df.columns:
            df["id"] = [a.id for a in assets]
        if not df.empty:
            df["date_of_purchase"] = pd.to_datetime(df["date_of_purchase"], errors='coerce')
            df["cost"] = df["cost"].apply(lambda x: f"P {x}" if str(x).replace('.', '', 1).isdigit() else x)
            cols = list(df.columns)
            if "username" in cols:
                cols.insert(0, cols.pop(cols.index("username")))
            df = df[cols]
        return df

#  MAIN APP 
def main_app():
    st.sidebar.write(f"✅ Logged in as: {st.session_state.user['email']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.title("📦 IT Asset Inventory System")
    menu = ["View Inventory", "Add Asset", "Edit/Delete Asset"]
    choice = st.sidebar.selectbox("Menu", menu)

    df = fetch_inventory()

    if choice == "View Inventory":
        st.subheader("Current Inventory")
        search_term = st.text_input("Search by Username, Item, or Location")
        if "status" in df.columns:
            status_options = ["All"] + sorted(df["status"].dropna().unique().tolist())
        else:
            status_options = ["All"]    
        status_filter = st.selectbox("Filter by Status", status_options)
        min_date = st.date_input("Start Date", value=df["date_of_purchase"].min().date() if not df.empty else None)
        max_date = st.date_input("End Date", value=df["date_of_purchase"].max().date() if not df.empty else None)

        if search_term:
            mask = df["username"].str.contains(search_term, case=False, na=False) | \
                   df["item"].str.contains(search_term, case=False, na=False) | \
                   df["location"].str.contains(search_term, case=False, na=False)
            df = df[mask]

         

        if status_filter != "All" and "status" in df.columns:
            df = df[df["status"] == status_filter]
        if "date_of_purchase" in df.columns and not df.empty:    
            df = df[(df["date_of_purchase"] >= pd.to_datetime(min_date)) &
                    (df["date_of_purchase"] <= pd.to_datetime(max_date))]

        st.dataframe(df)

    elif choice == "Add Asset":
        st.subheader("➕ Add New Asset")
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username (Owner)")
                item = st.text_input("Item")
                computer_name = st.text_input("Computer Name")
                ip_address = st.text_input("IP Address")
                mac_address = st.text_input("MAC Address")
                make = st.text_input("Make")
                model = st.text_input("Model")
                screen_size = st.text_input("Screen Size")
                man_serial_no = st.text_input("Manufacturer Serial No")
                g_serial_number = st.text_input("G Serial Number")
                operating_system = st.text_input("Operating System")
                os_version = st.text_input("OS Version")
                os_build = st.text_input("OS Build")
                system_type = st.text_input("System Type")
                storage_size = st.text_input("Storage Size")
                memory_size = st.text_input("Memory Size")
                processor_speed = st.text_input("Processor Speed")
            with col2:
                office_suite = st.text_input("Office Suite")
                comments = st.text_area("Comments")
                recommendations = st.text_area("Recommendations")
                location = st.text_input("Location")
                status = st.selectbox("Status", ["Working", "Not Working", "Repair", "Fair"])
                date_of_purchase = st.date_input("Date of Purchase")
                cost = st.text_input("Cost")
                supplier = st.text_input("Supplier")
                gpo_no = st.text_input("GPO Number")
                warranty_period = st.text_input("Warranty Period")
                quantity = st.number_input("Quantity", 1)
                storage_type = st.text_input("Storage Type")

            if st.form_submit_button("Add Asset"):
                errors = []

                if not username:
                    errors.append("Username is required.")
                if not item:
                    errors.append("Item is required.")
                if not cost:
                    errors.append("Cost is required.")
                elif not re.match(r'^\d+(\.\d{1,2})?$', cost):
                    errors.append("Cost must be a valid number.")
                if ip_address and not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip_address):
                    errors.append("IP Address format is invalid.")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    with SessionLocal() as db:
                        new_asset = Asset(
                            username=username, item=item, computer_name=computer_name, ip_address=ip_address,
                            mac_address=mac_address, make=make, model=model, screen_size=screen_size,
                            man_serial_no=man_serial_no, g_serial_number=g_serial_number, operating_system=operating_system,
                            os_version=os_version, os_build=os_build, system_type=system_type,
                            storage_size=storage_size, memory_size=memory_size, processor_speed=processor_speed,
                            office_suite=office_suite, comments=comments, recommendations=recommendations,
                            location=location, status=status, date_of_purchase= date_of_purchase.isofformat(),
                            cost=cost, supplier=supplier, gpo_no=gpo_no, warranty_period=warranty_period,
                            quantity=quantity, storage_type=storage_type
                        )
                        db.add(new_asset)
                        db.commit()
                        st.success("✅ Asset added!")

   


    elif choice == "Edit/Delete Asset":
        st.subheader("✏️ Edit / 🗑️ Delete Asset")
        search = st.text_input("🔍 Search by username, item, or location")

        if search:
            mask = df["username"].str.contains(search, case=False, na=False) | \
                   df["item"].str.contains(search, case=False, na=False) | \
                   df["location"].str.contains(search, case=False, na=False)
            filtered_df = df[mask]
            
            
                                       
        else:
            filtered_df = df.copy()

        if filtered_df.empty:
         st.info("No matching assets found.")
        else:
         filtered_df["label"] = filtered_df["username"] + " - " + filtered_df["item"]
         option = st.selectbox("Select asset to edit/delete", filtered_df["label"].tolist())
         selected = filtered_df[filtered_df["label"] == option].iloc[0]


         with st.form("edit_form", clear_on_submit=False):
            username = st.text_input("Username", selected["username"])
            item = st.text_input("Item", selected["item"])
            location = st.text_input("Location", selected["location"])
            status = st.selectbox("Status", ["Working", "Not Working", "Repair", "Fair"],
                                  index=["Working", "Not Working", "Repair", "Fair"].index(selected["status"]))
            cost = st.text_input("Cost (Pula)", str(selected["cost"]).replace("P ", ""))
            date_of_purchase = st.date_input("Date of Purchase", pd.to_datetime(selected["date_of_purchase"]))
            computer_name = st.text_input("Computer Name", selected["computer_name"])
            ip_address = st.text_input("IP Address", selected["ip_address"])
            mac_address = st.text_input("MAC Address", selected["mac_address"])
            man_serial_no = st.text_input("Manufacturer Serial No", selected.get("man_serial_no", ""))
            

            col1, col2 = st.columns(2)
            with col1:
                update = st.form_submit_button("💾 Update Asset")
            with col2:
                delete = st.form_submit_button("🗑️ Delete Asset")

            # Only check if update/delete INSIDE the form block!
            if update:
                with SessionLocal() as db:
                    asset_id = int(selected["id"])
                    asset = db.query(Asset).filter(Asset.id == asset_id).first()
                    if asset:
                        asset.username = username
                        asset.item = item
                        asset.location = location
                        asset.status = status
                        asset.cost = cost
                        asset.date_of_purchase = str(date_of_purchase)
                        asset.computer_name = computer_name
                        asset.ip_address = ip_address
                        asset.mac_address = mac_address
                        asset.man_serial_no = man_serial_no
                        db.commit()
                        st.success("✅ Asset updated successfully!")
                        st.cache_data.clear()  # add this before st.rerun()

                        st.rerun()
                    else:
                        st.error("Asset not found.")

            if delete:
                with SessionLocal() as db:
                    asset_id = int(selected["id"])
                    asset = db.query(Asset).filter(Asset.id == asset_id).first()
                    if asset:
                       db.delete(asset)
                       db.commit()
                       
                       st.success("🗑️ Asset deleted successfully!")
                       st.cache_data.clear()  # add this before st.rerun()

                       st.rerun()
                    else:
                       
                       st.error("Asset not found.")
                  

#  Run App 
if st.session_state.get("user"):
    main_app()
else:
    auth_ui()
              