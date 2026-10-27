"""
Bookings Directory Page for TravelResolve.
Reservation catalog search and rate conditions inspection.
Developed by Keyura Motegaonkar.
"""

import streamlit as st
import pandas as pd
from app.database import SessionLocal, Booking
from app.agents.tools import evaluate_cancellation_policy


def render_booking_explorer():
    with SessionLocal() as db:
        bookings = db.query(Booking).order_by(Booking.check_in_date.asc()).all()

    if not bookings:
        st.info("No booking records found in system.")
        return

    # Clean Search & Filters in Native Container
    with st.container(border=True):
        st.markdown("**Search & Filter Reservations**")
        col_search, col_status, col_fare, col_tier = st.columns([2.5, 1.2, 1.5, 1.2])
        with col_search:
            search_query = st.text_input(
                "Search",
                placeholder="Search reference, guest name, city, hotel...",
                label_visibility="collapsed"
            ).strip().lower()
        with col_status:
            status_filter = st.selectbox(
                "Status",
                ["All Statuses", "Confirmed", "Cancelled"],
                label_visibility="collapsed"
            )
        with col_fare:
            fare_filter = st.selectbox(
                "Fare Rules",
                ["All Fares", "Flexible", "Non-Refundable"],
                label_visibility="collapsed"
            )
        with col_tier:
            tier_filter = st.selectbox(
                "Tier",
                ["All Tiers", "Standard", "Silver", "Gold", "Platinum"],
                label_visibility="collapsed"
            )

    filtered = []
    for b in bookings:
        b_dict = b.to_dict()
        if search_query:
            match = (
                search_query in b_dict["id"].lower()
                or search_query in b_dict["customer_name"].lower()
                or search_query in b_dict["hotel_city"].lower()
                or search_query in b_dict["hotel_name"].lower()
            )
            if not match:
                continue

        if status_filter != "All Statuses" and b_dict["booking_status"].lower() != status_filter.lower():
            continue

        if fare_filter == "Flexible" and not b_dict["cancellation_eligible"]:
            continue
        if fare_filter == "Non-Refundable" and b_dict["cancellation_eligible"]:
            continue

        if tier_filter != "All Tiers" and b_dict["customer_tier"].lower() != tier_filter.lower():
            continue

        filtered.append(b_dict)

    st.markdown(f"**Records Found:** {len(filtered)}")

    if not filtered:
        st.info("No bookings match your selected filter criteria.")
        return

    # Summary Table in Native Bordered Container
    with st.container(border=True):
        st.markdown("#### Active Reservations")
        table_rows = [
            {
                "Booking Reference": b["id"],
                "Guest": f"{b['customer_name']} ({b['customer_tier']})",
                "Property": b["hotel_name"],
                "Destination": b["hotel_city"],
                "Check-In": b["check_in_date"],
                "Check-Out": b["check_out_date"],
                "Status": b["booking_status"].title(),
                "Payment": b["payment_status"].title(),
                "Total": f"${b['total_amount']:.2f} {b['currency']}",
                "Fare Rules": "Flexible" if b["cancellation_eligible"] else "Non-Refundable"
            }
            for b in filtered
        ]
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Master-Detail Inspection Card
    with st.container(border=True):
        st.markdown("#### Reservation Details & Cancellation Calculator")
        st.caption("Select a booking reference to inspect rate rules and refund calculations.")

        selected_bid = st.selectbox(
            "Select Reservation Reference",
            [b["id"] for b in filtered],
            label_visibility="collapsed"
        )

        target = next((b for b in filtered if b["id"] == selected_bid), None)
        if target:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Booking Reference:** `{target['id']}`")
                st.markdown(
                    f"**Registered Guest:** {target['customer_name']} (`{target['customer_email']}`)  \n"
                    f"**Loyalty Tier:** `{target['customer_tier']}`  \n"
                    f"**Room Type:** {target['room_type']}  \n"
                    f"**Special Requests:** {target['special_requests']}  \n"
                    f"**Payment Status:** {target['payment_status'].title()}"
                )

            with c2:
                st.markdown("**Real-Time Cancellation Terms**")
                calc = evaluate_cancellation_policy(target)
                st.markdown(
                    f"**Cancellation Permitted:** {'Yes' if calc['eligible'] else 'No'}  \n"
                    f"**Calculated Refund:** ${calc.get('refund_amount', 0.0):.2f} USD  \n"
                    f"**Cancellation Fee:** ${calc.get('cancellation_fee', 0.0):.2f} USD  \n"
                    f"**Policy Clause:** {calc.get('reason')}"
                )
