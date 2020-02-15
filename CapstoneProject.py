#!/usr/bin/env python
# coding: utf-8

# <h1 align=center><font size=5>Ideal Business Office Sites in Zurich</font></h1>
# 
# <h2 align=center><font size=4>Capstone Project - toward the IBM Data Science Professional Certificate</font></h2>
# 
# <h3 align=center><font size=3>Applied Data Science Capstone by IBM/Coursera</font></h3>

# ## Table of Contents
# 
# <div class="alert alert-block alert-info" style="margin-top: 20px">
# 
# 
# 1. [Introduction](#Introduction)
# 
# 2. [Methodology](#Methodology)
# 
# 3. [Data Preparation and Analysis](#DataPreparationandDiscussion)
# 
# 4. [Results](#Results)
#     
# 5. [Conclusion](#Conclusion)
# 
# </div>

# ## 1. Introduction <a name="Introduction"></a>
# 
# This chapter aims to answer the first question in the Capstone Project - The Battle of Neighborhoods (Week 1), namely, a description of the problem and a discussion of the background.

# ### 1.1 Problem Description
# 
# In this project we will try to find an ideal location for startups who want to locate at Zurich, Switzerland. The target stakeholders are companies/contractors who are interested in starting their own business in Zurich, Switzerland with the special consideration to attract qualified employees.
# 
# ### 1.2 Background Discussion
# 
# The selection of a company's location is complex in nature since it is influenced by many factors, such capital investment, government policies/regulations, labor, transportation, and influence of competitors. This project will focus on geographical factors which influences qualified job seekers’ choices while applying jobs. For instance, number of restaurant/coffee-bar/supermarket, distance to public transportation. 
# 
# In this project, we are going to use location data to explore Zurich and generate a few most promising neighborhoods for the target stockholders to select an ideal business office. The reason why those neighborhoods are the ideal location will be clarified within the data analysis process.

# ## 2. Methodology <a name="Methodology"></a>
# 
# This chapter aims to answer the secont question in the Capstone Project - The Battle of Neighborhoods (Week 1), namely, a description of the data and how it will be used to solve the problem.

# Based on the problem definition of this project, factors that will influence the business office selection are:
# 
# 1. Number of existing restaurants/coffee-bar/supermarkets nearby
# 2. If there is a gym or sport center nearby
# 3. Is it convenient to take public transportation 
# 
# According to the GeoNames Geographical Database, basic geographical data can be obtained and transformed to data frame by using the library pandas. Folium will be used to visualize maps and the latitude and longitude values will be acquired by the using of geopy library. Of course, ZurichFoursquare API will be used to explore the Zurich region and segment them. In the end, the ideal business office sites in Zurich for stockholders will be presented both descriptively and graphically.

# ## 3. Data Preparation and Analysis <a name="DataPreparationandDiscussion"></a>
# 
# In this section, all the necessionallary data will be handeled and relevent analysis will be processed.

# #### Import all the possibilly needed libraries

# In[3]:


import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json

get_ipython().system('pip install geopy')
from geopy.geocoders import Nominatim

import requests 
from pandas.io.json import json_normalize

import matplotlib.cm as cm
import matplotlib.colors as colors

from sklearn.cluster import KMeans

get_ipython().system('pip install folium')
import folium

print('Libraries imported.')


# #### Use geopy library to get the latitude and longitude values of Zurich

# In[4]:


address = 'Zurich, Switzerland'

geolocator = Nominatim(user_agent="ny_explorer", timeout=3)
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Zurich are {}, {}.'.format(latitude, longitude))


# #### Loading and inserting the GeoNames of Switzerland dowloaded from the GeoNames geographical database to code

# In[5]:



import types
import pandas as pd
from botocore.client import Config
import ibm_boto3

def __iter__(self): return 0

# @hidden_cell
# The following code accesses a file in your IBM Cloud Object Storage. It includes your credentials.
# You might want to remove those credentials before you share the notebook.
client_57987119d155404f93aebe55bb33cc74 = ibm_boto3.client(service_name='s3',
    ibm_api_key_id='DOWZ6P107XgimW48rX9hZauTThzn2Biod7GT_g4Qg6le',
    ibm_auth_endpoint="https://iam.eu-de.bluemix.net/oidc/token",
    config=Config(signature_version='oauth'),
    endpoint_url='https://s3.eu-geo.objectstorage.service.networklayer.com')

