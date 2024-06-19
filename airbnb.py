import pandas as pd
import pymongo
import mysql.connector
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
pd.set_option('display.max_columns',None)

#Page Configuration

def streamlit_config():

    page_icon_url = r"C:/Users/HP/Desktop/Data Scientist/project/airbnb_logo.png"
    st.set_page_config(page_title='Airbnb',
                       page_icon=page_icon_url,
                       layout='wide')
    
    page_background_color = """

    <style>
    [data-testid=stHeader]
    {
    background: rgba(0,0,0,0);
    }

    </style>"""

    st.markdown(page_background_color,unsafe_allow_html=True)

    st.markdown(f'<h1 style="text-align: center;">Airbnb Analysis</h1>',
                unsafe_allow_html=True)
    

class data_collection:
    
    mydb = pymongo.MongoClient("mongodb://localhost:27017/")
    db = mydb['Airbnb']
    col = db['sample']

class data_preprocessing:

    def primary():

        data = []
        for i in data_collection.col.find( {}, {'_id':1,'listing_url':1,'name':1,'property_type':1,'room_type':1,'bed_type':1,
                                'minimum_nights':1,'maximum_nights':1,'cancellation_policy':1,'accommodates':1,
                                'bedrooms':1,'beds':1,'number_of_reviews':1,'bathrooms':1,'price':1,
                                'cleaning_fee':1,'extra_people':1,'guests_included':1,'images.picture_url':1,
                                'review_scores.review_scores_rating':1} ):
            data.append(i)

        df_1 = pd.DataFrame(data)
        df_1['images'] = df_1['images'].apply(lambda x: x['picture_url'])
        df_1['review_scores'] = df_1['review_scores'].apply(lambda x: x.get('review_scores_rating',0))

        # null value handling
        df_1['bedrooms'].fillna(0, inplace=True)
        df_1['beds'].fillna(0, inplace=True)
        df_1['bathrooms'].fillna(0, inplace=True)
        df_1['cleaning_fee'].fillna('Not Specified', inplace=True)
        df_1.isnull().sum()

        # data types conversion

        df_1['minimum_nights'] = df_1['minimum_nights'].astype(int)
        df_1['maximum_nights'] = df_1['maximum_nights'].astype(int)
        df_1['bedrooms'] = df_1['bedrooms'].astype(int)
        df_1['beds'] = df_1['beds'].astype(int)
        df_1['bathrooms'] = df_1['bathrooms'].astype(str).astype(float)
        df_1['price'] = df_1['price'].astype(str).astype(float).astype(int)
        df_1['cleaning_fee'] = df_1['cleaning_fee'].apply(lambda x: int(float(str(x))) if x != 'Not Specified' else 'Not Specified')
        df_1['extra_people'] = df_1['extra_people'].astype(str).astype(float).astype(int)
        df_1['guests_included'] = df_1['guests_included'].astype(str).astype(int)

        return df_1
    
    def host():

        host = []
        for i in data_collection.col.find( {}, {'_id':1, 'host':1}):
            host.append(i)

        df_host = pd.DataFrame(host)
        host_keys = list(df_host.iloc[0,1].keys())
        host_keys.remove('host_about')

        # make nested dictionary to separate columns

        for i in host_keys:
            if i == 'host_response_time':
                df_host['host_response_time'] = df_host['host'].apply(lambda x: x['host_response_time'] if 'host_response_time' in x else 'Not Specified')
            else:
                df_host[i] = df_host['host'].apply(lambda x: x[i] if i in x and x[i]!='' else 'Not Specified')

        df_host.drop(columns=['host'], inplace=True)
        
        # data type conversion

        df_host['host_is_superhost'] = df_host['host_is_superhost'].map({False:'No',True:'Yes'})
        df_host['host_has_profile_pic'] = df_host['host_has_profile_pic'].map({False:'No',True:'Yes'})
        df_host['host_identity_verified'] = df_host['host_identity_verified'].map({False:'No',True:'Yes'})

        return df_host
    
    def address():

        address = []
        for i in data_collection.col.find( {}, {'_id':1, 'address':1}):
            address.append(i)

        df_address = pd.DataFrame(address)
        address_keys = list(df_address.iloc[0,1].keys())
        
        # nested dicionary to separate columns

        for i in address_keys:
            if i == 'location':
                df_address['location_type'] = df_address['address'].apply(lambda x: x['location']['type'])
                df_address['longitude'] = df_address['address'].apply(lambda x: x['location']['coordinates'][0])
                df_address['latitude'] = df_address['address'].apply(lambda x: x['location']['coordinates'][1])
                df_address['is_location_exact'] = df_address['address'].apply(lambda x: x['location']['is_location_exact'])
            else:
                df_address[i] = df_address['address'].apply(lambda x: x[i] if x[i]!='' else 'Not Specified')

        df_address.drop(columns=['address'], inplace=True)

        #dtype convetion bool to string

        df_address['is_location_exact'] = df_address['is_location_exact'].map({False:'No',True:'Yes'})

        return df_address
    
    def availability():

        Availability=[]

        for i in data_collection.col.find({},{'_id':1,'availability':1}):
            Availability.append(i)


        df_availability = pd.DataFrame(Availability)
        availability_keys = list(df_availability.iloc[0,1].keys())
        
        # nested dicionary to separate columns

        for i in availability_keys:

            df_availability['availability_30'] = df_availability['availability'].apply(lambda x: x['availability_30'])
            df_availability['availability_60'] = df_availability['availability'].apply(lambda x: x['availability_60'])
            df_availability['availability_90'] = df_availability['availability'].apply(lambda x: x['availability_90'])
            df_availability['availability_365'] = df_availability['availability'].apply(lambda x: x['availability_365'])

        df_availability.drop(columns=['availability'],inplace=True)

        return df_availability
    

    def amenities_sort(x):
        a = x
        a.sort(reverse = False)
        return a
    
    def amenities():

        amenities = []
        for i in data_collection.col.find({}, {'_id':1,'amenities':1}):
            amenities.append(i)

        df_amenities = pd.DataFrame(amenities)
        df_amenities['amenities'] = df_amenities['amenities'].apply(lambda x: data_preprocessing.amenities_sort(x))

        return df_amenities
    
    def merge_dataframe():

        df_1 = data_preprocessing.primary()
        df_host = data_preprocessing.host()
        df_address = data_preprocessing.address()
        df_availability = data_preprocessing.availability()
        df_amenities = data_preprocessing.amenities()


        df = pd.merge(df_1,df_host, on='_id')
        df = pd.merge(df, df_address, on= '_id')
        df = pd.merge(df, df_availability, on= '_id')
        df = pd.merge(df, df_amenities, on='_id')

        return df
    
