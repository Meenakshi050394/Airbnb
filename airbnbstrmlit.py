import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
import mysql.connector


# --------------------------------------------------Logo & details on top

icon = Image.open("C:/Users/HP/Desktop/Data Scientist/project/airbnb_logo.png")
st.set_page_config(page_title= "Airbnb Analysis | By Meenakshi.H",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded")

        #------------------------------------------------------------------HEADER common to all menu
col,coll = st.columns([3,2],gap="small")
    
with coll:
    st.markdown("""
                    <style>
                    .centered-text {
                        text-align: center;
                        font-style:italic;
                        font-weight: bold;
                        font-size: 120px; 
                        pointer-events: none;
                    }
                    </style>
                    <div class="centered-text">
                        Airbnb
                    </div>
                    """, unsafe_allow_html=True)

    
opt = option_menu(menu_title=None, 
                       options=["Home","Insights","Explore Data","About"],
                icons=["house","graph-up-arrow","bar-chart-line", "exclamation-circle"],
                default_index=0,
                orientation='horizontal',
                styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#fa5252"},
                        "nav-link-selected": {"background-color": "#fa5252"}})
#------------------------------------HOME
if opt=="Home":

    st.write(" ") 
    st.write(" ")     
    st.markdown("### :red[*OVERVIEW* ]")
    st.markdown("### *This project aims to analyze Airbnb data & perform data cleaning and preparation, develop interactive geospatial visualizations, and create dynamic plots to gain insights into pricing variations, availability patterns, and location-based trends in the Airbnb marketplace.*")
    col1,col2=st.columns([3,2],gap="large")
    with col1:
        st.markdown("### :red[*DOMAIN* ] ")
        st.markdown(" ### *Travel Industry, Property Management and Tourism* ")
        st.markdown("""
                    ### :red[*TECHNOLOGIES USED*]    
            
                    ###  *PYTHON*
                    ###  *DATA PREPROCESSING*
                    ### *EDA*
                    ### *PANDAS*
                    ### *VISUALIZATION*
                    ### *STREAMLIT GUI*
                    ### *POWERBI*
                    """)
    with col2:
            st.write(" ")
            
#---------------------------------------- DATA EXPLORATION
if opt=="Explore Data":
    st.write(" ")

    col,col1,col2,col3= st.columns([9,9,9,9],gap="medium")

    with col3:
        on = st.toggle("##### **Geo-spatial visualisation**")
        if on:
               
         #------------------------------------------------------------------How does the availability of listings change based on location?

            
        #SQL Connection
            
            #SQL Connection
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select country,price,number_of_reviews,market,availability_365,suburb,longitude,latitude from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1,columns=("Country","Price","Number_of_Reviews","Market","Availability_365","Suburb","Longitude","Latitude"))


            df_filtered = df[df['Availability_365'] < 365]
            fig = px.scatter_mapbox(df_filtered,lon="Longitude" , lat="Latitude", color="Availability_365",
                                    hover_name="Suburb", hover_data={"Suburb": True, "Market": True, "Country": True, "Availability_365": True, "Number_of_Reviews" : True, "Price" : True},
                                    color_continuous_scale=px.colors.sequential.Viridis,
                                    zoom=1,width=1300,height=700)
            fig.update_layout(mapbox_style="open-street-map", title="Listing Availability by Location")
            st.plotly_chart(fig)
      
            

            #-----------------------------------------------
            st.write("###### **Geospatial Distribution of Listings** ")

             #SQL Connection
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select country,price,number_of_reviews,accommodates,name,longitude,latitude,availability_365,review_scores from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1,columns=("Country","Price","Number_of_Reviews","Accommodates","Name","Longitude","Latitude","Availability_365","Review_scores"))

            fig = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', color='Price', size='Accommodates',
                                    color_continuous_scale= "Pinkyl",hover_name='Name',range_color=(0,1000), mapbox_style="carto-positron",
                                    zoom=1)
                

            fig.update_traces(hovertemplate='<b>%{hovertext}</b><br><br>Price: %{marker.color}<br>Accommodates: %{marker.size}<br>Country: %{customdata[0]}<br>No_of_Reviews: %{customdata[1]}<br>Review_scores: %{customdata[2]}<br>Availability: %{customdata[3]}',
                        customdata=df[['Country', 'Number_of_Reviews', 'Review_scores','Availability_365']])
            fig.update_layout(width=1250,height=800, title='Geospatial Distribution of Listings')
            fig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[
                {
                    "below": 'traces',
                    "sourcetype": "raster",
                    "sourceattribution": "United States Geological Survey",
                    "source": [
                        "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    ]
                }
            ])
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig)

            #------------------------------------------------------------------Are there any spatial clusters of high-priced listings?

            #SQL Connection
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select country,price,longitude,latitude,suburb from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1,columns=("Country","Price","Longitude","Latitude","Suburb"))
                     
            df = df.dropna(subset=['Price'])
            X = df[['Latitude', 'Longitude', 'Price']]
            kmeans = KMeans(n_clusters=5, random_state=42)
            df['cluster'] = kmeans.fit_predict(X)
            fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color="cluster",
                                    hover_name="Suburb", hover_data=["Price"],
                                    color_continuous_scale=px.colors.qualitative.Dark24,
                                    zoom=1,width=1250,height=700)

            fig.update_layout(mapbox_style="open-street-map", title="Spatial Clusters of High-Priced Listings")
            st.plotly_chart(fig)

      