# Your data file was loaded into a botocore.response.StreamingBody object.
# Please read the documentation of ibm_boto3 and pandas to learn more about the possibilities to load the data.
# ibm_boto3 documentation: https://ibm.github.io/ibm-cos-sdk-python/
# pandas documentation: http://pandas.pydata.org/
streaming_body_1 = client_57987119d155404f93aebe55bb33cc74.get_object(Bucket='machinelearningwithpython-donotdelete-pr-09mnzl9z4wd34u', Key='CH.txt')['Body']
# add missing __iter__ method, so pandas accepts body as file-like object
if not hasattr(streaming_body_1, "__iter__"): streaming_body_2.__iter__ = types.MethodType( __iter__, streaming_body_2 ) 


# #### Read the table to a dataframe

# In[6]:


import io

df = pd.read_csv(io.BytesIO(streaming_body_1.read()), sep='\t', header=None)
print(df.shape)
df.head()


# #### Cleaning the data
# The data includes all the detail geographical information in Switzerland. Let's select only information for canton Zurich and other useful information such as borough, neighborhood, latitude, and longitude

# In[10]:


df_Z = df.loc[df[3] == 'Kanton Zürich']
print(df_Z.shape)
df_Z.head()


# In[11]:


df_Z = df_Z[[1, 5, 2, 9, 10]]
df_Z.columns = ['PostCode', 'Borough', 'Neighborhood', 'Latitude', 'Longitude']
df_Z.reset_index(drop=True, inplace=True)
print(df_Z.shape)
df_Z.head()


# In[16]:


df_Z = df_Z.drop_duplicates(subset=['Latitude', 'Longitude'], keep='first')
df_Z.reset_index(drop=True, inplace=True)
print(df_Z.shape)
df_Z.tail(10)


# In[17]:


df_Z['Neighborhood'] = df_Z.groupby('Neighborhood').Neighborhood.apply(lambda n: n + np.concatenate(([''], (np.arange(len(n))+1).astype(str)[1:])))
print(df_Z.shape)
df_Z.tail(10)


# #### Create a map of canton Zurich with neighborhoods superimposed on top

# In[19]:


# create map of Zurich using latitude and longitude values
map_zurich = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, postcode, borough, neighborhood in zip(df_Z['Latitude'], df_Z['Longitude'], df_Z['PostCode'], df_Z['Borough'], df_Z['Neighborhood']):
    label = '{}, {}, {}'.format(neighborhood, postcode, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_zurich)  
    
map_zurich


# #### Define Foursquare Credentials and Version

# In[20]:


CLIENT_ID = 'QXTB3NFSILI2SK3VTC5ECYRV0LIEWY5L42ZJKQBGBCXVHVST'
CLIENT_SECRET = '3XMITHOMQZ5GF3LLFLAFS22KGU5V2YDVAXZLMEYGMGGW2KYB'
VERSION = '20200201'

