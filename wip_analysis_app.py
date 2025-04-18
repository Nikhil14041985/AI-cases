#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="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")  # Replace with your actual OpenAI key

# Load CSV file
file_path = "operational_data_full_jan_to_mar_2025 (1).csv"

df = pd.read_csv(file_path)

# Filter pending cases
pending_df = df[df['Pend Case'] == 'Yes']

# Create WIP Age Buckets
bins = [0, 1, 3, 5, 7, 10, 15, 30, 999]
labels = ['0-1d', '1-3d', '3-5d', '5-7d', '7-10d', '10-15d', '15-30d', '30+d']
pending_df.loc[:, 'WIP Age Bucket'] = pd.cut(pending_df['No of days in pend'], bins=bins, labels=labels)
wip_age_distribution = pending_df['WIP Age Bucket'].value_counts().sort_index()

# Backlog Drivers
backlog_drivers = (
    pending_df.groupby('Pend Reason')
    .agg(Case_Count=('Case ID', 'count'), Avg_Days_in_Pend=('No of days in pend', 'mean'))
    .sort_values(by='Case_Count', ascending=False)
    .head(10)
    .reset_index()
)

# WIP by Team
wip_by_team = pending_df['Team Name'].value_counts().head(10)

# WIP by Process
wip_by_process = pending_df['Process Name'].value_counts().head(10)

# GPT Summary Prompt
summary_prompt = f"""
You are a seasoned operations analyst. Summarize the following WIP analysis results, using bullet points for each insight:

1. WIP Age Distribution: {wip_age_distribution.to_dict()}
2. Backlog Drivers: {backlog_drivers.to_dict(orient='records')}
3. Top Teams by WIP: {wip_by_team.to_dict()}
4. Top Processes by WIP: {wip_by_process.to_dict()}

Provide actionable, concise bullet-point insights grouped by section.
"""

# Get GPT response
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": summary_prompt}]
)
gpt_summary = response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="WIP Analysis Report", layout="wide")
st.title("\U0001F4CA Back-office WIP Analysis Report (Jan–Mar 2025)")

st.markdown("## \U0001F50D GPT Summary")
for line in gpt_summary.split("\n"):
    if line.strip().startswith("-") or line.strip().startswith("*"):
        st.markdown(f"- {line.strip().lstrip('-* ')}")
    elif line.strip():
        st.markdown(f"**{line.strip()}**")

st.markdown("## \U0001F4C8 WIP Age Distribution")
st.dataframe(wip_age_distribution.rename("Case Count").reset_index().rename(columns={"index": "Age Bucket"}))

st.markdown("## 🛑 Top Backlog Drivers")
st.dataframe(backlog_drivers)

st.markdown("## 👥 Top Teams by WIP")
st.dataframe(wip_by_team.rename("Case Count").reset_index().rename(columns={"index": "Team"}))

st.markdown("## 🔄 Top Processes by WIP")
st.dataframe(wip_by_process.rename("Case Count").reset_index().rename(columns={"index": "Process"}))


# In[ ]:




