#!/usr/bin/env python3.14

import os
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest
)


# --- CONFIGURATION ---
PROPERTIES = [
    {"id": "325243030", "name": "ASF"},
    {"id": "325253028", "name": "VCF"}
]

CREDENTIALS_PATH = "credentials.json"
client = BetaAnalyticsDataClient()

# Build a JSON-serializable snapshot of the metrics for all properties
report_payload = {
    "properties": []
}

# Process each property
for prop in PROPERTIES:
    prop_id = prop["id"]
    prop_name = prop["name"]

    print(f"\n🏷️ Processing Property: {prop_name} ({prop_id})")

    # L3M Report Request
    request = RunReportRequest(
        property=f"properties/{prop_id}",
        date_ranges=[
            DateRange(start_date="2025-01-01",end_date="2025-01-31",name="Jan25"),
            DateRange(start_date="2025-02-01",end_date="2025-02-28",name="Feb25"),
            DateRange(start_date="2025-03-01",end_date="2025-03-31",name="Mar25")
        ],
        metrics=[
            Metric(name="newUsers"),
            Metric(name="totalUsers")
        ]
    )

    response = client.run_report(request)

    total_new_users = 0
    l3m_ranges = []

    for row in response.rows:
        date_range_name = row.dimension_values[0].value
        new_users = int(row.metric_values[0].value) 
        total_users = int(row.metric_values[1].value)
        percent_new = round(new_users / total_users * 100, 2) if total_users else 0
        total_new_users += new_users

        l3m_ranges.append({
            "name": date_range_name,
            "new_users": new_users,
            "total_users": total_users,
            "percent_new": percent_new,
        })

    # FY26 Q1 Report Request
    requesttwo = RunReportRequest(
        property=f"properties/{prop_id}",
        date_ranges=[
            DateRange(start_date="2025-08-03",end_date="2025-11-01",name="FY26-Q1"),
        ],
        metrics=[
            Metric(name="Sessions"),
            Metric(name="totalUsers")
        ]
    )

    responsetwo = client.run_report(requesttwo)

    total_sessions = 0
    unique_sessions = 0

    for row in responsetwo.rows:
        total_sessions = int(row.metric_values[0].value)
        unique_sessions = int(row.metric_values[1].value)

    # Add property data to payload
    report_payload["properties"].append({
        "id": prop_id,
        "name": prop_name,
        "l3m": {
            "ranges": l3m_ranges,
            "total_new_users": total_new_users,
        },
        "fy26_q1": {
            "sessions": total_sessions,
            "total_users": unique_sessions,
        },
    })

with open("data/mkt-funnel-kpis.json", "w") as f:
    json.dump(report_payload, f, indent=4)

