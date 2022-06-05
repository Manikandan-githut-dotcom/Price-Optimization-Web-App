# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 11:55:38 2022

@author: Manikandan
"""
import pandas as pd
import numpy as np
import streamlit as st
import pickle

st.set_page_config(page_title= "Price Optimization Webpage", layout= "centered", page_icon=":chart_with_upwards_trend:")

def main():
    st.title("WELCOME TO PRICE OPTIMIZATION!")
    html_temp = """
    <div style="background-color:#025246 ;padding:10px">
    <h2 style="color:white;text-align:center;">The Price Optimization App</h2>
    </div>
    """
    st.markdown(html_temp, unsafe_allow_html=True)
    
    # header
    st.header("The Optimized Prices for Retail Products")
   
    # sub header
    st.subheader("To know the Optimal Price of your Product: ")

    # loading the pickle files
    data = pickle.load(open('data.pkl','rb'))
    Products = pickle.load(open('Products.pkl','rb'))
    Zone = pickle.load(open('Zone.pkl','rb'))

    # Name of product as input
    Product = st.selectbox("Select One Product: ", (Products.values))

    # print the selected zone
    st.write("Selected Product:", Product)

    # select box
    Zone = st.selectbox("Select Zone: ", (Zone.values))
    # print the selected zone
    st.write("Selected Zone:", Zone)

    # MRP as input
    MRP = st.number_input("Enter MRP:", min_value = 0.399709302, max_value = 4765.472527)

    #print the MRP
    st.write("Entered MRP:", MRP)

    df = data.loc[data['NAME'] == Product,: ]


    def get_optimal_price(data):
        S = []

        for i in np.arange(MRP/2, MRP, 0.01):
            S.append(i)

        intercept = df['Intercept'].values[0]
        spcoef = df['SP_coeff'].values[0]
        uccoef = df['Unitcost_coeff'].values[0]
        cost = df['Unit_cost'].values[0]
        gst = df['Unit_gst'].values[0]
        N = []
        Rev = []
        Dis = []
        Disper = []

        for p in S:
            nsu = (intercept) + (spcoef*p) + (uccoef*cost)
            N.append(nsu)
            # Profit function
            rev = nsu*(p - cost - gst)
            Rev.append(rev)
            dis = MRP - p
            disper = dis/MRP *100
            Dis.append(dis)
            Disper.append(disper)
            
        profit = pd.DataFrame({'NSU': N, 'Price': S, 'Revenue': Rev, 'Discount': Dis, 'Discount%': Disper })
        
        #plt.plot(profit['Price'], profit['Revenue'])
        #plt.xlabel('Selling_Price')
        #plt.ylabel('Revenue')
        #plt.axhline(y = 0, linestyle = 'dashed')
        #plt.show()  

        optimal_price = np.where(profit['Revenue'] == profit['Revenue'].max())[0][0]
        maximum_profit = profit.iloc[[optimal_price]]
        return maximum_profit
        
     
    optimized_price = {}
    optimized_price[Product] = get_optimal_price(df)

    if st.button('Get Optimal Price'):
        maximum_profit = get_optimal_price(df)
        st.write("The Optimized Price for Your Product: ", maximum_profit)

if __name__=='__main__':
    main()
    

    

