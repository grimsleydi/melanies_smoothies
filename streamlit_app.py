import streamlit as st
from snowflake.snowpark.functions import col
import pandas
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
try:
    cnx = st.connection("snowflake")
    session = cnx.session()
except Exception as e:
    st.error(f"Failed to connect to Snowflake: {str(e)}")

# Get fruit options
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    # st.dataframe(data=my_dataframe, use_container_width = True)
    # st.stop()
    pd_df=my_dataframe.to_pandas()
    st.dataframe(pd_df)
    st.stop()
    # fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()
except Exception as e:
    st.error(f"Error retrieving fruit options: {str(e)}")
    fruit_options = []

# Multi-select for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_options, max_selections=5)

# Display chosen ingredients
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' ' 
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    st.write("Ingredients chosen:", ingredients_string)
else:
    ingredients_string = ''

# Submit order
time_to_insert = st.button('Submit Order')
if time_to_insert:
    if not name_on_order:
        st.error("Please enter a name for your Smoothie.")
    elif not ingredients_list:
        st.error("Please select at least one ingredient.")
    else:
        try:
            # Construct the SQL query using string interpolation
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        except Exception as e:
            st.error(f"An error occurred while submitting your order: {str(e)}")



