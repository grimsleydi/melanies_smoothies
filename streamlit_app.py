import streamlit as st
from snowflake.snowpark.functions import col

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
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
    fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()
except Exception as e:
    st.error(f"Error retrieving fruit options: {str(e)}")
    fruit_options = []

# Multi-select for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_options, max_selections=5)

# Display chosen ingredients
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    st.write("Ingredients chosen:", ingredients_string)
else:
    ingredients_string = ''

# Insert query
my_insert_stmt = (
    "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
    "VALUES (%s, %s)"
)

# Submit order
time_to_insert = st.button('Submit Order')
if time_to_insert:
    if not name_on_order:
        st.error("Please enter a name for your Smoothie.")
    elif not ingredients_list:
        st.error("Please select at least one ingredient.")
    else:
        try:
            session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        except Exception as e:
            st.error(f"An error occurred while submitting your order: {str(e)}")