#------------------------------------------------------------------------------------------------------------ Price Analysis  

    with col:
        on = st.toggle("##### **Price Analysis**")

        if on:
            
            st.write(" ")
# How does the average price vary by property type?

#SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select property_type,price from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Property_Type", "Price"])

            avg_price_by_type = df.groupby("Property_Type")["Price"].mean()
            fig = px.line(
                avg_price_by_type.reset_index(),
                x="Property_Type",
                y="Price",
                title="Average Price by Property Type in Airbnb Data",width=1300,height=700,
                labels={"Property_Type": "Property Type", "Price": "Average Price"},
            )
            fig.update_traces(mode='markers+lines') 
            fig.update_layout(xaxis_title='Property Type', yaxis_title='Average Price')
            st.plotly_chart(fig)

    # Is there a difference in price between superhost and regular host listings?


    #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select host_is_superhost,price from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Host_is_Superhost", "Price"])

            avg_price_by_host_type = df.groupby("Host_is_Superhost")["Price"].mean()
            fig = px.pie(
            avg_price_by_host_type.reset_index(), 
            values="Price",
            names="Host_is_Superhost",
            title="Average Price Distribution by Host Type (Superhost vs. Regular)",width=1300,height=700,
            hole=0.5 
        )
            fig.update_traces(textinfo="percent+label", textposition="inside")
            st.plotly_chart(fig)

# How does the price vary across different neighborhoods or cities?

            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select host_neighbourhood,price from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Host_Neighbourhood", "Price"])

         
            avg_price_by_location = df.groupby("Host_Neighbourhood")["Price"].mean()  

            fig = px.bar(
                avg_price_by_location.reset_index(), 
                x="Host_Neighbourhood", 
                y="Price",
                color="Host_Neighbourhood",width=1410,height=700,
                title="Average Price by Host_neighbourhood (or City)",
                labels={"Host_Neighbourhood": "Host_neighbourhood", "Price": "Average Price"},
                 
            )
            st.plotly_chart(fig)

# how review scores influence listing prices the most?

            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select review_scores,price from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Review_scores", "Price"])
        
            review_scores_prices = df.groupby('Review_scores')['Price'].mean().reset_index()
            review_scores_prices['Price'] = review_scores_prices['Price'].round(3)

            figg = px.scatter(review_scores_prices, x='Review_scores', y='Price', title='Review Scores vs. Average Price',width=1300,height=700,color="Price",color_continuous_scale= "RdBu")
            st.plotly_chart(figg)
            
# How does the price change based on the cancellation policy?

            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select cancellation_policy,price from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Cancellation_Policy", "Price"])
          
            canc_pol= df['Cancellation_Policy'].unique()
            fig = make_subplots(rows=1, cols=len(canc_pol), subplot_titles=canc_pol)
            for i, policy in enumerate(canc_pol, start=1):
                data_for_policy = df[df['Cancellation_Policy'] == policy]
                fig.add_trace(go.Histogram(x=data_for_policy['Price'], name=policy), row=1, col=i)

            fig.update_layout(title='Distribution of Prices by Cancellation Policy',width=1410,height=700)
            fig.update_xaxes(title_text="Price")
            fig.update_yaxes(title_text="Frequency")
            st.plotly_chart(fig)

#------------------------------------------------------------------------- Avalaibility Analysis

    with col1:
        on = st.toggle("##### **Availability Analysis**")

        if on:
           
            st.write(" " )
 # How does the availability of listings vary by property type?

            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select property_type,availability_365 from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Property_type", "Availability_365"])
           
            aaa = df.groupby("Property_type")["Availability_365"].mean()
            fig = px.bar(aaa.reset_index(), x="Property_type", y="Availability_365", color="Availability_365",color_continuous_scale="Rdpu",
                        labels={'x': 'Property Type', 'y': 'Average Availability (Days)'},
                        title='Average Availability by Property Type')
            fig.update_layout(width=1300, height=700)
            fig.update_xaxes(tickangle=45)

            st.plotly_chart(fig)

