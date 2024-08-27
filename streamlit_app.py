import os
import requests
import pandas as pd
import urllib3
import streamlit as st
from dotenv import load_dotenv

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# OAuth URL for Strava
auth_url = "https://www.strava.com/oauth/token"

def reauthorize():
    """
    Use the refresh token to get the latest access token.
    """
    payload = {
        'client_id': os.getenv('STRAVA_CLIENT_ID'),  # Get from environment variables
        'client_secret': os.getenv('STRAVA_CLIENT_SECRET'),  # Get from environment variables
        'refresh_token': os.getenv('STRAVA_REFRESH_TOKEN'),  # Get from environment variables
        'grant_type': 'refresh_token',
        'f': 'json'
    }

    try:
        response = requests.post(url=auth_url, data=payload, verify=False)
        response.raise_for_status()
        access_token = response.json()['access_token']
        return access_token
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to reauthorize: {e}")
        return None

def get_latest_activity_id(access_token):
    """
    Retrieve the ID of the latest activity.
    """
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    params = {'per_page': 1, 'page': 1}  # Fetch only the latest activity
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(url=activities_url, headers=headers, params=params, verify=False)
        response.raise_for_status()

        activities = response.json()
        if activities:
            latest_activity_id = activities[0]['id']
            latest_activity_name = activities[0]['name']
            st.write(f"Latest Activity ID: {latest_activity_id}")
            st.write(f"Latest Activity Name: {latest_activity_name}")
            return latest_activity_id
        else:
            st.warning("No activities found.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

def rename_activity(access_token, activity_id, new_name="funny_test_name"):
    """
    Rename a Strava activity by its ID.
    """
    activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'name': new_name}

    try:
        response = requests.put(url=activity_url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        st.success(f"Activity ID {activity_id} renamed to: {new_name}")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to rename activity: {e}")

def get_activity_name_by_id(access_token, activity_id):
    """
    Retrieve the name of a Strava activity by its ID.
    """
    activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(url=activity_url, headers=headers, verify=False)
        response.raise_for_status()

        activity_data = response.json()
        activity_name = activity_data.get('name')
        st.write(f"Activity ID {activity_id} Name: {activity_name}")
        return activity_name

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to retrieve activity name: {e}")
        return None

# Streamlit app starts here
st.title("Strava Activity Renamer")

# Input fields and button
new_activity_name = st.text_input("Enter new activity name:", "")
if st.button("Rename Latest Activity"):
    access_token = reauthorize()
    if access_token:
        latest_activity_id = get_latest_activity_id(access_token)
        if latest_activity_id:
            rename_activity(access_token, latest_activity_id, new_name=new_activity_name)

