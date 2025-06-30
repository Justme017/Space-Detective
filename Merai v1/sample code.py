import streamlit as st
import streamlit.components.v1 as components

st.title("Space Detective - Aladin Lite Integration")

# Embed Aladin Lite via HTML iframe approach
aladin_html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <script type="text/javascript" src="https://aladin.u-strasbg.fr/AladinLite/api/v3/latest/aladin.min.js" ></script>
    <link rel="stylesheet" href="https://aladin.u-strasbg.fr/AladinLite/api/v3/latest/aladin.min.css" />
  </head>
  <body>
    <div id="aladin-lite-div" style="width:800px;height:600px;"></div>
    <script type="text/javascript">
      var aladin = A.aladin('#aladin-lite-div', {survey: "P/DSS2/color", fov:0.5, target: "M1"});
    </script>
  </body>
</html>
"""

# Display Aladin Lite
components.html(aladin_html, height=600, width=800)