# What is the overall availability trend of Airbnb listings over time? 

            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select _id,availability_365 from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Id", "Availability_365"])

            df1 = df.drop(columns=['Id'])
            overall_availability = df.mean()
            overall_availability ['Availability_365'] = overall_availability ['Availability_365'].round(3)
            fig = px.pie(names=overall_availability.index, values=overall_availability.values,
                        title='Overall Availability Trend of Airbnb Listings',width=1300,height=700)
            st.plotly_chart(fig)

#---------------------------------------------------------------------------------

# How does the availability of listings change based on the cancellation policy?

            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select cancellation_policy,availability_365,price from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Cancellation_policy", "Availability_365","Price"])
           
            avg_data_by_cancellation_policy = df.groupby('Cancellation_policy').agg({'Availability_365': 'mean', 'Price': 'mean'}).reset_index()
            avg_data_by_cancellation_policy ['Availability_365'] = avg_data_by_cancellation_policy ['Availability_365'].round(3)

            fig = px.scatter_3d(avg_data_by_cancellation_policy, x='Cancellation_policy', z='Availability_365', y='Price',
                                title='Average Availability and Price by Cancellation Policy',width=1000,height=700,color="Availability_365",color_continuous_scale="Plotly3",
                                labels={'Cancellation_policy': 'Cancel Pol', 'Availability_365': 'Avg Avail', 'Price': 'Price'})

            st.plotly_chart(fig)

# Is there a relationship between the availability of listings and the number of reviews?

             #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select number_of_reviews,availability_365 from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Number_of_reviews", "Availability_365"])

            availability_reviews_df = df[['Availability_365', 'Number_of_reviews']]
            correlation_matrix = availability_reviews_df.corr()
            fig = px.imshow(correlation_matrix.values,  
                            labels=dict(x='Availability', y='Number of Reviews', color='Correlation'),
                            x=correlation_matrix.columns,
                            y=correlation_matrix.columns,
                            color_continuous_scale='RdBu',
                            title='Correlation Heatmap between Availability and Number of Reviews',width=1300,height=700,)

            st.plotly_chart(fig)

# What is the average availability for different room types?

            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select room_type,availability_365 from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Room_type", "Availability_365"])


            avg_availability_by_room_type = df.groupby('Room_type')['Availability_365'].mean().reset_index()
            avg_availability_by_room_type ['Availability_365'] = avg_availability_by_room_type ['Availability_365'].round(3)

            fig = px.pie(avg_availability_by_room_type, values='Availability_365', names='Room_type',
                                title='Average Availability by Room Type', hole=0.4,width=1300,height=700,)
            st.plotly_chart(fig)

    
# __________________________________Location Analysis
    with col2:
        on = st.toggle("##### **Location Analysis**")

        if on:
            
 # ---------------------------------------------------------------------  diff countries based on avg review score 
    #-----------------------------------------------------diff countries based on their avg book price

             #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select country,review_scores,price from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Country", "Review_scores", "Price"])

            
            avg_review_score_by_country = df.groupby('Country')['Review_scores'].mean().reset_index()
            avg_review_score_by_country = avg_review_score_by_country.sort_values(by='Review_scores')
            avg_price_by_country = df.groupby('Country')['Price'].mean().reset_index()
            avg_price_by_country = avg_price_by_country.sort_values(by='Price', ascending=False)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=avg_review_score_by_country['Country'], y=avg_review_score_by_country['Review_scores'],
                                name='Average Review Score', marker_color='skyblue'))
            fig.add_trace(go.Bar(x=avg_price_by_country['Country'], y=avg_price_by_country['Price'],
                                name='Average Booking Price', marker_color='lightgreen'))
            fig.update_layout(barmode='group', title='Average Review Score and Booking Price by Country',width=1300,height=700,
                            xaxis_tickangle=-45, xaxis_title='Country', yaxis_title='Value')
            st.plotly_chart(fig)

