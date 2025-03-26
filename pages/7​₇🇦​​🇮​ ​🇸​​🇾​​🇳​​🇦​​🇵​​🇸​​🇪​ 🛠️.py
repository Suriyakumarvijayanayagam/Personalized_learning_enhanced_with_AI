import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random



# Check if the user is logged in
if 'signed_in' not in st.session_state or not st.session_state.signed_in:
    st.warning("🔒You must be logged in to access this page.")
    st.stop()  # Stop rendering the rest of the page


# Configure the app
st.set_page_config(layout="wide",page_icon="🛠️", page_title="AI Synapse: Neural Learning Environment")

# App title and introduction
st.title("AI Synapse: Neural Learning Environment")
st.markdown("*Where AI adapts to your unique neural pathways*")

# Sidebar for user settings and neural profile
with st.sidebar:
    st.header("Neural Profile")
    
    if 'neural_profile' not in st.session_state:
        st.session_state.neural_profile = {
            'cognitive_strength': random.choice(['Visual-Spatial', 'Logical-Mathematical', 'Linguistic', 'Kinesthetic']),
            'attention_span': random.randint(15, 45),
            'memory_pattern': random.choice(['Associative', 'Semantic', 'Episodic', 'Procedural']),
            'learning_rhythm': [random.random() for _ in range(24)],
            'concept_bridges': random.randint(3, 8)
        }
    
    profile = st.session_state.neural_profile
    
    st.subheader("Your Cognitive Signature")
    st.info(f"Primary Neural Strength: {profile['cognitive_strength']}")
    st.info(f"Optimal Attention Window: {profile['attention_span']} minutes")
    st.info(f"Memory Encoding Pattern: {profile['memory_pattern']}")
    st.info(f"Concept Bridge Capacity: {profile['concept_bridges']}")
    
    # Neural rhythm visualization
    st.subheader("Your Learning Rhythm")
    fig = px.line(
        x=list(range(24)), 
        y=profile['learning_rhythm'],
        labels={'x': 'Hour of Day', 'y': 'Cognitive Receptivity'}
    )
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    # if st.button("Recalibrate Neural Profile"):
    #     st.session_state.neural_profile = None
    #     st.rerun()

# Main app content
tab1, tab2, tab3 = st.tabs(["Neural Learning Path", "Synapse Strengthening", "Cognitive Analytics"])

with tab1:
    st.header("Your Dynamic Neural Learning Path")
    
    # Neural network visualization of learning topics
    st.subheader("Knowledge Neural Network")
    
    # Generate mock neural network data
    def generate_knowledge_network():
        nodes = [
            "Core Concept", "Application", "Theory", "Practice",
            "Fundamentals", "Advanced", "Mastery", "Integration"
        ]
        
        edges = []
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                if random.random() > 0.5:
                    edges.append((i, j, random.random()))
        
        node_strengths = [0.2 + 0.8 * random.random() for _ in nodes]
        
        return nodes, edges, node_strengths
    
    nodes, edges, node_strengths = generate_knowledge_network()
    
    # Create neural network visualization
    node_x = []
    node_y = []
    for i in range(len(nodes)):
        angle = 2 * np.pi * i / len(nodes)
        node_x.append(np.cos(angle))
        node_y.append(np.sin(angle))
    
    edge_x = []
    edge_y = []
    for edge in edges:
        edge_x += [node_x[edge[0]], node_x[edge[1]], None]
        edge_y += [node_y[edge[0]], node_y[edge[1]], None]
    
    # Create edges trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create nodes trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=nodes,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='Viridis',
            size=30,
            color=node_strengths,
            line_width=2))
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0,l=0,r=0,t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Adaptive learning recommendations
    st.subheader("Today's Neural-Optimized Learning Activities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Morning Session (Peak Receptivity)")
        st.info(
            f"**Concept Expansion**: Build new neural pathways\n\n"
            f"Based on your {profile['cognitive_strength']} strength and "
            f"{profile['memory_pattern']} memory pattern, we recommend:\n\n"
            f"- Interactive simulation: Quantum Computation Basics\n"
            f"- Duration: {profile['attention_span']} minutes\n"
            f"- Neural consolidation: 3 new concept bridges"
        )
    
    with col2:
        st.markdown("##### Afternoon Session (Retrieval Practice)")
        st.info(
            f"**Neural Reinforcement**: Strengthen existing pathways\n\n"
            f"Optimized for your cognitive rhythm peak at 3 PM:\n\n"
            f"- Spaced repetition sequence: Algorithmic Thinking\n"
            f"- Duration: {profile['attention_span']-5} minutes\n"
            f"- Neural activation: {profile['concept_bridges']} concept bridges"
        )

