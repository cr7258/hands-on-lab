# doc: https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/
from langchain_text_splitters import MarkdownHeaderTextSplitter

with open("./16-employee-handbook.md") as f:
    employee_handbook = f.read()

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=False)
md_header_splits = markdown_splitter.split_text(employee_handbook)

for doc in md_header_splits:
    print("-----------------------------------------------")
    print(doc)
# -----------------------------------------------
# page_content='**CR7 Technology Co., Ltd. Employee Handbook**
# **Version:** v1.0
# **Release Date:** April 2025
# **Applicable to:** All Employees
# ---'
# -----------------------------------------------
# page_content='## 1. Company Introduction
# Welcome to **CR7 Technology Co., Ltd.**!
# We are a cutting-edge technology company engaged in the research, development, and application of innovative digital solutions. CR7 Technology specializes in areas such as artificial intelligence, big data analytics, cloud-native infrastructure, and digital transformation for enterprises. We are committed to solving complex problems for global clients with smart and reliable solutions, enabling their industries to thrive in a digital world.
# At CR7, we champion the mission of "unlocking the power of technology and empowering future industries." Our products and solutions are widely adopted in sectors such as finance, healthcare, e-commerce, manufacturing, education, and logistics. Through continuous innovation and strong engineering execution, we build scalable and sustainable systems that bring tangible value.
# We cultivate a corporate culture that values talent, creativity, and collaboration. With a flat management structure and an open, inclusive working environment, CR7 provides every employee the opportunity to grow, lead, and make an impact. Here, your success is our success.
# ---' metadata={'Header 2': '1. Company Introduction'}
# -----------------------------------------------
# page_content='## 2. Corporate Culture
# - **Mission:** Unlocking the power of technology, empowering future industries
# - **Vision:** To be a globally respected provider of digital innovation and enterprise transformation
# - **Core Values:** Integrity, Focus, Collaboration, Innovation, Win-Win
# - **Guiding Behaviors:**
# - Respect the individuality and dignity of every employee
# - Deliver exceptional value to clients with professionalism
# - Embrace change and cultivate a mindset of continuous improvement
# - Promote open communication and teamwork
# Culture is the cornerstone of CR7’s long-term success. We are committed to cultivating a vibrant and value-driven environment where every individual is empowered.
# ---' metadata={'Header 2': '2. Corporate Culture'}