#-------------------------------------------What are the top amenities offered in listings across different neighborhoods?

            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select amenities from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Amenities"])



            amenities = df['Amenities'].str.replace('[{}]', '', regex=True).str.replace('"', '', regex=True).str.split(',')

            # Count the occurrences of each amenity
            amenity_counts = {}
            for amns in amenities:
                for amenity in amns:
                    amenity = amenity.strip()
                    if amenity in amenity_counts:
                        amenity_counts[amenity] += 1
                    else:
                        amenity_counts[amenity] = 1

            # Sort the amenities by count and select the top N
            sorted_amenities = sorted(amenity_counts.items(), key=lambda x: x[1], reverse=True)
            top_n = 10
            top_amenities = dict(sorted_amenities[:top_n])

            # Create the pie chart
            fig = go.Figure(data=[go.Pie(
                labels=list(top_amenities.keys()), 
                values=list(top_amenities.values()),
                hole=0.4,
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}',
                name=''  
            )])

            fig.update_traces(
                marker=dict(colors=px.colors.qualitative.Pastel)
            )

            fig.update_layout(
                title='Top Amenities Offered in Listings Across Different Neighborhoods',
                width=1300,
                height=700,
              
            )

            # Display the chart using Streamlit
            st.plotly_chart(fig)
            #----------------------------------------Are there any neighborhoods with a significantly higher average review score than others?

             #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select suburb,review_scores from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Suburb","Review_scores"])


            avg_review_score_by_neighborhood = df.groupby('Suburb')['Review_scores'].mean().reset_index()
            top_10_neighborhoods = avg_review_score_by_neighborhood.sort_values(by='Review_scores', ascending=False).head(10)
            top_10_neighborhoods['Rank'] = 'Top 10'
            least_10_neighborhoods = avg_review_score_by_neighborhood.sort_values(by='Review_scores', ascending=True).head(10)
            least_10_neighborhoods['Rank'] = 'Least 10'
            merged_neighborhoods = pd.concat([top_10_neighborhoods, least_10_neighborhoods])
            fig = px.bar(merged_neighborhoods, x='Suburb', y='Review_scores', color='Rank',
                        labels={'Review_scores': 'Average Review Score'},
                        title='Top and Least 10 Neighborhoods by Average Review Score',width=1200,height=700,
                        color_discrete_sequence=px.colors.qualitative.Pastel)

            fig.update_layout(xaxis_title='Neighborhood', yaxis_title='Average Review Score')
            st.plotly_chart(fig)

#-----------------------------------------------------Are there any differences in the distribution of property types across neighborhoods?
            
            #SQL Connection
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
            )

            cursor = mydb.cursor(buffered=True)

            cursor.execute("select suburb,property_type from airbnb_info")
            mydb.commit()
            tb1 = cursor.fetchall()
            cursor.close()  
            df = pd.DataFrame(tb1, columns=["Suburb","Property_type"])
            
        
            property_type_distribution = df.groupby(['Suburb', 'Property_type']).size().reset_index(name='count')

            fig = px.scatter(property_type_distribution, x='Suburb', y='count', color='Property_type',
                            title='Distribution of Property Types Across Neighborhoods',width=1110,height=700,
                            labels={'count': 'Number of Listings', 'Suburb': 'Neighborhood'})
            fig.update_layout(xaxis_title='Neighborhood', yaxis_title='Number of Listings')
            st.plotly_chart(fig)

        
        

    #---------------------------------------- INSIGHTS