with tab2:
    st.header("Synapse Strengthening Lab")
    
    # Neurotransmitter simulation
    st.subheader("Neural Pathway Simulator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Generate mock neuron activation data
        times = np.linspace(0, 5, 1000)
        activation = np.zeros_like(times)
        for i in range(5):
            peak_time = random.uniform(0.5, 4.5)
            activation += 0.8 * np.exp(-((times - peak_time) / 0.2) ** 2)
        
        # Create the neuron activation plot
        fig = px.line(x=times, y=activation,
                     labels={'x': 'Time (s)', 'y': 'Neural Activation'},
                     title='Live Neuron Activation During Learning')
        fig.add_shape(
            type="line", line=dict(dash='dot', width=2, color='red'),
            y0=0.7, y1=0.7, x0=0, x1=5
        )
        fig.add_annotation(
            x=5, y=0.7,
            text="Activation Threshold",
            showarrow=False,
            yshift=10
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Neural Efficiency Metrics")
        
        # Mock neural metrics
        metrics = {
            "Synaptic Efficiency": random.uniform(0.65, 0.95),
            "Concept Retention": random.uniform(0.70, 0.90),
            "Neural Plasticity": random.uniform(0.50, 0.85),
            "Memory Consolidation": random.uniform(0.60, 0.92)
        }
        
        for metric, value in metrics.items():
            st.metric(metric, f"{value:.0%}")
    
    st.subheader("Personalized Neural Exercises")
    
    exercise_types = [
        "Conceptual Association Mapping",
        "Cross-Modal Pattern Recognition",
        "Temporal Lobe Activation Sequence",
        "Prefrontal Cortex Strengthening"
    ]
    
    selected_exercise = st.selectbox("Select Neural Exercise Type", exercise_types)
    
    st.markdown(f"### {selected_exercise}")
    st.markdown(
        f"This exercise is tailored to your {profile['cognitive_strength']} neural strength "
        f"and optimized for your {profile['memory_pattern']} memory encoding pattern."
    )
    
    # Mock exercise interface
    st.info(
        "**Exercise Protocol**:\n\n"
        "1. Establish baseline neural activation (30 seconds)\n"
        "2. Engage in conceptual linking of new material (3 minutes)\n"
        "3. Perform active recall with increasing intervals (5 minutes)\n"
        "4. Complete cross-domain application task (7 minutes)"
    )
    
    if st.button("Start Neural Exercise"):
        st.success("Neural exercise sequence initiated. Follow the prompts as they appear.")
        
        # Mock progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(101):
            # Update progress bar
            progress_bar.progress(i)
            
            if i < 20:
                status_text.text("Calibrating to your neural baseline...")
            elif i < 50:
                status_text.text("Establishing new synaptic connections...")
            elif i < 80:
                status_text.text("Strengthening neural pathways...")
            else:
                status_text.text("Consolidating memory patterns...")
            
            # Simulate some work
            import time
            time.sleep(0.05)
        
        status_text.text("Exercise completed successfully!")

with tab3:
    st.header("Cognitive Analytics Dashboard")
    
    # Generate mock learning data
    def generate_learning_data(days=30):
        dates = [datetime.now() - timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        metrics = {
            "Cognitive Load": [random.uniform(20, 80) for _ in range(days)],
            "Memory Retention": [random.uniform(50, 95) for _ in range(days)],
            "Neural Efficiency": [random.uniform(40, 90) for _ in range(days)],
            "Concept Bridging": [random.uniform(30, 85) for _ in range(days)]
        }
        
        df = pd.DataFrame({
            'Date': dates,
            **metrics
        })
        
        return df
    
    learning_data = generate_learning_data()
    
    # Time series visualization
    st.subheader("Neural Learning Progression")
    
    metrics = st.multiselect(
        "Select Neural Metrics to Display",
        options=["Cognitive Load", "Memory Retention", "Neural Efficiency", "Concept Bridging"],
        default=["Memory Retention", "Neural Efficiency"]
    )
    
    if metrics:
        fig = px.line(
            learning_data, x='Date', y=metrics,
            labels={'value': 'Performance', 'variable': 'Metric'},
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    
    # Brain region activity analysis
    st.subheader("Brain Region Activity Analysis")
    
    # Mock brain region data
    brain_regions = {
        "Prefrontal Cortex": random.uniform(60, 90),
        "Temporal Lobe": random.uniform(50, 85),
        "Parietal Lobe": random.uniform(55, 88),
        "Occipital Lobe": random.uniform(45, 80),
        "Hippocampus": random.uniform(65, 95),
        "Amygdala": random.uniform(40, 75)
    }
    
    fig = px.bar(
        x=list(brain_regions.keys()),
        y=list(brain_regions.values()),
        labels={'x': 'Brain Region', 'y': 'Activation Level (%)'},
        color=list(brain_regions.values()),
        color_continuous_scale='Viridis'
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Neural insights
    st.subheader("AI-Generated Neural Insights")
    
    insights = [
        f"Your {profile['cognitive_strength']} strength shows 23% higher activation during problem-solving tasks",
        f"Your {profile['memory_pattern']} memory pattern is optimally engaged during morning learning sessions",
        f"Concept bridging capacity has increased by 17% over the past two weeks",
        f"Neural efficiency peaks at {profile['learning_rhythm'].index(max(profile['learning_rhythm']))}:00, suggesting optimal learning time"
    ]
    
    for insight in insights:
        st.info(insight)
    
    # Recommendations based on neural profile
    st.subheader("Personalized Neural Optimization Strategies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Learning Environment Optimization")
        st.markdown(
            f"Based on your neural profile, we recommend:\n\n"
            f"- Learning environment: {random.choice(['Minimal distractions', 'Background white noise', 'Nature sounds'])}\n"
            f"- Lighting: {random.choice(['Natural sunlight', 'Cool white light', 'Warm light'])}\n"
            f"- Session structure: {random.choice(['Pomodoro with 25-5 splits', 'Deep work blocks of 90 minutes', 'Alternating focus-diffuse modes'])}"
        )
    
    with col2:
        st.markdown("##### Cognitive Enhancement")
        st.markdown(
            f"To optimize neural pathway formation:\n\n"
            f"- Practice {random.choice(['dual n-back exercises', 'cross-hemispheric activities', 'working memory training'])}\n"
            f"- Engage in {random.choice(['mindfulness meditation', 'visualization techniques', 'binaural beat sessions'])}\n"
            f"- Utilize {random.choice(['spaced repetition software', 'concept mapping tools', 'neural feedback systems'])}"
        )