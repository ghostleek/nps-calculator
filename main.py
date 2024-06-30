import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import spacy

# Function to load spaCy model with fallback in case it's not installed
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

# Load spaCy model
nlp = load_spacy_model()

# Helper functions
def calculate_nps(df):
    nps_data = {}

    # Calculate overall NPS
    promoters = df[df['Rating'] >= 5].shape[0]
    detractors = df[df['Rating'] <= 3].shape[0]
    total_responses = df.shape[0]
    overall_nps = ((promoters - detractors) / total_responses) * 100
    overall_avg_rating = df['Rating'].mean()
    nps_data['Overall NPS'] = {'NPS': overall_nps, 'Avg Rating': overall_avg_rating}

    for entity in df['Entity'].unique():
        subset = df[df['Entity'] == entity]
        promoters = subset[subset['Rating'] >= 5].shape[0]
        detractors = subset[subset['Rating'] <= 3].shape[0]
        total_responses = subset.shape[0]
        nps_score = ((promoters - detractors) / total_responses) * 100
        average_rating = subset['Rating'].mean()
        nps_data[entity] = {'NPS': nps_score, 'Avg Rating': average_rating}

    return nps_data

def format_nps(nps_data):
    formatted_data = []
    for entity, values in nps_data.items():
        formatted_data.append({
            'Type': entity,
            'Net Promoter Score (NPS)': f"{values['NPS']:.2f} ({values['Avg Rating']:.3f} / 5)"
        })
    return formatted_data

def categorize_feedback(text):
    doc = nlp(text)
    categories = [ent.label_ for ent in doc.ents]
    return categories if categories else ["Uncategorized"]

# Streamlit app
st.title('NPS Score Calculator')

# Load the CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, parse_dates=['Submitted At'], dayfirst=True)
    data['Submitted At'] = pd.to_datetime(data['Submitted At'], format='%d/%m/%y %H:%M')
    
    # Date range selection
    date_options = ['Past Week', 'Past Month', 'All Time', 'Custom Date Range']
    selected_range = st.selectbox("Select Date Range", date_options)
    
    if selected_range == 'Past Week':
        start_date = datetime.now() - timedelta(weeks=1)
        end_date = datetime.now()
    elif selected_range == 'Past Month':
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif selected_range == 'All Time':
        start_date = data['Submitted At'].min()
        end_date = data['Submitted At'].max()
    elif selected_range == 'Custom Date Range':
        start_date = st.date_input("Start Date", value=data['Submitted At'].min().date())
        end_date = st.date_input("End Date", value=data['Submitted At'].max().date())
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())
    
    filtered_data = data[(data['Submitted At'] >= start_date) & (data['Submitted At'] <= end_date)]
    filtered_data = filtered_data.dropna(subset=['Answer'])
    
    # Calculate NPS
    nps_scores = calculate_nps(filtered_data)
    formatted_nps = format_nps(nps_scores)
    
    # Display NPS scores
    st.write("### Feedback")
    st.table(pd.DataFrame(formatted_nps))
    
    # Display unique feedback submissions count
    unique_submissions = filtered_data['User Id'].nunique()
    st.write(f"Unique Feedback Submissions: {unique_submissions}")
    
    st.write("---")

    # Display categorized answers
    st.write("### Categorized Feedback")
    filtered_data['Categories'] = filtered_data['Answer'].apply(lambda x: categorize_feedback(str(x)))
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### Booking Comments")
        booking_data = filtered_data[filtered_data['Entity'].str.contains("BOOKING")]
        for index, row in booking_data.iterrows():
            st.write(f"**User ID:** {row['User Id']}")
            st.write(f"**Answer:** {row['Answer']}")
            st.write(f"**Categories:** {', '.join(row['Categories'])}")
            st.write("---")
    
    with col2:
        st.write("#### Ballot Comments")
        ballot_data = filtered_data[filtered_data['Entity'].str.contains("BALLOT")]
        for index, row in ballot_data.iterrows():
            st.write(f"**User ID:** {row['User Id']}")
            st.write(f"**Answer:** {row['Answer']}")
            st.write(f"**Categories:** {', '.join(row['Categories'])}")
            st.write("---")