if opt=="Insights":
        st.markdown(
    """
    <style>
        .css-15qegpx {
            display: flex;
            justify-content: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

        analysis_type = st.radio(
             "#### *:red[Choose the Option to Visualize]*",
            ("###### ***:rainbow[Rough Analysis]***", "###### ***:rainbow[Top Charts]***")
        )

     #-----------------------------------------------------------------INSIGHTS 1ST TAB ROUGH ANALYSIS
        if analysis_type == "###### ***:rainbow[Rough Analysis]***":
                
                
        #------------------------------------------------------------- ( 1 )

                 #SQL Connection
                mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="airbnb"
                )

                cursor = mydb.cursor(buffered=True)

                cursor.execute("select property_type from airbnb_info")
                mydb.commit()
                tb1 = cursor.fetchall()
                cursor.close()  
                df = pd.DataFrame(tb1, columns=["Property_type"])
                
                property_type_counts = df['Property_type'].value_counts()

                fig = px.bar(property_type_counts, x=property_type_counts.index, y=property_type_counts.values,
                            labels={'x': 'Property Type', 'y': 'Count'},
                            title='Distribution of Property Types', width=1300,height=700)

                st.plotly_chart(fig)
                


            #------------------------------------------------------------- ( 2 )


                # SQL query to fetch data
                sql_query = """
                SELECT minimum_nights, maximum_nights, accommodates, bedrooms, beds, availability_365, price,
                    cleaning_fee, extra_people, guests_included, number_of_reviews, review_scores
                FROM airbnb_info
                """

                # Function to establish database connection and fetch data
                def get_airbnb_data():
                    try:
                        mydb = mysql.connector.connect(
                            host="127.0.0.1",
                            port="3306",
                            user="root",
                            password="root",
                            database="airbnb"
                        )
                        cursor = mydb.cursor(buffered=True)
                        cursor.execute(sql_query)
                        data = cursor.fetchall()
                        mydb.commit()
                        cursor.close()
                        mydb.close()
                        return data
                    except mysql.connector.Error as err:
                        print("Error connecting to database:", err)
                        st.error("Error connecting to database. Please check credentials or network connectivity.")
                        return None

                # Get data from database
                data = get_airbnb_data()

                if data is None:
                    st.stop()  # Stop Streamlit app if data retrieval fails

                # Create pandas DataFrame (handling potential empty data)
                if data:
                    df = pd.DataFrame(data, columns=[
                        "Minimum_nights", "Maximum_nights", "Accommodates", "Total_bedrooms", "Total_beds",
                        "Availability_365", "Price", "Cleaning_fee", "Extra_people", "Guests_included",
                        "Number_of_reviews", "Review_scores"
                    ])
                else:
                    st.error("No data found in the database. Please check the table or query.")
                    st.stop()

                # Data cleaning and selection

                #df.fillna(np.nan, inplace=True)  # Replace missing values with NaN
                selected_columns = ['Minimum_nights', 'Maximum_nights', 'Accommodates', 'Total_bedrooms',
                                'Total_beds', 'Availability_365', 'Price', 'Cleaning_fee', 'Extra_people',
                                'Guests_included', 'Number_of_reviews', 'Review_scores']
                
                for col in selected_columns:
                    df[col].replace('Not Specified', 0, inplace=True)

                # Check if all selected columns exist in the DataFrame
                if not all(col in df.columns for col in selected_columns):
                    missing_cols = set(selected_columns) - set(df.columns)
                    st.error(f"Some selected columns are missing in the DataFrame: {', '.join(missing_cols)}")
                    st.stop()

                # Correlation matrix and heatmap
                correlation_matrix = df[selected_columns].corr()
                fig = px.imshow(correlation_matrix,
                                labels=dict(x="Features", y="Features", color="Correlation"),
                                x=selected_columns,
                                y=selected_columns,
                                title='Correlation Heatmap of Airbnb Features',
                                width=1500, height=850,
                                # Customize color scale (optional)
                                color_continuous_scale='RdBu'  # Example color scale
                                )

                # Add annotations with rounded correlation values
                for i in range(len(selected_columns)):
                    for j in range(len(selected_columns)):
                        fig.add_annotation(x=selected_columns[i], y=selected_columns[j],
                                        text=str(round(correlation_matrix.iloc[j, i], 2)),
                                        showarrow=False, font=dict(color="black", size=10))

                fig.update_layout(annotations=dict(xref="x", yref="y"))
                st.plotly_chart(fig)


            # -------------------------------------------- ( 3 )

                 #SQL Connection
                mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="airbnb"
                )

                cursor = mydb.cursor(buffered=True)

                cursor.execute("select accommodates,price from airbnb_info")
                mydb.commit()
                tb1 = cursor.fetchall()
                cursor.close()  
                df = pd.DataFrame(tb1, columns=["Accommodates","Price"])

                avg_price_by_capacity = df.groupby('Accommodates')['Price'].mean().reset_index()
                fig = px.bar(avg_price_by_capacity, x='Accommodates', y='Price', 
                        color='Accommodates',width=1300, height=700,
                        labels={'Accommodates': 'Accommodation Capacity', 'Price': 'Average Price'},
                        title='Average Price by Accommodation Capacity',color_continuous_scale= "emrld")
                st.plotly_chart(fig)
            
            #----------------------------------------(4)

                 #SQL Connection
                mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="airbnb"
                )

                cursor = mydb.cursor(buffered=True)

                cursor.execute("select room_type from airbnb_info")
                mydb.commit()
                tb1 = cursor.fetchall()
                cursor.close()  
                df = pd.DataFrame(tb1, columns=["Room_type"])

                room_type_counts = df['Room_type'].value_counts()
                donut_df = pd.DataFrame({'Room Type': room_type_counts.index, 'Count': room_type_counts.values})
                fig = px.pie(donut_df, values='Count', names='Room Type', hole=0.4)
                fig.update_layout(
                    title='Distribution of Room Types',width=1100, height=700,
                    margin=dict(l=0, r=0, b=0, t=40)
                )
                st.plotly_chart(fig)

            #-------------------------------------------------------------------Which host verification method is the most popular among hosts?
               

                #SQL Connection
                mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="airbnb"
                )

                cursor = mydb.cursor(buffered=True)

                cursor.execute("select host_verifications from airbnb_info")
                mydb.commit()
                tb1 = cursor.fetchall()
                cursor.close()  
                df = pd.DataFrame(tb1, columns=["Host_verifications"])

                df['Host_verifications'] = df['Host_verifications'].fillna('')
                all_verifications = ', '.join(str(verification) for verification in df['Host_verifications'] if pd.notnull(verification))
                verifications_list = [verification.strip() for verification in all_verifications.split(',')]
                verifications_list = ['Undefined' if verification == '' else verification for verification in verifications_list]
                verification_counts = pd.DataFrame(verifications_list, columns=['Verification Method'])
                verification_counts = verification_counts['Verification Method'].value_counts().reset_index()
                verification_counts.columns = ['Verification Method', 'Count']
                fig = px.bar(
                    verification_counts, 
                    x='Verification Method', 
                    y='Count',
                    title='Popularity of Host Verification Methods',
                    width=1100, 
                    height=700, 
                    color='Verification Method',
                    labels={'Verification Method': 'Host Verification Method', 'Count': 'Number of Hosts'}
                )

                fig.update_layout(
                    xaxis_title='Verification Method', 
                    yaxis_title='Number of Hosts'
                )
                st.plotly_chart(fig)

                
 # ---------------------------------------------------  INSIGHTS 2ND TAB TOP CHARTS

        elif analysis_type =="###### ***:rainbow[Top Charts]***":
                
                title=st.selectbox("Shoot Your Choice",
                                    ["Choose a Title...",
                                     '1.Neighborhoods with the Highest Number of Listings',
                                     '2.Top 10 Most Expensive Neighborhoods',
                                     '3.Number of Available Listings in the Next 30 Days by City',
                                     '4.Top 10 Host IDs with Host Response Times',
                                     '5.Top 10 Countries with the Most Listings',
                                     '6.Top 10 Most Reviewed Listings',
                                     '7.Top 10 Property Types with the Highest Average Review Scores',
                                     '8.Top 10 Most Expensive Property Types by Price',
                                     '9.Top 10 Most Common Amenities Provided in Listings',
                                     '10.Distribution of Average Review Scores for Top Hosts',
                                     '11.Top 10 Most Popular Host Verification Methods'],
                                      index=0)
                
                if title=='1.Neighborhoods with the Highest Number of Listings':

                        #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select host_neighbourhood,host_listings_count from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Host_neighbourhood","Host_listings_count"])

            # Which neighborhoods have the highest number of listings?

                    neighborhood_counts = df['Host_neighbourhood'].value_counts().reset_index()
                    neighborhood_counts.columns = ['Host_neighbourhood', 'Host_listings_count']
                    neighborhood_counts = neighborhood_counts.sort_values(by='Host_listings_count', ascending=False)

                   
                    fig = px.bar(neighborhood_counts.head(10), x='Host_neighbourhood', y='Host_listings_count',
                                labels={'Host_neighbourhood': 'Neighborhood', 'Host_listings_count': 'Number of Listings'},
                                title='Neighborhoods with the Highest Number of Listings', width=1300,height=700,color='Host_listings_count',color_continuous_scale= "plasma")
                    
                    st.plotly_chart(fig)

                elif title=='2.Top 10 Most Expensive Neighborhoods':

                    # What are the top 10 most expensive neighborhoods in terms of average listing price?

                     #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select host_neighbourhood,price from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Host_neighbourhood","Price"])

                    avg_price_by_neighborhood = df.groupby('Host_neighbourhood')['Price'].mean().reset_index()
                    avg_price_by_neighborhood = avg_price_by_neighborhood.sort_values(by='Price', ascending=False)
                    top_10_expensive_neighborhoods = avg_price_by_neighborhood.head(10)

                    fig = px.pie(top_10_expensive_neighborhoods, values='Price', names='Host_neighbourhood',
                                title='Top 10 Most Expensive Neighborhoods', width=1300,height=700,
                                hole=0.4)  
                    st.plotly_chart(fig)

                elif title=='3.Number of Available Listings in the Next 30 Days by City':

                    #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select market,availability_30 from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Market","Availability_30"])


                    availability_30_by_city = df.groupby('Market')['Availability_30'].sum().reset_index()
                    availability_30_by_city_sorted = availability_30_by_city.sort_values(by='Availability_30', ascending=False)

                    fig = px.bar(availability_30_by_city_sorted, x='Market', y='Availability_30',color="Availability_30",color_continuous_scale='oryel',
                                title='Number of Available Listings for 30 Days over City', width=1300,height=700,
                                labels={'Market': 'City', 'Availability_30': 'Available'})

                    fig.update_layout(xaxis_title='City', yaxis_title='Available')
                    st.plotly_chart(fig)

                   
                elif title=='4.Top 10 Host IDs with Host Response Times':

                # ---------------------------------What are the top 10 most common host response times?

                    #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select host_id,host_response_time from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Host_id","Host_response_time"])

                    top_host_response_times = df.groupby(['Host_id', 'Host_response_time']).size().reset_index(name='Count')
                    top_host_response_times = top_host_response_times.sort_values(by='Count', ascending=False)
                    top_10_host_ids = top_host_response_times['Host_id'].head(10)
                    top_10_host_response_times = top_host_response_times[top_host_response_times['Host_id'].isin(top_10_host_ids)]
                    fig = px.line(top_10_host_response_times, x='Host_response_time', y='Count', color='Host_id', markers=True,
                                labels={'Host_response_time': 'Response Time', 'Count': 'Number of Responses', 'Host_id': 'Host ID'},
                                title='Top 10 Host IDs with Host Response Times', width=1300,height=700)

                    st.plotly_chart(fig)

                elif title=='5.Top 10 Countries with the Most Listings':

                     
                    # What are the top 10 countries with the most listings? 

                    #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select country,host_listings_count from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Country","Host_listings_count"])


                    listings_by_country = df['Country'].value_counts().reset_index()
                    listings_by_country.columns = ['Country', 'Host_listings_count']
                    listings_by_country = listings_by_country.sort_values(by='Host_listings_count', ascending=False)
                    top_10_countries = listings_by_country.head(10)

                    fig = px.bar(top_10_countries, x='Host_listings_count', y='Country', orientation='h',
                                labels={'Host_listings_count': 'Number of Listings', 'Country': 'Country'},
                                title='Top 10 Countries with the Most Listings', width=1300,height=700,color='Host_listings_count',color_continuous_scale='Purpor')

                    st.plotly_chart(fig)

                elif title=='6.Top 10 Most Reviewed Listings':

                    #--------------------------What are the top 10 most reviewed listings?

                    #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",                      
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select _id,number_of_reviews from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Id","Number_of_reviews"])

                    top_10_most_reviewed_listings = df.nlargest(10, 'Number_of_reviews')
                    fig = px.scatter(top_10_most_reviewed_listings, x='Id', y='Number_of_reviews',
                                    labels={'Id': 'Listing ID', 'Number_of_reviews': 'Number of Reviews'},
                                    title='Top 10 Most Reviewed Listings', width=1300,height=700,color='Number_of_reviews',color_continuous_scale='Aggrnyl')
                    st.plotly_chart(fig)

                elif title=='7.Top 10 Property Types with the Highest Average Review Scores':

                  #---------------------What are the top 10 property types with the highest average review scores? 

                    #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select property_type,review_scores from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Property_type","Review_scores"])

                    avg_review_scores_by_property_type = df.groupby('Property_type')['Review_scores'].mean().reset_index()
                    avg_review_scores_by_property_type = avg_review_scores_by_property_type.sort_values(by='Review_scores', ascending=False)
                    top_10_property_types = avg_review_scores_by_property_type.head(10)
                    fig = px.line(top_10_property_types, x='Property_type', y='Review_scores', markers=True,
                                labels={'Property_type': 'Property Type', 'Review_scores': 'Average Review Scores'},
                                title='Top 10 Property Types with the Highest Average Review Scores', width=1300,height=700)

                    st.plotly_chart(fig)

                elif title=='8.Top 10 Most Expensive Property Types by Price':

                # --------------------------------What are the top 10 most expensive property types by price ? 

                            #SQL Connection
                        mydb = mysql.connector.connect(
                        host="127.0.0.1",
                        port="3306",
                        user="root",
                        password="root",
                        database="airbnb"
                        )

                        cursor = mydb.cursor(buffered=True)

                        cursor.execute("select property_type,price from airbnb_info")
                        mydb.commit()
                        tb1 = cursor.fetchall()
                        cursor.close()  
                        df = pd.DataFrame(tb1, columns=["Property_type","Price"])

                        avg_price_by_property_type = df.groupby('Property_type')['Price'].mean().reset_index()
                        avg_price_by_property_type['Price'] = avg_price_by_property_type['Price'].round(3)
                        top_10_expensive_property_types = avg_price_by_property_type.sort_values(by='Price', ascending=False).head(10)
                        fig = px.bar(top_10_expensive_property_types, x='Property_type', y='Price',color="Price",color_continuous_scale='Pinkyl',
                                    title='Top 10 Most Expensive Property Types by Price', width=1300,height=700,
                                    labels={'Property_type': 'Property Type', 'Price': 'Average Price'})
                        st.plotly_chart(fig)

                        top_10_expensive_property_types = avg_price_by_property_type.sort_values(by='Price', ascending=False).head(10)
                        fig = px.bar(top_10_expensive_property_types, x='Property_type', y='Price',color="Price",color_continuous_scale='Pinkyl',
                                    title='Top 10 Most Expensive Property Types by Price', width=1300,height=700,
                                    labels={'Property_type': 'Property Type', 'Price': 'Average Price'})
                        st.plotly_chart(fig)

                elif title=='9.Top 10 Most Common Amenities Provided in Listings':

                #----------------------------------------What are the top 10 most common amenities provided in listings?

                    #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select amenities from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Amenities"])

                    all_amenities = ', '.join(df['Amenities'])
                    amenities_list = [amenity.strip() for amenity in all_amenities.split(',')]
                    amenity_counts = pd.Series(amenities_list).value_counts().reset_index()
                    amenity_counts.columns = ['Amenities', 'Count']

                    top_10_common_amenities = amenity_counts.head(10)

                    fig = px.pie(top_10_common_amenities, values='Count', names='Amenities',
                                title='Top 10 Most Common Amenities Provided in Listings', width=1300,height=700)
                    st.plotly_chart(fig)

                # ------------------------------------ Which city has the highest number of available listings in the next 30 days?

                elif title=='10.Distribution of Average Review Scores for Top Hosts':

                    #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select host_id,review_scores from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Host_id","Review_scores"])

                   
                    avg_review_scores_by_host = df.groupby('Host_id')['Review_scores'].mean().reset_index()
                    avg_review_scores_by_host = avg_review_scores_by_host.sort_values(by='Review_scores', ascending=False)
                    top_hosts = avg_review_scores_by_host.head(10)

                    fig = px.pie(top_hosts, values='Review_scores', names='Host_id',
                                title='Distribution of Average Review Scores for Top Hosts', width=1300,height=700,color='Host_id',
                                hole=0.4)  
                    st.plotly_chart(fig)

                elif title=="11.Top 10 Most Popular Host Verification Methods":


                #-----------------------------------------Which host verification method is the most popular among hosts?

                    #SQL Connection
                    mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    port="3306",
                    user="root",
                    password="root",
                    database="airbnb"
                    )

                    cursor = mydb.cursor(buffered=True)

                    cursor.execute("select host_verifications from airbnb_info")
                    mydb.commit()
                    tb1 = cursor.fetchall()
                    cursor.close()  
                    df = pd.DataFrame(tb1, columns=["Host_verifications"])


                    
                    df['Host_verifications'] = df['Host_verifications'].astype(str)
                    all_verifications = ', '.join(df['Host_verifications'])
                    verifications_list = [verification.strip() for verification in all_verifications.split(',')]
                    verification_counts = pd.Series(verifications_list).value_counts().reset_index()
                    verification_counts.columns = ['Verification Method', 'Count']
                    top_10_verification_methods = verification_counts.sort_values(by='Count', ascending=False).head(10)
                    fig = px.bar(top_10_verification_methods, x='Verification Method', y='Count', color="Count", 
                                color_continuous_scale='bluyl',
                                title='Top 10 Most Popular Host Verification Methods', width=1300, height=700,
                                labels={'Verification Method': 'Host Verification Method', 'Count': 'Number of Hosts'})

                    fig.update_layout(xaxis_title='Verification Method', yaxis_title='Number of Hosts')
                    st.plotly_chart(fig)
                                

if opt=="About":
    st.markdown("### :red[*AIRBNB* ] ")
    st.write(' ### *Airbnb is an online marketplace that connects people who want to rent out their property with people who are looking for accommodations,typically for short stays. Airbnb offers hosts a relatively easy way to earn some income from their property.Guests often find that Airbnb rentals are cheaper and homier than hotels.* ')
    st.write("")
    st.write(' ### *Airbnb Inc (Airbnb) operates an online platform for hospitality services.The company provides a mobile application (app) that enables users to list,discover, and book unique accommodations across the world.The app allows hosts to list their properties for lease, and enables guests to rent or lease on a short-term basis,which includes vacation rentals, apartment rentals, homestays, castles,tree houses and hotel rooms.* ')
    st.write(' ### *The company has presence in China, India, Japan, Australia, Canada, Austria, Germany, Switzerland, Belgium, Denmark, France, Italy, Norway, Portugal, Russia, Spain, Sweden, the UK, and others.Airbnb is headquartered in San Francisco, California, the US.* ')
    
   
    st.markdown("### :red[*BACKGROUND OF AIRBNB* ] ")
    st.write(' ### *Airbnb was born in 2007 when two Hosts welcomed three guests to their San Francisco home, and has since grown to over 4 million Hosts who have welcomed over 1.5 billion guest arrivals in almost every country across the globe.* ')
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    col11,col22=st.columns([2,3],gap="small")
    with col11:
         st.write(" ")
    #with col22:
         
      #st.image("airr.png")

    st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <a href="https://github.com/Meenakshi050394/Airbnb" style="color: violet; font-weight: bold; text-decoration: none; padding: 10px 20px; background-color: white; border: 2px solid violet; border-radius: 5px;">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)























