import streamlit as st
import pandas as pd
import random
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Setup
st.set_page_config(page_title="Advanced A/B Testing", layout="centered")
st.title("🧪 Advanced A/B Testing Framework")

st.markdown("### 🔧 Step 1: Configure Your Test")

# User input: Number of users
num_users = st.number_input("Number of users to simulate:", min_value=10, max_value=5000, value=100, step=10)

# User input: Group names
group_input = st.text_input("Enter group names (comma-separated):", value="A,B")

# Group setup and sliders
if group_input.strip():
    group_list = [g.strip() for g in group_input.split(",") if g.strip()]
    st.markdown("### 🎯 Step 2: Set Conversion Rates for Each Group")

    conversion_rates = {}
    for g in group_list:
        rate = st.slider(f"Conversion rate for group '{g}':", min_value=0.0, max_value=1.0, value=0.3, step=0.01)
        conversion_rates[g] = rate
else:
    group_list = []
    conversion_rates = {}

# Button to simulate
simulate_btn = st.button("🎲 Simulate Data")


# ----------- FUNCTION: Simulate Data ------------
def simulate_data(n_users, groups, conversion_rates):
    data = []
    group_list = [g.strip() for g in groups.split(",") if g.strip()]

    for user_id in range(1, n_users + 1):
        group = random.choice(group_list)
        clicked = 1 if random.random() < conversion_rates[group] else 0
        data.append({"user_id": user_id, "group": group, "clicked": clicked})

    df = pd.DataFrame(data)
    return df


# ----------- STREAMLIT LOGIC ---------------------
if simulate_btn:
    if len(group_input.strip()) == 0 or not conversion_rates:
        st.error("Please enter valid group names and conversion rates.")
    else:
        df = simulate_data(num_users, group_input, conversion_rates)
        st.success("✅ Data simulated successfully!")

        st.write("### 🔍 User-defined Conversion Rates:")
        st.write(conversion_rates)

        st.write("### 🧾 Simulated Data Preview:")
        st.dataframe(df.head())

        st.write("### 📊 Conversion Rates by Group:")
        conv = df.groupby('group')['clicked'].mean().reset_index()
        conv.columns = ['Group', 'Conversion Rate']
        st.dataframe(conv)

        st.write("### 📈 Conversion Plot:")
        fig = plt.figure()
        sns.barplot(x='group', y='clicked', data=df, ci=None)
        plt.title("Conversion Rate by Group")
        plt.ylabel("Conversion Rate")
        st.pyplot(fig)

        # Statistical test
        groups = df['group'].unique()
        if len(groups) == 2:
            a = df[df['group'] == groups[0]]['clicked']
            b = df[df['group'] == groups[1]]['clicked']
            t_stat, p_val = stats.ttest_ind(a, b)
            st.write("### 🧪 T-Test Result")
            st.write(f"T-Statistic: `{t_stat:.4f}`")
            st.write(f"P-Value: `{p_val:.4f}`")
            is_significant = p_val < 0.05
        else:
            samples = [df[df['group'] == g]['clicked'] for g in groups]
            f_stat, p_val = stats.f_oneway(*samples)
            st.write("### 🧪 ANOVA Result")
            st.write(f"F-Statistic: `{f_stat:.4f}`")
            st.write(f"P-Value: `{p_val:.4f}`")
            is_significant = p_val < 0.05

        if is_significant:
            st.success("✅ Statistically Significant Difference Detected!")
        else:
            st.warning("❌ No Statistically Significant Difference.")

        # ---------------- Log the Result ----------------
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": now,
            "num_users": num_users,
            "groups": group_input,
        }

        for g in groups:
            conv_rate = df[df['group'] == g]['clicked'].mean()
            log_entry[f"{g}_conversion"] = round(conv_rate, 4)

        log_entry["test_type"] = "t-test" if len(groups) == 2 else "ANOVA"
        log_entry["p_value"] = round(p_val, 4)
        log_entry["result"] = "Significant" if is_significant else "Not Significant"

        log_file = "experiment_log.csv"

        if os.path.exists(log_file):
            log_df = pd.read_csv(log_file)
            log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
        else:
            log_df = pd.DataFrame([log_entry])

        log_df.to_csv(log_file, index=False)
        st.success("📄 Experiment result saved to `experiment_log.csv`.")
# ---------------- View All Past Experiments ----------------
st.markdown("### 🗂️ View All Experiments")

if os.path.exists("experiment_log.csv"):
    st.subheader("📊 Experiment Logs")
    log_df = pd.read_csv("experiment_log.csv")
    st.dataframe(log_df)
else:
    st.info("No experiments have been logged yet.")

