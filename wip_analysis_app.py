{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "162c6dfb-54aa-4a3d-a8f3-04b5fde4fae5",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\nikhi\\AppData\\Local\\Temp\\ipykernel_12640\\3121356647.py:18: SettingWithCopyWarning: \n",
      "A value is trying to be set on a copy of a slice from a DataFrame.\n",
      "Try using .loc[row_indexer,col_indexer] = value instead\n",
      "\n",
      "See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy\n",
      "  pending_df.loc[:, 'WIP Age Bucket'] = pd.cut(pending_df['No of days in pend'], bins=bins, labels=labels)\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "DeltaGenerator()"
      ]
     },
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import pandas as pd\n",
    "import streamlit as st\n",
    "from openai import OpenAI\n",
    "\n",
    "# Initialize OpenAI client\n",
    "client = OpenAI(api_key=\"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\")  # Replace with your actual OpenAI key\n",
    "\n",
    "# Load CSV file\n",
    "file_path = r\"C:/Users/nikhi/Downloads/operational_data_full_jan_to_mar_2025 (1).csv\"\n",
    "df = pd.read_csv(file_path)\n",
    "\n",
    "# Filter pending cases\n",
    "pending_df = df[df['Pend Case'] == 'Yes']\n",
    "\n",
    "# Create WIP Age Buckets\n",
    "bins = [0, 1, 3, 5, 7, 10, 15, 30, 999]\n",
    "labels = ['0-1d', '1-3d', '3-5d', '5-7d', '7-10d', '10-15d', '15-30d', '30+d']\n",
    "pending_df.loc[:, 'WIP Age Bucket'] = pd.cut(pending_df['No of days in pend'], bins=bins, labels=labels)\n",
    "wip_age_distribution = pending_df['WIP Age Bucket'].value_counts().sort_index()\n",
    "\n",
    "# Backlog Drivers\n",
    "backlog_drivers = (\n",
    "    pending_df.groupby('Pend Reason')\n",
    "    .agg(Case_Count=('Case ID', 'count'), Avg_Days_in_Pend=('No of days in pend', 'mean'))\n",
    "    .sort_values(by='Case_Count', ascending=False)\n",
    "    .head(10)\n",
    "    .reset_index()\n",
    ")\n",
    "\n",
    "# WIP by Team\n",
    "wip_by_team = pending_df['Team Name'].value_counts().head(10)\n",
    "\n",
    "# WIP by Process\n",
    "wip_by_process = pending_df['Process Name'].value_counts().head(10)\n",
    "\n",
    "# GPT Summary Prompt\n",
    "summary_prompt = f\"\"\"\n",
    "You are a seasoned operations analyst. Summarize the following WIP analysis results, using bullet points for each insight:\n",
    "\n",
    "1. WIP Age Distribution: {wip_age_distribution.to_dict()}\n",
    "2. Backlog Drivers: {backlog_drivers.to_dict(orient='records')}\n",
    "3. Top Teams by WIP: {wip_by_team.to_dict()}\n",
    "4. Top Processes by WIP: {wip_by_process.to_dict()}\n",
    "\n",
    "Provide actionable, concise bullet-point insights grouped by section.\n",
    "\"\"\"\n",
    "\n",
    "# Get GPT response\n",
    "response = client.chat.completions.create(\n",
    "    model=\"gpt-4\",\n",
    "    messages=[{\"role\": \"user\", \"content\": summary_prompt}]\n",
    ")\n",
    "gpt_summary = response.choices[0].message.content\n",
    "\n",
    "# Streamlit UI\n",
    "st.set_page_config(page_title=\"WIP Analysis Report\", layout=\"wide\")\n",
    "st.title(\"\\U0001F4CA Back-office WIP Analysis Report (Jan–Mar 2025)\")\n",
    "\n",
    "st.markdown(\"## \\U0001F50D GPT Summary\")\n",
    "for line in gpt_summary.split(\"\\n\"):\n",
    "    if line.strip().startswith(\"-\") or line.strip().startswith(\"*\"):\n",
    "        st.markdown(f\"- {line.strip().lstrip('-* ')}\")\n",
    "    elif line.strip():\n",
    "        st.markdown(f\"**{line.strip()}**\")\n",
    "\n",
    "st.markdown(\"## \\U0001F4C8 WIP Age Distribution\")\n",
    "st.dataframe(wip_age_distribution.rename(\"Case Count\").reset_index().rename(columns={\"index\": \"Age Bucket\"}))\n",
    "\n",
    "st.markdown(\"## 🛑 Top Backlog Drivers\")\n",
    "st.dataframe(backlog_drivers)\n",
    "\n",
    "st.markdown(\"## 👥 Top Teams by WIP\")\n",
    "st.dataframe(wip_by_team.rename(\"Case Count\").reset_index().rename(columns={\"index\": \"Team\"}))\n",
    "\n",
    "st.markdown(\"## 🔄 Top Processes by WIP\")\n",
    "st.dataframe(wip_by_process.rename(\"Case Count\").reset_index().rename(columns={\"index\": \"Process\"}))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "22592d0d-917b-4edb-8cfc-8cfa0b2e59ef",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