print('My credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# #### Explore Neighborhoods in Zurich

# In[24]:


# get the top 100 venues that are in all the neighborhoods in Zurich within a radius of 2000 meters

LIMIT = 100
def getNearbyVenues(names, latitudes, longitudes, radius=1000):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[25]:


zurich_venues = getNearbyVenues(names=df_Z['Neighborhood'],
                                latitudes=df_Z['Latitude'],
                                longitudes=df_Z['Longitude']
                                )


# In[35]:


print(zurich_venues.shape)
zurich_venues.head()


# In[36]:


# check how many venues were returned for each neighborhood
zurich_new = zurich_venues.groupby('Neighborhood').count().reset_index()
print(zurich_new.shape)
zurich_new


# #### Analyze Each Neighborhood

# In[37]:


# one hot encoding
zurich_onehot = pd.get_dummies(zurich_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
zurich_onehot['Neighborhood'] = zurich_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [zurich_onehot.columns[-1]] + list(zurich_onehot.columns[:-1])
zurich_onehot = zurich_onehot[fixed_columns]

print(zurich_onehot.shape)
zurich_onehot.head()


# #### Grouping rows by neighborhood and by taking the total frequency of each category occurrence

# In[38]:


zurich_g = zurich_onehot.groupby('Neighborhood').sum().reset_index()
print(zurich_g.shape)
zurich_g.tail()


# Since our focus is what people care about while looking for jobs such as the number of restaurent/supermarket and gym close to the ideal business office, which companies also care in order to attract talented emplayees. Therefore, let's find out how many relevent categories can be captured from all the returned venues for each neighborhood.

# #### 1. Number of existing restaurants/coffee-bar/supermarkets nearby

# In[39]:


zurich_food1 = zurich_g.filter(like='Restaurant', axis=1)
zurich_food2 = zurich_g.filter(like='Breakfast', axis=1)
zurich_food3 = zurich_g.filter(like='Cafeteria', axis=1)
zurich_food4 = zurich_g.filter(like='Café', axis=1)
zurich_food5 = zurich_g.filter(like='Coffee', axis=1)
zurich_food6 = zurich_g.filter(like='Supermarket', axis=1)

zurich_food = pd.concat([zurich_food1, zurich_food2, zurich_food3, zurich_food4, zurich_food5, zurich_food6], axis=1)
print(zurich_food.shape)
zurich_food.head()


# In[40]:


zurich_food.loc[:, 'Food'] = zurich_food.sum(axis=1)
print(zurich_food.shape)
zurich_food.head()


# In[41]:


zurich_new.index = zurich_food.index
zurich_new['Food']= zurich_food['Food']
print(zurich_new.shape)
zurich_new.head()


# #### Merge number of food sites nearby with latitude/longitude for each neighborhood

# In[42]:


zurich_merged = zurich_new
zurich_merged = zurich_merged.join(df_Z.set_index('Neighborhood'), on='Neighborhood')
zurich_merged = zurich_merged[['PostCode', 'Neighborhood', 'Latitude', 'Longitude', 'Food']]
print(zurich_merged.shape)
zurich_merged.head()


# #### Selecting the top 10 neighborhoods with the most restaurants nearby

# In[65]:


zurich_merged_food = zurich_merged.sort_values(by='Food', ascending=False)
zurich_merged_food.reset_index(drop=True, inplace=True)
print(zurich_merged_food.shape)
zurich_merged_food.head(10)


# #### Clustering neighborhoods based on the number of restaurents nearby

# In[66]:


# set number of clusters
kclusters = 4
zurich_merged_food_clustering = zurich_merged_food[['Food']]
# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(zurich_merged_food_clustering)


# In[67]:


# add clustering labels
zurich_merged_food.insert(5, 'Cluster Labels', kmeans.labels_)
zurich_merged_food.head(10)


# #### visualizing the resulting food clusters

# In[69]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=10)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, Neighborhood, cluster in zip(zurich_merged_food['Latitude'], zurich_merged_food['Longitude'], zurich_merged_food['Neighborhood'], zurich_merged_food['Cluster Labels']):
    label = folium.Popup(str(Neighborhood) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# According to the above analysis, the top 10 neighborhoods with the most restaurants nearby can be presented to stackholders. The visualization map also created for a better understanding at a glance. The red color are the worst choices in terms of the concern by attracting qualified labers with sufficient food choices nearby.
# 
# Similiarly, let's continuously analyz the gym and public transparation conditions.

# #### 2. Check if a gym or sport center is nearby

# In[70]:


zurich_gym1 = zurich_g.filter(like='Gym', axis=1)
zurich_gym2 = zurich_g[['Dance Studio', 'Sports Club', 'Tennis Court', 'Tennis Stadium', 'Yoga Studio', 'Rock Climbing Spot']]
zurich_gym = pd.concat([zurich_gym1, zurich_gym2], axis=1)
print(zurich_gym.shape)
zurich_gym.head()


# In[71]:


zurich_gym.loc[:, 'GymT'] = zurich_gym.sum(axis=1)
print(zurich_gym.shape)
zurich_gym.head()


# In[72]:


zurich_merged['Gym']= zurich_gym['GymT']
print(zurich_merged.shape)
zurich_merged.head()


# #### Select the top 10 neighborhood with the most gym/sport centers nearby

# In[80]:


zurich_merged_gym = zurich_merged[['PostCode', 'Neighborhood', 'Latitude', 'Longitude', 'Gym']]
zurich_merged_gym = zurich_merged_gym.sort_values(by='Gym', ascending=False)
zurich_merged_gym.reset_index(drop=True, inplace=True)
print(zurich_merged_gym.shape)
zurich_merged_gym.head(10)


# #### Check how many neighborhoods with at least one sport place nearby

# In[77]:


zurich_merged_gym1 = zurich_merged_gym[zurich_merged_gym['Gym'] > 0]
print ("There are", zurich_merged_gym1.shape[0], 'neighborhoods with at least one sport place nearby')


# #### Clustering and visualizing based on if there is at least a gym nearby

# In[81]:


# set number of clusters
kclusters_g = 2
zurich_merged_gym_clustering = zurich_merged_gym[['Gym']]
# run k-means clustering
kmeans = KMeans(n_clusters=kclusters_g, random_state=0).fit(zurich_merged_gym_clustering)
# add clustering labels
zurich_merged_gym.insert(5, 'Cluster Labels', kmeans.labels_)
zurich_merged_gym.head(10)


# In[83]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=10)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, Neighborhood, cluster in zip(zurich_merged_gym['Latitude'], zurich_merged_gym['Longitude'], zurich_merged_gym['Neighborhood'], zurich_merged_gym['Cluster Labels']):
    label = folium.Popup(str(Neighborhood) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# Based on the above analysis, 49 neighborhoods have at least one gym/sports center nearby. Stakeholders can further consider the number of gyms nearby while making decisions regarding where is the ideal business location. Accordingly, the 49 neighborhoods are shown in purple color in the visualization for a clear understanding.

# #### 3. Check if it is convenient to take public transportation

# In[85]:


zurich_transport = zurich_g[['Bus Station', 'Light Rail Station', 'Train Station', 'Tram Station']]
zurich_transport.loc[:, 'Transport'] = zurich_transport.sum(axis=1)
zurich_transport.head()


# In[86]:


zurich_merged['Transport']= zurich_transport['Transport']
print(zurich_merged.shape)
zurich_merged.head()


# #### Find out 10 of the most convenitent neighborhoods with most public transport stations nearby

# In[106]:


zurich_merged_transport = zurich_merged[['PostCode', 'Neighborhood', 'Latitude', 'Longitude', 'Transport']]
zurich_merged_transport = zurich_merged_transport.sort_values(by='Transport', ascending=False)
zurich_merged_transport.reset_index(drop=True, inplace=True)
print(zurich_merged_transport.shape)
zurich_merged_transport.head(10)


# In[94]:


zurich_merged_transport1 = zurich_merged_transport[zurich_merged_transport['Transport'] > 0]
zurich_merged_transport2 = zurich_merged_transport[zurich_merged_transport['Transport'] > 1]
print ("There are", zurich_merged_transport1.shape[0], 'neighborhoods with at least one public transportation nearby')
print ("There are", zurich_merged_transport2.shape[0], 'neighborhoods with at least two public transportations nearby')


# #### Clustering and visualizing neighborhoods according to public transportation

# In[107]:


# set number of clusters
kclusters_t = 2
zurich_merged_transport_clustering = zurich_merged_transport[['Transport']]
# run k-means clustering
kmeans = KMeans(n_clusters=kclusters_t, random_state=0).fit(zurich_merged_transport_clustering)
# add clustering labels
zurich_merged_transport.insert(5, 'Cluster Labels', kmeans.labels_)
zurich_merged_transport.head(10)


# In[109]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=10)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, Neighborhood, cluster in zip(zurich_merged_transport['Latitude'], zurich_merged_transport['Longitude'], zurich_merged_transport['Neighborhood'], zurich_merged_transport['Cluster Labels']):
    label = folium.Popup(str(Neighborhood) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# Similarly, we analyzed the ideal business office locations based on consideration of if it is convenient to take public transportation. The above analysis shows that 47 neighborhoods in Zurich have at least two public transport stations nearby. Accordingly, the 47 neighborhoods are shown in purple color in the visualization for a clear understanding as well.

# ### Aggregated Analysis based on the Three Factors
# 
# Based on the above analysis aim at each of the three criteria that we used at this project to select the ideal office location for business, the three tables show the top 10 choices of each consideration can be presented to stakeholders if they consider only one of the factors. Accordingly depends on stakeholders' preference, the aggregated analysis of the three factors can be adjusted according to stakeholders' specific demands.
# 
# For instance, if a company want to select a business office location with as long as one gym and one public transportation nearby, and as many restaurants as possible to attract qualified employees, the analytical results are different compared to companies who require as many as gyms, restaurants, and public transportations nearby. Let's first analyze all neighborhoods that have at least one restaurant, one gym, and one public transport station nearby to satisfy the basic demands without the consideration of the amount.

# In[123]:


zurich_merged_a = zurich_merged[zurich_merged['Food'] > 0]
zurich_merged_a = zurich_merged_a[zurich_merged_a['Gym'] > 0]
zurich_merged_a = zurich_merged_a[zurich_merged_a['Transport'] > 0]
zurich_merged_a.reset_index(drop=True, inplace=True)
print(zurich_merged_a.shape)
zurich_merged_a


# As we can see above, we narrow down the neighborhood to 31 while considering the basic factors without the comparison of quantity about various venues. The above table shows 31 neighborhoods can be selected or presented to stakeholders for further consideration. Let's further put the number of the three factors, namely,  restaurants nearby, public transportations, and gym into consideration.

# In[124]:


zurich_merged_a = zurich_merged_a.sort_values(['Food', 'Transport', 'Gym'], ascending=False)
zurich_merged_a.reset_index(drop=True, inplace=True)
print(zurich_merged_a.shape)
zurich_merged_a


# #### Clustering and visualizing neighborhoods based on the aggregated three factors

# In[125]:


# set number of clusters
kclusters_a = 3
zurich_merged_a_clustering = zurich_merged_a[['Food', 'Gym', 'Transport']]
# run k-means clustering
kmeans = KMeans(n_clusters=kclusters_a, random_state=0).fit(zurich_merged_a_clustering)
# add clustering labels
zurich_merged_a.insert(7, 'Cluster Labels', kmeans.labels_)
zurich_merged_a


# In[127]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=10)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, Neighborhood, cluster in zip(zurich_merged_a['Latitude'], zurich_merged_a['Longitude'], zurich_merged_a['Neighborhood'], zurich_merged_a['Cluster Labels']):
    label = folium.Popup(str(Neighborhood) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# According to the aggregated analysis taking all the elements and its numbers into consideration, we found that 31 neighborhoods are the potential ideal business locations for stakeholders considering the three factors to attract employees. Furthermore, we analyzed that there are 17 neighborhood are more attractive after clustering all the 31 neighborhoods. As it is shown in the table and the visual map. One can see from the map clearly that the neighborhoods presented by the purple points are the most favorable ones. The red neighborhoods are still good choices. However, compared to the others, those ones may not take into primary consideration for this project.

# ## 4. Results <a name="Results"></a>

# #### Final results for stakeholders

# In[129]:


zurich_merged_a = zurich_merged_a[zurich_merged_a['Cluster Labels'] > 0]
zurich_merged_a


# This project shows that there are more than 300 neighborhoods in Zurich can be selected by stakeholders as a business office location. However, many of them are less suitable for companies who want to select their business office close to a place where has many restaurants, at least one sports place and public transport station nearby as preconditions to attract qualified employees. After analyzing each of the three factors which indicated at the beginning of this project, the results show that the preferably business office locations are quite different when considering neither each factor separately nor aggregated together.
# 
# The findings in this project can be presented to stakeholders with different important consideration of the three factors. The adjustment can be made accordingly based on specific stakeholders' demands.
# 
# In summary, the top ten neighborhoods of each factor can be presented and the relevant cluster maps can be found in this project. By selecting only neighborhoods that contain at least one restaurant, one gym, and one public transportation station within a 1km radius, this project found 31 neighborhoods in Zurich can be selected to attract employees. Moreover, after taking the total amount those venues into consideration by clustering the 31 neighborhoods into 3 clusters, this project further targets 17 neighborhoods and 4 of them can be considered as priorities when other conditions are equal.
# 
# The purpose of this project is to provide statistical information for stakeholders who want to find an ideal business office location in Zurich where is attractive to employees. The following table can be shown to stakeholders as final results. Of course, those recommended neighborhoods should be considered as a starting point for more detailed analysis for stakeholders who take the three factors contained in this project as a priority and many other factors need to be considered.

# ## 5. Conclusion <a name="Conclusion"></a>

# Based on the use of GeoNames Geographical Database, Foursquare API and some machine learning techniques with various libraries such as Pandas, Folium, Scikit-learn, we analyzed the Ideal Business Office Sites in Zurich based on three factors. Namely, the number of existing restaurants/coffee-bar/supermarkets nearby, if there is a gym or sports center nearby, and is it convenient to take public transportation. According to the analysis processes, we narrowed down the ideal business location in Zurich from the original almost 300 to around 30 neighborhoods. Moreover, by clustering all the possible ones, we further target a smaller portion of around 10 of the best possible business office locations to present to the relevant stakeholders.
# 
# The final decision on optimal business office locations can be made by stakeholders based on other specific considerations of neighborhoods in every recommended zone, taking into additional factors such as fixed costs like office renting price, closeness to park, levels of noise, and other social as well as economic considerations. It is important to point out that this project is based on the three factors we analyzed. There are also many other factors and ways to analysis and the results may vary based on distinct criteria and analyzed at different times. The market is dynamic and the importance of factors to various stakeholders is different.
