# interface
import streamlit as st
# preprocessing and computations
import pandas as pd
import numpy as np
import os
import json
import requests
from streamlit_lottie import st_lottie

# ===================================================================================
st.set_page_config(
    page_title="Business app",
    page_icon="something"
)
url = requests.get(
    "https://assets5.lottiefiles.com/packages/lf20_49rdyysj.json")
# Creating a blank dictionary to store JSON file,
# as their structure is similar to Python Dictionary
url_json = dict()
  
if url.status_code == 200:
    url_json = url.json()
else:
    print("Error in the URL")  

st_lottie(url_json,
          # change the direction of our animation
          reverse=True,
          # height and width of animation
          height=300,  
          width=650,
          # speed of animation
          speed=1,  
          # means the animation will run forever like a gif, and not as a still image
          loop=True,  
          # quality of elements used in the animation, other values are "low" and "medium"
          quality='high',
           # THis is just to uniquely identify the animation
          key='buisness' 
          )
st.title(":blue[Inputs Page]")
# ===================================================================================
file1 = st.file_uploader("Store", type=['xlsx'])
file2 = st.file_uploader("Product Masters", type=['xlsx'])
file3 = st.file_uploader("Sales", type=['xlsx'])
file4 = st.file_uploader("Budget", type=['xlsx'])
stockInput = st.file_uploader("Stock", type=['xlsx'])
ReOrderInput = st.file_uploader("Re-Ordering Constraints", type=['xlsx'])


def store_ag(store, product, sales, budget):
    store_df = pd.read_excel(store)
    prod_mas_df = pd.read_excel(product)
    sales_df = pd.read_excel(sales)
    budget_df = pd.read_excel(budget)

    sales_merged_df = pd.merge(sales_df, prod_mas_df, on="sku", how='left')
    sales_merged_df['month_year'] = sales_merged_df['day(yyyy-mm-dd)'].dt.to_period('M')

    sales_merged_df = sales_merged_df.drop(['day(yyyy-mm-dd)', 'sku', 'style', 'size', 'mrp'], axis=1)

    sales_grouped_df = sales_merged_df.groupby(
        ['store_id', 'Atttribute1', 'Atttribute2', 'Atttribute3', 'Atttribute4', 'Atttribute5', 'Atttribute6',
         'Atttribute7', 'Atttribute8', 'month_year']).agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()

    asp_grouped_df = sales_merged_df.groupby(
        ['store_id', 'Atttribute1', 'Atttribute2', 'Atttribute3', 'Atttribute4', 'Atttribute5', 'Atttribute6',
         'Atttribute7', 'Atttribute8']).agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()

    distinct_month_year_df = sales_grouped_df[['month_year']].drop_duplicates()

    distinct_attribute_df = sales_grouped_df[
        ['store_id', 'Atttribute1', 'Atttribute2', 'Atttribute3', 'Atttribute4', 'Atttribute5', 'Atttribute6',
         'Atttribute7', 'Atttribute8']].drop_duplicates()

    distinct_month_year_df['key'] = 1
    distinct_attribute_df['key'] = 1

    cross_join_df = pd.merge(distinct_attribute_df, distinct_month_year_df, on='key')

    cross_join_df.drop('key', axis=1, inplace=True)

    final_df = pd.merge(cross_join_df, sales_grouped_df,
                        on=['store_id', 'Atttribute1', 'Atttribute2', 'Atttribute3', 'Atttribute4', 'Atttribute5',
                            'Atttribute6', 'Atttribute7', 'Atttribute8', 'month_year'], how='left')

    final_df = final_df.fillna(0)

    final_df = final_df.sort_values(by='month_year')

    def weighted_average(group):
        weights = np.arange(len(group)) + 1
        weighted_sum = np.sum(group['revenue'] * weights)
        total_weight = np.sum(weights)
        return weighted_sum / total_weight

    weighted_avg_df = final_df.groupby(
        ['store_id', 'Atttribute1', 'Atttribute2', 'Atttribute3', 'Atttribute4', 'Atttribute5', 'Atttribute6',
         'Atttribute7', 'Atttribute8']).apply(weighted_average).reset_index(name='weighted_average_revenue')

    store_agg_df = weighted_avg_df.groupby('store_id')['weighted_average_revenue'].sum().reset_index()

    wei_df = pd.merge(weighted_avg_df, store_agg_df, on='store_id', how='left')

    wei_df['weighted_average_revenue_x'] = pd.to_numeric(wei_df['weighted_average_revenue_x'], errors='coerce')
    wei_df['weighted_average_revenue_y'] = pd.to_numeric(wei_df['weighted_average_revenue_y'], errors='coerce')

    wei_df['final rev mix'] = wei_df['weighted_average_revenue_x'] / wei_df['weighted_average_revenue_y']

    asp_grouped_df['forecasted_asp'] = asp_grouped_df['revenue'] / asp_grouped_df['quantity']

    semi_final_df = pd.merge(wei_df, asp_grouped_df,
                             on=['store_id', 'Atttribute1', 'Atttribute2', 'Atttribute3', 'Atttribute4', 'Atttribute5',
                                 'Atttribute6', 'Atttribute7', 'Atttribute8'], how='left')

    semi_final_df = pd.merge(semi_final_df, budget_df, on=['store_id'], how='left')

    semi_final_df['forecasted_revenue'] = (semi_final_df['budget'] * semi_final_df['final rev mix'])
    semi_final_df['forecasted_quantity'] = round(semi_final_df['forecasted_revenue'] / semi_final_df['forecasted_asp'])

    Revenue_split_output = semi_final_df[
        ['store_id', 'Atttribute1', 'Atttribute2', 'Atttribute3', 'Atttribute4', 'Atttribute5', 'Atttribute6',
         'Atttribute7', 'Atttribute8', 'forecasted_asp', 'forecasted_revenue', 'forecasted_quantity']]

    Revenue_split_output = Revenue_split_output[Revenue_split_output['forecasted_quantity'] > 0]
    # %%
    st.write("Output computed successfully, Preparing downloadable file now....")
    return Revenue_split_output


# ===================================================================================
if st.button("Calculate Store AG"):
    if file1 and file2 and file3 and file4 is not None:
        df = store_ag(file1, file2, file3, file4)

        # Write data to Excel file
        with pd.ExcelWriter('store_ag_output.xlsx') as writer:
            df.to_excel(writer, index=False)

        # Create the download button
        with open('store_ag_output.xlsx', 'rb') as f:
            bytes_data = f.read()
            st.download_button(label='Download Store AG Output', data=bytes_data, file_name='store_ag_output.xlsx',
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.error("Please upload relevant files first")



