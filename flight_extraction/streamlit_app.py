import streamlit as st
import tempfile
import json
from main import process_files

st.set_page_config(
    page_title="Travel Document Extractor",
    layout="centered"
)

st.title("🧳 Travel Document Extraction")

st.write(
    """
Upload PDF files (flight tickets, boarding passes, train tickets, hotel bookings, etc.).

The system will automatically:
- **Classify** document types
- **Extract** relevant information
- **Validate** using AI reasoning
- **Group** related documents

Supported: ✈️ Flights | 🚂 Trains | 🏨 Hotels
"""
)

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"{len(uploaded_files)} file(s) uploaded")

if st.button("Process Documents", disabled=not uploaded_files):
    try:
        with st.spinner("Processing documents..."):
            temp_paths = []

            for uploaded in uploaded_files:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as tmp:
                    tmp.write(uploaded.read())
                    temp_paths.append(tmp.name)

            results = process_files(temp_paths)

        st.success(f"✅ Extraction completed — {len(results)} booking(s) detected")

        # 🔁 Show one section per booking
        for idx, booking in enumerate(results, start=1):
            booking_id = booking.get("bookingIdentity", {})
            booking_type = booking_id.get("type", "UNKNOWN")
            
            # Different icons for different types
            icon = {"FLIGHT": "✈️", "TRAIN": "🚂", "HOTEL": "🏨"}.get(booking_type, "📄")
            
            st.subheader(f"{icon} {booking_type.title()} Booking {idx}")

            # Display identity info based on type
            if booking_type == "FLIGHT":
                st.markdown(
                    f"""
**PNR:** `{booking_id.get("pnr", "N/A")}`  
**Flight Number:** `{booking_id.get("flightNumber", "N/A")}`
"""
                )
            elif booking_type == "TRAIN":
                st.markdown(
                    f"""
**PNR:** `{booking_id.get("pnr", "N/A")}`  
**Train Number:** `{booking_id.get("trainNumber", "N/A")}`
"""
                )
            elif booking_type == "HOTEL":
                st.markdown(
                    f"""
**Booking Reference:** `{booking_id.get("bookingReference", "N/A")}`  
**Hotel:** `{booking_id.get("hotelName", "N/A")}`
"""
                )
            
            # Show reasoning insights
            insights = booking.get("reasoningInsights", {})
            confidence = insights.get("averageConfidence", 0)
            
            if confidence >= 80:
                st.success(f"🎯 Confidence: {confidence}% - High quality extraction")
            elif confidence >= 60:
                st.info(f"⚠️ Confidence: {confidence}% - Good extraction")
            else:
                st.warning(f"⚠️ Confidence: {confidence}% - Review recommended")
            
            if insights.get("issues"):
                with st.expander("⚠️ Issues Found"):
                    for issue in insights["issues"]:
                        st.write(f"- {issue}")
            
            if insights.get("suggestions"):
                with st.expander("💡 Suggestions"):
                    for suggestion in insights["suggestions"]:
                        st.write(f"- {suggestion}")

            st.json(booking)

            # Download per booking
            st.download_button(
                label=f"Download {booking_type.title()} {idx} JSON",
                data=json.dumps(booking, indent=4).encode("utf-8"),
                file_name=f"{booking_type.lower()}_{idx}.json",
                mime="application/json",
                key=f"download_{idx}"
            )

        # Optional: download all bookings together
        st.divider()
        st.subheader("⬇️ Download All Bookings")

        st.download_button(
            label="Download All Bookings JSON",
            data=json.dumps(results, indent=4).encode("utf-8"),
            file_name="all_bookings.json",
            mime="application/json"
        )

    except Exception as e:
        st.error("❌ Processing failed")
        st.exception(e)
