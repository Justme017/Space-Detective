import streamlit as st
from streamlit_javascript import st_javascript

st.title("Space Detective - Live User Location")

# Embed the deployed HTML page
st.markdown("""
<iframe src="https://geolocation-page.vercel.app/" width="0" height="0"></iframe>
""", unsafe_allow_html=True)

# Listen for the postMessage from iframe
location = st_javascript("""
async () => {
  return await new Promise((resolve) => {
    window.addEventListener("message", (event) => {
      resolve(event.data);
    }, {once: true});
  });
}
""")

if location:
    if "error" in location:
        st.error(f"Error: {location['error']}")
    else:
        st.success(f"Your live location is: ({location['latitude']}, {location['longitude']})")
else:
    st.write("Fetching location...")
