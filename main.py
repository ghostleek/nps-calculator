import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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

def analyze_sentiment(comments):
    analyzer = SentimentIntensityAnalyzer()
    positive_comments = []
    negative_comments = []

    for comment in comments:
        sentiment_score = analyzer.polarity_scores(comment)['compound']
        if sentiment_score >= 0.7:
            positive_comments.append(comment)
        else:
            negative_comments.append(comment)

    return positive_comments, negative_comments

# Streamlit app
st.title('NPS Score Calculator')

# Load the CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, parse_dates=['Submitted At'], dayfirst=True)
    data['Submitted At'] = pd.to_datetime(data['Submitted At'], format='%Y-%m-%d %H:%M:%S')
    
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
    
    # Calculate NPS
    nps_scores = calculate_nps(filtered_data)
    formatted_nps = format_nps(nps_scores)
    
    # Display NPS scores
    st.write("### Net Promoter Score (NPS)")
    st.table(pd.DataFrame(formatted_nps))
    
    # Display unique feedback submissions count
    unique_submissions = filtered_data['User Id'].nunique()
    st.write(f"Unique Feedback Submissions: {unique_submissions}")
    total_submissions = filtered_data['User Id'].count()
    st.write(f"Total Feedback Submissions: {total_submissions}")
    st.write("---")

    # Comments section
    st.write("### Comments")
    st.write("⚠️ for grouping of positive v negative, a simple library for sentiment analysis is used - please exercise discretion")

    # Analyze and display comments for Booking
    with st.container():
        st.write("#### Booking")
        booking_data = filtered_data[filtered_data['Entity'].str.contains('BOOKING_BY_PAYMENT_ID', case=False)]
        booking_answers = booking_data['Answer'].dropna()
        booking_positive, booking_negative = analyze_sentiment(booking_answers)
        
        st.write(f"{len(booking_answers)} out of {len(booking_data)} wrote comments")
        with st.expander(f"Positive Feedback ({len(booking_positive)})"):
            if booking_positive:
                for answer in booking_positive:
                    st.write(answer)
                    st.write("---")
            else:
                st.write("No positive booking comments available.")

        with st.expander(f"Negative Feedback ({len(booking_negative)})"):
            if booking_negative:
                for answer in booking_negative:
                    st.write(answer)
                    st.write("---")
            else:
                st.write("No negative booking comments available.")

    # Analyze and display comments for Ballot
    with st.container():
        st.write("#### Ballot")
        ballot_data = filtered_data[filtered_data['Entity'].str.contains('BALLOT_BY_REFERENCE_ID', case=False)]
        ballot_answers = ballot_data['Answer'].dropna()
        ballot_positive, ballot_negative = analyze_sentiment(ballot_answers)

        st.write(f"{len(ballot_answers)} out of {len(ballot_data)} wrote comments")
        with st.expander(f"Positive Feedback ({len(ballot_positive)})"):
            if ballot_positive:
                for answer in ballot_positive:
                    st.write(answer)
                    st.write("---")
            else:
                st.write("No positive ballot comments available.")

        with st.expander(f"Negative Feedback ({len(ballot_negative)})"):
            if ballot_negative:
                for answer in ballot_negative:
                    st.write(answer)
                    st.write("---")
            else:
                st.write("No negative ballot comments available.")

    # Analyze and display comments for Programme
    with st.container():
        st.write("#### Programme")
        programme_data = filtered_data[filtered_data['Entity'].str.contains('PROGRAMME', case=False)]
        programme_answers = programme_data['Answer'].dropna()
        programme_positive, programme_negative = analyze_sentiment(programme_answers)

        st.write(f"{len(programme_answers)} out of {len(programme_data)} wrote comments")
        with st.expander(f"Positive Feedback ({len(programme_positive)})"):
            if programme_positive:
                for answer in programme_positive:
                    st.write(answer)
                    st.write("---")
            else:
                st.write("No positive programme comments available.")

        with st.expander(f"Negative Feedback ({len(programme_negative)})"):
            if programme_negative:
                for answer in programme_negative:
                    st.write(answer)
                    st.write("---")
            else:
                st.write("No negative programme comments available.")
