import json
import os
from io import BytesIO
from pathlib import Path
from typing import List

import networkx as nx
import nltk
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from annotated_text import annotated_text, parameters
from docx import Document
from pypdf import PdfReader

from scripts.parsers import ParseJobDesc, ParseResume
from scripts.similarity.get_score import *
from scripts.utils.logger import init_logging_config

# Set page configuration
st.set_page_config(
    page_title="Resume Matcher",
    page_icon="Assets/img/favicon.ico",
    initial_sidebar_state="collapsed",
    layout="wide",
)

init_logging_config()
cwd = find_path("Resume-Matcher")
config_path = os.path.join(cwd, "scripts", "similarity")

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

parameters.SHOW_LABEL_SEPARATOR = False
parameters.BORDER_RADIUS = 3
parameters.PADDING = "0.5 0.25rem"


st.markdown(
    """
    <style>
    .section-heading {
        font-size: 1.2rem;
        font-weight: 800;
        color: #0B666A;
        border-left: 5px solid #0B666A;
        padding: 0.35rem 0.9rem;
        margin: 1.5rem 0 1rem 0;
        background: linear-gradient(90deg, rgba(11, 102, 106, 0.12), rgba(11, 102, 106, 0.02));
        text-transform: uppercase;
        letter-spacing: 0.04rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_section_heading(container, title: str):
    container.markdown(
        f"<div class='section-heading'>{title}</div>",
        unsafe_allow_html=True,
    )


def render_dual_section(title: str, resume_renderer, job_renderer, show_heading: bool = True):
    if show_heading:
        render_section_heading(st, title)
    resume_col, job_col = st.columns(2, gap="large")
    resume_renderer(resume_col)
    job_renderer(job_col)


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    pdf_reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in pdf_reader.pages:
        text = page.extract_text() or ""
        if text:
            pages.append(text)
    return "\n".join(pages)


def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
    return "\n".join(paragraphs)


def parse_uploaded_resume(uploaded_file) -> dict:
    file_bytes = uploaded_file.getvalue()
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".pdf":
        raw_text = extract_text_from_pdf_bytes(file_bytes)
    elif suffix == ".docx":
        raw_text = extract_text_from_docx_bytes(file_bytes)
    else:
        raise ValueError("Unsupported resume file type. Please upload a PDF or DOCX file.")
    if not raw_text.strip():
        raise ValueError("Uploaded resume does not contain extractable text.")
    return ParseResume(raw_text).get_JSON()


def parse_job_description_input(job_description: str) -> dict:
    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")
    return ParseJobDesc(job_description).get_JSON()


def create_star_graph(nodes_and_weights, title, central_label="resume"):
    # Create an empty graph
    G = nx.Graph()

    # Add the central node
    central_node = central_label
    G.add_node(central_node)

    # Add nodes and edges with weights to the graph
    for node, weight in nodes_and_weights:
        G.add_node(node)
        G.add_edge(central_node, node, weight=weight * 100)

    # Get position layout for nodes
    pos = nx.spring_layout(G)

    # Create edge trace
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    # Create node trace
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="Rainbow",
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title="Node Connections",
                xanchor="left",
                titleside="right",
            ),
            line_width=2,
        ),
    )

    # Color node points by number of connections
    node_adjacencies = []
    node_text = []
    for node in G.nodes():
        adjacencies = list(G.adj[node])  # changes here
        node_adjacencies.append(len(adjacencies))
        node_text.append(f"{node}<br># of connections: {len(adjacencies)}")

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    # Create the figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    # Show the figure
    st.plotly_chart(fig)


def create_annotated_text(
    input_string: str, word_list: List[str], annotation: str, color_code: str
):
    # Tokenize the input string
    tokens = nltk.word_tokenize(input_string)

    # Convert the list to a set for quick lookups
    word_set = set(word_list)

    # Initialize an empty list to hold the annotated text
    annotated_text = []

    for token in tokens:
        # Check if the token is in the set
        if token in word_set:
            # If it is, append a tuple with the token, annotation, and color code
            annotated_text.append((token, annotation, color_code))
        else:
            # If it's not, just append the token as a string
            annotated_text.append(token)

    return annotated_text


def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def tokenize_string(input_string):
    tokens = nltk.word_tokenize(input_string)
    return tokens


st.title(":blue[Resume Matcher]")
st.divider()

# Inputs section in two columns (no sidebar navigation)
resume_data = st.session_state.get("resume_data")
job_data = st.session_state.get("job_data")

st.markdown("### Data Inputs")
uploader_cols = st.columns(2, gap="large")

with uploader_cols[0]:
    st.markdown("#### Resume")
    uploaded_resume = st.file_uploader(
        "Upload resume (PDF or DOCX)", type=["pdf", "docx"], key="resume_uploader"
    )
    if uploaded_resume is not None:
        resume_signature = (uploaded_resume.name, uploaded_resume.size)
        if st.session_state.get("resume_source") != resume_signature:
            try:
                st.session_state["resume_data"] = parse_uploaded_resume(uploaded_resume)
                st.session_state["resume_source"] = resume_signature
                st.session_state["resume_filename"] = uploaded_resume.name
            except ValueError as exc:
                st.error(str(exc))
    else:
        st.session_state.pop("resume_source", None)
        st.session_state.pop("resume_data", None)
        st.session_state.pop("resume_filename", None)

    resume_data = st.session_state.get("resume_data")
    if resume_data and st.session_state.get("resume_filename"):
        st.caption(f"Using uploaded resume: {st.session_state['resume_filename']}")

with uploader_cols[1]:
    st.markdown("#### Job Description")
    submit_jd = False
    with st.form("job_description_form"):
        job_description_text = st.text_area(
            "Paste job description text",
            height=220,
            placeholder="Paste job description here",
            key="job_text_input",
        )
        button_cols = st.columns([0.75, 0.25])
        with button_cols[1]:
            submit_jd = st.form_submit_button("Enter")
    if submit_jd:
        if job_description_text.strip():
            try:
                st.session_state["job_data"] = parse_job_description_input(job_description_text)
                st.session_state["job_text_cache"] = job_description_text
            except ValueError as exc:
                st.error(str(exc))
        else:
            st.session_state.pop("job_data", None)
            st.session_state.pop("job_text_cache", None)

    job_data = st.session_state.get("job_data")
    if job_data:
        st.caption("Using the pasted job description for ATS-style analysis.")

resume_data = st.session_state.get("resume_data")
job_data = st.session_state.get("job_data")
show_dual_titles = bool(resume_data) and bool(job_data)

missing_prompts = []
if not resume_data:
    missing_prompts.append("Upload a resume (PDF or DOCX) to unlock resume analytics.")
if not job_data:
    missing_prompts.append("Submit a job description to unlock job analytics.")
if missing_prompts:
    st.info(" ".join(missing_prompts))

def render_resume_parsed(column):
    if resume_data:
        column.caption(
            "ATS-style cleaned content extracted from the uploaded resume for downstream analysis."
        )
        column.write(resume_data["clean_data"])
    else:
        column.empty()

def render_job_parsed(column):
    if job_data:
        column.caption(
            "ATS-style cleaned content derived from the job description for accurate comparison."
        )
        column.write(job_data["clean_data"])
    else:
        column.empty()

render_dual_section(
    "Parsed Text",
    render_resume_parsed,
    render_job_parsed,
    show_heading=show_dual_titles,
)

def render_resume_keywords(column):
    if resume_data:
        column.caption("Keywords automatically highlighted from the resume content.")
        with column:
            annotated_text(
                create_annotated_text(
                    resume_data["clean_data"],
                    resume_data["extracted_keywords"],
                    "RESUME",
                    "#98DFD6",
                )
            )
    else:
        column.empty()

def render_job_keywords(column):
    if job_data:
        column.caption("Keywords automatically highlighted from the job description content.")
        with column:
            annotated_text(
                create_annotated_text(
                    job_data["clean_data"],
                    job_data["extracted_keywords"],
                    "JD",
                    "#F24C3D",
                )
            )
    else:
        column.empty()

render_dual_section(
    "Extracted Keywords",
    render_resume_keywords,
    render_job_keywords,
    show_heading=show_dual_titles,
)

def render_resume_entities(column):
    if resume_data:
        resume_keyterms = resume_data.get("keyterms", [])
        if resume_keyterms:
            column.caption("Network view of key entities discovered in the resume.")
            with column:
                create_star_graph(resume_keyterms, "Entities from Resume", central_label="resume")
        else:
            column.info("No entities extracted from the resume.")
    else:
        column.empty()

def render_job_entities(column):
    if job_data:
        job_keyterms = job_data.get("keyterms", [])
        if job_keyterms:
            column.caption("Network view of key entities discovered in the job description.")
            with column:
                create_star_graph(job_keyterms, "Entities from Job Description", central_label="job")
        else:
            column.info("No entities extracted from the job description.")
    else:
        column.empty()

render_dual_section(
    "Entities",
    render_resume_entities,
    render_job_entities,
    show_heading=show_dual_titles,
)

def render_resume_topics(column):
    if resume_data:
        resume_keyterms = resume_data.get("keyterms", [])
        df_resume = pd.DataFrame(resume_keyterms, columns=["keyword", "value"])
        if not df_resume.empty:
            column.caption("Topic weighting extracted from the resume text.")
            resume_keyword_dict = {keyword: value * 100 for keyword, value in resume_keyterms}
            if resume_keyword_dict:
                fig_resume = go.Figure(
                    data=[
                        go.Table(
                            header=dict(
                                values=["Keyword", "Value"],
                                font=dict(size=12),
                                fill_color="#070A52",
                            ),
                            cells=dict(
                                values=[
                                    list(resume_keyword_dict.keys()),
                                    list(resume_keyword_dict.values()),
                                ],
                                line_color="darkslategray",
                                fill_color="#6DA9E4",
                            ),
                        )
                    ]
                )
                column.plotly_chart(fig_resume, use_container_width=True)
            fig_resume_tree = px.treemap(
                df_resume,
                path=["keyword"],
                values="value",
                color_continuous_scale="Rainbow",
                title="Key Terms/Topics Extracted from the Resume",
            )
            column.plotly_chart(fig_resume_tree, use_container_width=True)
        else:
            column.info("No topics extracted from the resume.")
    else:
        column.empty()

def render_job_topics(column):
    if job_data:
        job_keyterms = job_data.get("keyterms", [])
        df_job = pd.DataFrame(job_keyterms, columns=["keyword", "value"])
        if not df_job.empty:
            column.caption("Topic weighting extracted from the job description text.")
            job_keyword_dict = {keyword: value * 100 for keyword, value in job_keyterms}
            if job_keyword_dict:
                fig_job = go.Figure(
                    data=[
                        go.Table(
                            header=dict(
                                values=["Keyword", "Value"],
                                font=dict(size=12),
                                fill_color="#070A52",
                            ),
                            cells=dict(
                                values=[
                                    list(job_keyword_dict.keys()),
                                    list(job_keyword_dict.values()),
                                ],
                                line_color="darkslategray",
                                fill_color="#6DA9E4",
                            ),
                        )
                    ]
                )
                column.plotly_chart(fig_job, use_container_width=True)
            fig_job_tree = px.treemap(
                df_job,
                path=["keyword"],
                values="value",
                color_continuous_scale="Rainbow",
                title="Key Terms/Topics Extracted from the Job Description",
            )
            column.plotly_chart(fig_job_tree, use_container_width=True)
        else:
            column.info("No topics extracted from the job description.")
    else:
        column.empty()

render_dual_section(
    "Topics",
    render_resume_topics,
    render_job_topics,
    show_heading=show_dual_titles,
)

# Match Insights section (always visible under inputs when data available)
st.markdown("### Match Insights")
if resume_data and job_data:
    render_section_heading(st, "Keyword Overlap")
    st.caption(
        "Highlights shared terminology between the uploaded resume and job description."
    )
    annotated_text(
        create_annotated_text(
            resume_data["clean_data"],
            job_data["extracted_keywords"],
            "JD",
            "#F24C3D",
        )
    )

    render_section_heading(st, "Similarity Score")
    st.caption(
        "Overall semantic alignment score calculated using FastEmbed similarity between resume and job description keywords."
    )
    resume_string = " ".join(resume_data["extracted_keywords"])
    jd_string = " ".join(job_data["extracted_keywords"])
    result = get_score(resume_string, jd_string)
    similarity_score = round(result[0].score * 100, 2)
    score_color = "green"
    if similarity_score < 60:
        score_color = "red"
    elif 60 <= similarity_score < 75:
        score_color = "orange"
    st.markdown(
        f'<span style="color:{score_color};font-size:28px; font-weight:800">{similarity_score}</span>',
        unsafe_allow_html=True,
    )
else:
    st.info(
        "Provide both a resume and a job description to unlock match insights."
    )
