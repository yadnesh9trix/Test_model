import pandas as pd

MAIN_PATH = r"D:/"
STD_PATH = r"D:\Test_model/"
INP_PATH = STD_PATH + "Input/"
PAID_AMOUNT_FOLDER = MAIN_PATH + "Paidamount/"
OUT_PATH = STD_PATH + "OutPut/"


data = pd.read_excel(INP_PATH + "society_data.xlsx")

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

# Assuming 'addresses.txt' contains the list of addresses
# with open('addresses.txt', 'r', encoding='utf-8') as file:
#     addresses = file.readlines()

addresses = data['preoprtyaddress']
# Function to calculate cosine similarity between text data
def calculate_similarity(data):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(data)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

# Calculate similarity matrix
similarity_matrix = calculate_similarity(addresses)

# Perform hierarchical clustering
agg_clustering = AgglomerativeClustering(n_clusters=None, affinity='cosine', linkage='average', distance_threshold=0.7)
clusters = agg_clustering.fit_predict(similarity_matrix)

# Create a DataFrame with addresses and their respective clusters
df = pd.DataFrame({'Address': addresses, 'Cluster': clusters})

# Group addresses by cluster
grouped_addresses = df.groupby('Cluster')['Address'].apply(list)

# Display the groups
for group_index, group_addresses in grouped_addresses.items():
    print(f"Group {group_index}:\n{', '.join(group_addresses)}\n")






















# from fuzzywuzzy import fuzz
#
# def identify_societies(data):
#     society_mapping = {}
#
#     for i, row in data.iterrows():
#         property_address = row['propertyaddress']
#
#         # Check against existing societies
#         found = False
#         for society, society_address in society_mapping.items():
#             ratio = fuzz.ratio(property_address, society)
#             if ratio > 80:  # You can adjust the threshold as needed
#                 society_mapping[society].append(row['propertyname'])
#                 found = True
#                 break
#
#         # If no match is found, create a new society entry
#         if not found:
#             society_mapping[property_address] = [row['propertyname']]
#
#     return society_mapping
#
# # Replace this with your actual data loading code
# # For example, you might use pandas to read data from a CSV file
# import pandas as pd
#
# # Assuming 'data.csv' is your file with property data
#
# # Call the function to identify societies
# society_mapping = identify_societies(data)
#
# # Print the result
# for society, properties in society_mapping.items():
#     print(f"Society: {society}\nProperties: {', '.join(properties)}\n")