class data_inserting:

    def create_db():

        mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="airbnb"
            )

        cursor = mydb.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS airbnb_info(
                                _id					int,
                                        listing_url			text,
                                        name				varchar(255),
                                        property_type		varchar(255),
                                        room_type			varchar(255),
                                        bed_type			varchar(255),
                                        minimum_nights		int,
                                        maximum_nights		int,
                                        cancellation_policy	varchar(255),
                                        accommodates		int,
                                        bedrooms			int,
                                        beds				int,
                                        number_of_reviews	int,
                                        bathrooms			float,
                                        price				int,
                                        cleaning_fee		varchar(20),
                                        extra_people		int,
                                        guests_included		int,
                                        images				text,
                                        review_scores		int,
                                        host_id				varchar(255),
                                        host_url			text,
                                        host_name			varchar(255),
                                        host_location		varchar(255),
                                        host_response_time			varchar(255),
                                        host_thumbnail_url			text,
                                        host_picture_url			text,
                                        host_neighbourhood			varchar(255),
                                        host_response_rate			varchar(255),
                                        host_is_superhost			varchar(25),
                                        host_has_profile_pic		varchar(25),
                                        host_identity_verified		varchar(25),
                                        host_listings_count			int,
                                        host_total_listings_count	int,
                                        host_verifications			text,
                                        street				varchar(255),
                                        suburb				varchar(255),
                                        government_area		varchar(255),
                                        market				varchar(255),
                                        country				varchar(255),
                                        country_code		varchar(255),
                                        location_type		varchar(255),
                                        longitude			float,
                                        latitude			float,
                                        is_location_exact	varchar(25),
                                        availability_30		int,
                                        availability_60		int,
                                        availability_90		int,
                                        availability_365	int,
                                        amenities			text)""")
        mydb.commit()
        mydb.close()


    def insert_data():

        mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="airbnb"
        )

        cursor = mydb.cursor()

        df = data_preprocessing.merge_dataframe()
        try:
            for index, row in df.iterrows():
                #data = tuple(row.values.tolist())

                # Convert DataFrame to list of tuples
                #data = [tuple(row) for row in df.values]
                #data = tuple(row)
                #data = tuple(str(value) if isinstance(value, (int, float)) else value for value in row)
                converted_row = []
                for value in row:
                    if isinstance(value, (int, float)):
                        converted_row.append(value)
                    else:
                        converted_row.append(str(value))

                try:
                    cursor.execute("""INSERT INTO airbnb_info(_id,listing_url,name,property_type,room_type,bed_type,minimum_nights,maximum_nights,
                                        cancellation_policy,accommodates,bedrooms,beds,number_of_reviews,bathrooms,price,cleaning_fee,extra_people,
                                        guests_included,images,review_scores,host_id,host_url,host_name,host_location,host_response_time,
                                        host_thumbnail_url,host_picture_url,host_neighbourhood,host_response_rate,host_is_superhost,
                                        host_has_profile_pic,host_identity_verified,host_listings_count,host_total_listings_count,
                                        host_verifications,street,suburb,government_area,market,country,country_code,location_type,
                                        longitude,latitude,is_location_exact,availability_30,availability_60,availability_90,availability_365,amenities)
                                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",tuple(converted_row))

                except Exception as e:
                    print("Error inserting row:", e)
                    print("Problematic data:", tuple(converted_row))

        except mysql.connector.Error as err:
                print("Error during insertion:", err)

        #val =[tuple(df.values.tolist())]

        #val1 = tuple(map(int, df.split(',')))
        #cursor.execute(query,val)

        #val = df.values.tolist()[0]
        mydb.commit()
        cursor.close()
        mydb.close()




    				





        



        

        
    



            



