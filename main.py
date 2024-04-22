# Import necessary libraries
from tarfile import PAX_NAME_FIELDS
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import base64
import streamlit as st
from PIL import Image, ImageEnhance
from io import BytesIO
import base64
import datetime
import re

# Function to enhance the brightness of an image
def lighten_image(image_path, brightness_factor=1.0):

    img = Image.open(image_path)
    enhancer = ImageEnhance.Brightness(img)
    lightened_img = enhancer.enhance(brightness_factor)
    return lightened_img

# Function to convert an image to a Base64 string
def get_base64_from_image(img):

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Function to set a background image for the Streamlit app
def set_background(image_path, brightness_factor=0.99):

    lightened_img = lighten_image(image_path, brightness_factor)
    base64_img = get_base64_from_image(lightened_img)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{base64_img}");
        background-size: cover;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set the background image for the app
set_background(r"DiscoverEaseBG.jpg", brightness_factor=0.99)

# Display headings in the app
st.markdown('<h1 style="color: #fac002;">DiscoverEase</h1>', unsafe_allow_html=True)
st.markdown("<h3 style='color: #02ddfa'>Tailored App Recommendations at Your Fingertips</h3>", unsafe_allow_html=True)       

# Function to validate inputs for a new or updated app entry
def validate_app_inputs(app_id, app_name, developer_id, genre, size, app_version, ios_version, released_date, updated_date, avg_user_rating, age_group, developer_name, price, currency):
    
    # Ensure all mandatory fields are filled
    if not all([app_id, app_name, developer_id, genre, size, app_version, ios_version, released_date, updated_date, avg_user_rating, age_group, developer_name, price, currency]):
        return "Please fill in all mandatory fields."
    
    # Numerical fields validation (price and size)
    try:
        if float(price) < 0:
            return "Price must be non-negative numbers."
    except ValueError:
        return "Price must be valid numbers."
    
    try:
        if float(size) < 0:
            return "Size must be non-negative numbers."
    except ValueError:
        return "Size must be valid numbers."   

    # Date fields validation
    if updated_date and not is_valid_date(updated_date):
        return "Updated Date must be in YYYY-MM-DD format."
    if not is_valid_date(released_date):
        return "Released Date must be in YYYY-MM-DD format."

    # User Rating validation
    if avg_user_rating and (float(avg_user_rating) < 0 or float(avg_user_rating) > 5):
        return "Average User Rating must be between 0 and 5."

    # Genre validation to allow text and spaces
    if not re.match(r"^[A-Za-z\s\-]+$", genre):
        return "Genre should only contain letters, spaces, and hyphens."

    return None

# Function to check if a date string is valid
def is_valid_date(date_str):

    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Function to check if a developer ID is unique    
def is_developer_id_unique(developer_id):

    conn = sqlite3.connect('DiscoverEase.db')
    query = "SELECT * FROM developers WHERE Developer_Id = ?"
    result = pd.read_sql_query(query, conn, params=(developer_id,))
    conn.close()
    return result.empty  # Returns True if no record found, meaning the ID is unique

# Function to check if an app ID is unique
def is_app_id_unique(app_id):

    conn = sqlite3.connect('DiscoverEase.db')
    query = "SELECT * FROM applications WHERE App_Id = ?"
    result = pd.read_sql_query(query, conn, params=(app_id,))
    conn.close()
    return result.empty  # Returns True if no record found, meaning the ID is unique

