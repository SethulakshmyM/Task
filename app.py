import requests
import streamlit as st
import os

# -----------------------------
# Backend API URL from environment variable
# -----------------------------
API_URL = os.environ.get("API_URL", "https://task-manager-app-f2pn.onrender.com")

st.title("📋 Task Manager App")

# -----------------------------
# Add Task Section
# -----------------------------
st.header("Add a New Task")
title = st.text_input("Task Title")
description = st.text_area("Task Description")

if st.button("Add Task"):
    if title and description:
        payload = {
            "title": title,
            "description": description,
            "is_done": False  # default new task
        }
        try:
            res = requests.post(API_URL, json=payload)
            if res.status_code == 201:
                st.success("✅ Task added successfully!")
                st.experimental_rerun()
            else:
                st.error(f"❌ Failed to add task: {res.text}")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
    else:
        st.warning("Please enter both title and description.")

# -----------------------------
# Show Tasks Section
# -----------------------------
st.header("All Tasks")
try:
    res = requests.get(API_URL)
    if res.status_code == 200:
        tasks = res.json()
        for task in tasks:
            with st.container():
                st.subheader(f"{task['id']} - {task['title']}")
                st.write(task['description'])

                # ✅ Toggle Done / Not Done
                if task["is_done"]:
                    st.success("✅ Done")
                    if st.button(f"Mark as Not Done", key=f"undone_{task['id']}"):
                        update_payload = {
                            "title": task["title"],
                            "description": task["description"],
                            "is_done": False
                        }
                        requests.put(f"{API_URL}/{task['id']}", json=update_payload)
                        st.experimental_rerun()
                else:
                    st.warning("❌ Not Done")
                    if st.button(f"Mark as Done", key=f"done_{task['id']}"):
                        update_payload = {
                            "title": task["title"],
                            "description": task["description"],
                            "is_done": True
                        }
                        requests.put(f"{API_URL}/{task['id']}", json=update_payload)
                        st.experimental_rerun()

                # 🗑 Delete Task
                if st.button("🗑 Delete Task", key=f"delete_{task['id']}"):
                    requests.delete(f"{API_URL}/{task['id']}")
                    st.experimental_rerun()

                st.markdown("---")
    else:
        st.error("⚠️ Could not fetch tasks.")
except Exception as e:
    st.error(f"⚠️ Could not fetch tasks: {e}")



