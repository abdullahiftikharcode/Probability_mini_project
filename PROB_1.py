import random
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
file_path = "C:/Users/jivot/source/repos/PROB-1/PROB-1/aid_workers_security_incidents.csv"
data = pd.read_csv(file_path)

# Streamlit app
st.title("Sankey Diagram for Aid Workers Security Incidents")
st.write("Use the filters below to customize the Sankey diagram.")

# Sidebar filters with "Select All" option
def multiselect_with_select_all(label, options):
    select_all = st.sidebar.checkbox(f"Select all {label}")
    if select_all:
        selected_options = options
    else:
        selected_options = st.sidebar.multiselect(label, options)
    return selected_options

# Sidebar selections with "Select All" options
selected_year = multiselect_with_select_all("Year(s)", sorted(data['Year'].dropna().unique()))
countries_in_year = data[data['Year'].isin(selected_year)]['Country'].dropna().unique()
selected_country = multiselect_with_select_all("Country(s)", sorted(countries_in_year))
cities_in_year_country = data[(data['Year'].isin(selected_year)) & (data['Country'].isin(selected_country))]['City'].dropna().unique()
selected_city = multiselect_with_select_all("City(s)", sorted(cities_in_year_country))

# Filter data based on user selections
filtered_data = data[
    (data['Year'].isin(selected_year)) &
    (data['Country'].isin(selected_country)) &
    (data['City'].isin(selected_city))
]

# Convert relevant columns to numeric
filtered_data['Total affected'] = pd.to_numeric(filtered_data['Total affected'], errors='coerce').fillna(0)
filtered_data['Total killed'] = pd.to_numeric(filtered_data['Total killed'], errors='coerce').fillna(0)
filtered_data['Total wounded'] = pd.to_numeric(filtered_data['Total wounded'], errors='coerce').fillna(0)
filtered_data['Total kidnapped'] = pd.to_numeric(filtered_data['Total kidnapped'], errors='coerce').fillna(0)

# Node indices for Sankey (Year, Country, Totals, Motive)
node_labels = list(filtered_data['Year'].unique()) + \
              list(filtered_data['Country'].unique()) + \
              list(filtered_data['Motive'].unique()) + \
              ["Total wounded", "Total kidnapped", "Total killed", "Total affected"]  # Reorder Total affected last

node_indices = {label: idx for idx, label in enumerate(node_labels)}

# Create links for the Sankey diagram
links = {'source': [], 'target': [], 'value': []}
for _, row in filtered_data.iterrows():
    # Add Year -> Country link
    links['source'].append(node_indices[row['Year']])
    links['target'].append(node_indices[row['Country']])
    links['value'].append(row['Total affected'])
    
    # Add Country -> Motive link
    links['source'].append(node_indices[row['Country']])
    links['target'].append(node_indices[row['Motive']])
    links['value'].append(row['Total affected'])
    
    # Add Motive -> Total category links
    links['source'].append(node_indices[row['Motive']])
    links['target'].append(node_indices["Total wounded"])
    links['value'].append(row['Total wounded'])

    links['source'].append(node_indices[row['Motive']])
    links['target'].append(node_indices["Total kidnapped"])
    links['value'].append(row['Total kidnapped'])
    
    links['source'].append(node_indices[row['Motive']])
    links['target'].append(node_indices["Total killed"])
    links['value'].append(row['Total killed'])
    
    # Link Total categories to Total affected
    links['source'].append(node_indices["Total wounded"])
    links['target'].append(node_indices["Total affected"])
    links['value'].append(row['Total wounded'])

    links['source'].append(node_indices["Total kidnapped"])
    links['target'].append(node_indices["Total affected"])
    links['value'].append(row['Total kidnapped'])

    links['source'].append(node_indices["Total killed"])
    links['target'].append(node_indices["Total affected"])
    links['value'].append(row['Total killed'])

# Aggregate data for the Sankey diagram
labels = node_labels
source = links['source']
target = links['target']
value = links['value']

# Plotting the Sankey Diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels
    ),
    link=dict(
        source=source,
        target=target,
        value=value
    )
)])

fig.update_layout(title_text="Sankey Diagram of Security Incidents", font_size=10)
st.plotly_chart(fig)