# Function to create a new app in the database
def create_app():

    st.markdown('<h5 style="color: #FFFFFF;">Create a New App</h5>', unsafe_allow_html=True)

    # Get user input for a new app
    app_id = st.text_input("App_Id*")
    app_name = st.text_input("App Name*")
    developer_id = st.text_input("Developer ID*")
    genre = st.text_input("Genre*")
    size = st.text_input("Size (MB)*")
    app_version = st.text_input("App Version*")
    ios_version = st.text_input("iOS Version*")
    released_date = st.text_input("Released Date (YYYY-MM-DD)*")
    updated_date = st.text_input("Updated Date (YYYY-MM-DD)*")
    avg_user_rating = st.text_input("Average User Rating*")
    age_group = st.text_input("Age Group*")
    
    # Get additional information for developer and pricing
    developer_name = st.text_input("Developer Name*")
    price = st.text_input("Price*")
    currency = st.text_input("Currency*")

    # Validate and add the new app, developer, and pricing to the database
    if st.button("Create App"):

        error_message = validate_app_inputs(app_id, app_name, developer_id, genre, size, app_version, ios_version, released_date, updated_date, avg_user_rating, age_group, developer_name, price, currency)
        if error_message:
            st.error(error_message)
            return
        
        if not is_app_id_unique(app_id):
            st.error("App ID must be unique. The provided ID already exists.")
            return 

        if not is_developer_id_unique(developer_id):
            st.error("Developer ID must be unique. The provided ID already exists.")
            return       
        
        conn = sqlite3.connect('DiscoverEase.db')
        c = conn.cursor()

        # Insert into applications table
        insert_app_query = """
            INSERT INTO applications (App_Id, App_name, Developer_Id, Genre, Size, App_version, IOS_version, Released_date, Updated_date, Avg_user_rating, Age_group)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        app_values = (
            app_id, app_name, developer_id, genre, size, app_version,
            ios_version, released_date, updated_date, avg_user_rating, age_group
        )
        c.execute(insert_app_query, app_values)

        # Insert into developers table
        insert_dev_query = """
            INSERT INTO developers (Developer_Id, Developer)
            VALUES (?, ?);
        """
        dev_values = (developer_id, developer_name)
        c.execute(insert_dev_query, dev_values)

        # Insert into pricing table
        insert_pricing_query = """
            INSERT INTO pricing (App_id, Price, Currency)
            VALUES (?, ?, ?);
        """
        pricing_values = (app_id, price, currency)
        c.execute(insert_pricing_query, pricing_values)

        conn.commit()
        conn.close()

        st.success("App created successfully!")


# Function to update an existing app
def update_app():

    st.markdown('<h5 style="color: #FFFFFF;">Update an Existing App</h5>', unsafe_allow_html=True)

    # Get user input for app ID to fetch existing data
    app_id = st.text_input("App ID")

    # Fetch and display the existing app data for editing
    existing_app_data = read_data()[read_data()['App_Id'] == app_id]
        
    if existing_app_data.empty:
        st.warning("App not found. Enter a valid App ID.")
        return
    st.dataframe(existing_app_data)

    # Fetch and display the existing app data for editing
    existing_app_data = read_data()[read_data()['App_Id'] == app_id]

    # Fetching the developer id
    developer_id = existing_app_data.iloc[0]['Developer_Id']

    # Fetching developer data
    dev_data = read_developer(developer_id)

    # Fetch and display data from pricing table
    pricing_data = read_pricing(existing_app_data.iloc[0]['App_Id'])

    # Get updated values from the user for app properties
    updated_app_name = st.text_input("Updated App Name*", existing_app_data.iloc[0]['App_name'])
    updated_genre = st.text_input("Updated Genre*", existing_app_data.iloc[0]['Genre'])
    updated_price = st.text_input("Updated Price*", pricing_data.iloc[0]['Price'])  # Added line for pricing update

    if not dev_data.empty:
        updated_dev_name = st.text_input("Updated Developer Name*", dev_data.iloc[0]['Developer']) 

    # Perform update when the button is clicked
    if st.button("Update App"):

        # Validate inputs and perform updates in the database
        # Check if any of the required fields are empty
        if not all([updated_app_name, updated_genre, updated_price]):
            st.error("Please fill in all mandatory fields before submitting.")
            return
        
        # Numeric fields validation (updated_price)
        try:
            if float(updated_price) < 0:
                st.error("Price must be non-negative numbers.")
                return
        except ValueError:
            st.error("Price must be valid numbers.")
            return  
        
        # Genre validation to allow text and spaces
        if not re.match(r"^[A-Za-z\s\-]+$", updated_genre):
            st.error("Genre should only contain letters, spaces, and hyphens.")
            return             

        # Update database entries for the application and related tables
        conn = sqlite3.connect('DiscoverEase.db')
        c = conn.cursor()

        # Update applications table
        update_app_query = """
        UPDATE applications
        SET App_name=?, Genre=?
        WHERE App_Id=?;
        """
        app_values = (
            updated_app_name, updated_genre, app_id
        )
        c.execute(update_app_query, app_values)

        # Update developers table
        if not dev_data.empty:
            update_dev_query = """
            UPDATE developers
            SET Developer=?
            WHERE Developer_Id=?;
            """
            dev_values = (updated_dev_name, existing_app_data.iloc[0]['Developer_Id'])
            c.execute(update_dev_query, dev_values)

        # Update pricing table
        update_pricing_query = """
        UPDATE pricing
        SET Price=?
        WHERE App_id=?;
        """
        pricing_values = (updated_price, app_id)
        c.execute(update_pricing_query, pricing_values)

        conn.commit()
        conn.close()

        st.success("App updated successfully!")

# Function to read an existing app by app name
def read_app():

    # User inputs the name of the app to read
    app_name_to_read = st.text_input("App name to read")

    # Retrieve and display the app data
    existing_app_data = read_data()[read_data()['App_name'] == app_name_to_read]

    if existing_app_data.empty:
        st.warning("App not found. Enter a valid App Name.")
        return

    # Display data for the application, developer, and pricing
    st.markdown('<h5 style="color: #FFFFFF;">Application Information</h5>', unsafe_allow_html=True)
    st.dataframe(existing_app_data)

    # Fetch and display developer information
    developer_id = existing_app_data.iloc[0]['Developer_Id']
    dev_data = read_developer(developer_id)

    if not dev_data.empty:
        st.markdown('<h5 style="color: #FFFFFF;">Developer Information</h5>', unsafe_allow_html=True)
        st.dataframe(dev_data)

    # Fetch and display pricing information
    pricing_data = read_pricing(existing_app_data.iloc[0]['App_Id'])
    if not pricing_data.empty:
        st.markdown('<h5 style="color: #FFFFFF;">Pricing Information</h5>', unsafe_allow_html=True)
        st.dataframe(pricing_data)

    # Confirm reading
    if st.button("Read App"):
        st.success("App read successfully!")

# Function to retrieve developer information based on a developer ID
def read_developer(developer_id):

    conn = sqlite3.connect('DiscoverEase.db')
    dev_query = """
    SELECT * FROM developers
    WHERE Developer_Id=?;
    """
    dev_data = pd.read_sql_query(dev_query, conn, params=(developer_id,))
    conn.close()

    return dev_data

# Function to retrieve pricing information for a specific app based on its app ID
def read_pricing(app_id):

    conn = sqlite3.connect('DiscoverEase.db')
    pricing_query = """
    SELECT * FROM pricing
    WHERE App_id=?;
    """
    pricing_data = pd.read_sql_query(pricing_query, conn, params=(app_id,))
    conn.close()

    return pricing_data

# Function to delete an existing app
def delete_app():
    st.markdown('<h5 style="color: #FFFFFF;">Delete an Existing App</h5>', unsafe_allow_html=True)
   
    # Get user input for deleting an app
    app_id_to_delete = st.text_input("App ID to Delete")

    # Retrieve and confirm the app to be deleted
    existing_app_data = read_data()[read_data()['App_Id'] == app_id_to_delete]

    if existing_app_data.empty:
        st.warning("App not found. Enter a valid App ID.")
        return
    
    st.dataframe(existing_app_data)

    # Perform deletion upon confirmation
    if st.button("Delete App"):
        conn = sqlite3.connect('DiscoverEase.db')
        c = conn.cursor()

        # Delete from pricing, developers, and applications tables

        # Delete from pricing table
        delete_pricing_query = """
        DELETE FROM pricing
        WHERE App_id=?;
        """
        c.execute(delete_pricing_query, (app_id_to_delete,))

        # Fetch developer ID from the existing app data
        developer_id = existing_app_data.iloc[0]['Developer_Id']

        # Delete from developers table
        delete_dev_query = """
        DELETE FROM developers
        WHERE Developer_Id=?;
        """
        c.execute(delete_dev_query, (developer_id,))

        # Delete from applications table
        delete_app_query = """
        DELETE FROM applications
        WHERE App_Id=?;
        """
        c.execute(delete_app_query, (app_id_to_delete,))

        conn.commit()
        conn.close()

        st.success("App and related records deleted successfully!")

# Function to read data from the applications table in the SQLite database
def read_data():

    conn = sqlite3.connect('DiscoverEase.db')
    df = pd.read_sql_query("SELECT * FROM applications;", conn)
    conn.close()
    return df

# Function to display top developers based on the number of apps developed
def top_developers():

    conn = sqlite3.connect('DiscoverEase.db')
    top_dev_df = pd.read_sql_query("SELECT Developer, total_Apps FROM TopDevelopers ORDER BY Total_Apps DESC LIMIT 10;", conn)
    conn.close()
    
    # Create a bar graph using Plotly Express to visualize top developers
    fig = px.bar(
    top_dev_df, 
    x='Developer', 
    y='total_apps',
    labels={'total_apps': 'Total Apps Developed', 'Developer': 'Developer Name'},
    template='plotly_dark', 
    color_discrete_sequence=['#fac002']
    )
    
    # Display the bar graph in the Streamlit app
    st.markdown('<h5 style="color: #FFFFFF;">Top Developers by Total Apps Developed</h5>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    
# Function to display free applications filtered by genre
def free_applications(genre):

    conn = sqlite3.connect('DiscoverEase.db')
    query = """
    SELECT a.App_name, d.Developer 
    FROM applications AS a 
    JOIN pricing AS p ON a.App_Id = p.App_Id 
    JOIN developers AS d ON a.Developer_Id = d.Developer_Id 
    WHERE p.Price = 0.0 AND a.Genre = ? 
    LIMIT 15;
    """
    free_apps_df = pd.read_sql_query(query, conn, params=(genre,))
    conn.close()

    # Display the free applications in the Streamlit app
    st.markdown(f'<h5 style="color: #FFFFFF;">Free Applications Based on {genre} Genre</h5>', unsafe_allow_html=True)
    st.dataframe(free_apps_df)

# Function to display top-rated apps by genre
def top_rated_apps_by_genre(genre):

    conn = sqlite3.connect('DiscoverEase.db')
    query = f"SELECT * FROM TopRatedAppsByGenre WHERE genre = '{genre}' LIMIT 10;"
    top_rated_df = pd.read_sql_query(query, conn)
    conn.close()

    # Display top-rated apps by genre in the Streamlit app
    st.subheader(f"Top Rated {genre} Apps")
    st.dataframe(top_rated_df)

# Main function to execute the Streamlit app
def main():
    
    # Read and display basic application data from the database
    app_data = read_data()

    st.markdown('<h5 style="color: #FFFFFF;">Sampled App Data</h5>', unsafe_allow_html=True)
    st.dataframe(app_data.head(10))  # Display only top 10 rows

    # Sidebar for user interactions to filter and display data
    st.sidebar.header("Explore To Discover")

    # Filter by Genre
    selected_genre = st.sidebar.selectbox("Select Genre", app_data['Genre'].unique())
    genre_filtered_df = app_data[app_data['Genre'] == selected_genre]

    # Filter by Average User Rating
    min_rating = st.sidebar.slider("Minimum Average User Rating", min_value=0, max_value=5, value=3)
    rating_filtered_df = genre_filtered_df[genre_filtered_df['Avg_user_rating'] >= min_rating]

    # Filter by Size
    min_size = st.sidebar.slider("Minimum Size (MB)", min_value=0.0, max_value=500.0, value=0.0)
    size_filtered_df = rating_filtered_df[rating_filtered_df['Size'] >= min_size]

    # Display the final filtered results
    st.markdown('<h5 style="color: #FFFFFF;">Top 10 Apps based on Filters</h5>', unsafe_allow_html=True)
    st.dataframe(size_filtered_df.head(10))

    # Search functionality in the sidebar
    search_term = st.sidebar.text_input("Search by App Name")
    if search_term:
        search_result_df = size_filtered_df[size_filtered_df['App_name'].str.contains(search_term, case=False)]
        st.subheader('Search results')
        st.table(search_result_df.head(10))

    st.markdown('<h3 style="color: #FFFFFF;">Additional Information</h3>', unsafe_allow_html=True)
    
    # Additional Information Section
    st.sidebar.header("Additional Information")

   # Display top developers
    st.sidebar.subheader("Top Developers")
    top_developers()

    # Display free applications based on the selected genre
    st.sidebar.subheader("Free Applications")
    free_applications(selected_genre)

    # CRUD Operations Section
    st.sidebar.header("CRUD Operations Section")
    st.sidebar.subheader("Create an App")
    st.sidebar.subheader("Read an App Details")
    st.sidebar.subheader("Update an App Details")
    st.sidebar.subheader("Delete an App")
    
    st.markdown('<h3 style="color: #FFFFFF;">CRUD Operations</h3>', unsafe_allow_html=True)
    selected_action = st.selectbox("Select an action", ["Create App", "Update App", "Read App", "Delete App"])

# Call the corresponding function based on the selected action
    if selected_action == "Create App":
        create_app()
    elif selected_action == "Update App":
        update_app()
    elif selected_action == "Read App":
        read_app()
    elif selected_action == "Delete App":
        delete_app()

# Execute the main function if the script is run directly
if __name__ == "__main__":
    main()
